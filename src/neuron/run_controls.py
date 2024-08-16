"""Defines main for managing NEURON simulations.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""

import json
import os
import sys
import time
import warnings

import numpy as np
from pyfibers import BoundsSearchMode, Fiber, FiberModel, ScaledStim, TerminationMode, ThresholdCondition, build_fiber
from saving import initialize_saving, save_activation, save_matrix, save_runtime, save_sfap, save_thresh, save_variables


def handle_termination(protocol_configs: dict) -> (int, float):
    """Handle termination mode and tolerance.

    :param protocol_configs: dictionary containing protocol configs
    :return: returns termination mode and tolerance required for NEURON simulation
    """
    if protocol_configs['termination_criteria']['mode'] == 'PERCENT_DIFFERENCE':
        termination_mode = TerminationMode.PERCENT_DIFFERENCE
        termination_tolerance = protocol_configs['termination_criteria']['percent']
    elif protocol_configs['termination_criteria']['mode'] == 'ABSOLUTE_DIFFERENCE':
        termination_mode = TerminationMode.ABSOLUTE_DIFFERENCE
        termination_tolerance = protocol_configs['termination_criteria']['tolerance']
    else:
        return None
    return termination_mode, termination_tolerance


def handle_bounds_search(bounds_search_configs: dict) -> (str, float, int):
    """Handle bounds search configs for simulation.

    :param bounds_search_configs: dictionary containing information about bounds search for simulation
    :return: returns the values required for bounds searching during NEURON simulation
    """
    bounds_search_mode = getattr(BoundsSearchMode, bounds_search_configs['mode'])
    bounds_search_step = bounds_search_configs['step']
    max_iterations = bounds_search_configs.get("max_steps", 100)
    return bounds_search_mode, bounds_search_step, max_iterations


def main(
    inner_ind: int,
    fiber_ind: int,
    stimamp_top: float,
    stimamp_bottom: float,
    potentials_path: str,
    waveform_path: str,
    sim_path: str,
    n_sim: int,
):
    """Control flow of a single n_sim NEURON simulation.

    :param inner_ind: inner index
    :param fiber_ind: fiber index
    :param stimamp_top: top stimamp to start bounds search
    :param stimamp_bottom: bottom stimamp to start bounds search
    :param potentials_path: path to potentials file
    :param waveform_path: path to waveform file
    :param sim_path: path to n_sim directory
    :param n_sim: n_sim number
    :raises NotImplementedError: for deprecated features
    """
    start_time = time.time()  # Starting time of simulation
    stimamp_top, stimamp_bottom = float(stimamp_top), float(stimamp_bottom)

    # Read in <sim_index>.json file as dictionary
    with open(f'{sim_path}/{n_sim}.json') as file:
        sim_configs = json.load(file)

    # Read in <model_index>.json file to get temperature
    with open(f'{sim_path}/model.json') as file:
        model_configs = json.load(file)
        temperature = model_configs['temperature']

    # Read in waveform array, time step, and stop time
    with open(waveform_path) as waveform_file:
        dt = float(waveform_file.readline().strip())  # time step
        tstop = int(waveform_file.readline().strip())  # stop time
        file_lines = waveform_file.read().splitlines()
        waveform = np.array([float(i) for i in file_lines])

    # Read in extracellular potentials
    with open(potentials_path) as potentials_file:
        axontotal = int(potentials_file.readline())
        file_lines = potentials_file.read().splitlines()
        potentials = np.array([float(i) for i in file_lines]) * 1000  # Need to convert to V -> mV

    # create fiber object
    model = getattr(FiberModel, sim_configs['fibers']['mode'])
    diameter = sim_configs['fibers']['z_parameters']['diameter']
    fiber = build_fiber(diameter=diameter, fiber_model=model, temperature=temperature, n_sections=axontotal)
    fiber.potentials = potentials

    # attach intracellular stimulation
    istim_configs = sim_configs.get('intrinsic_activity', {})
    if istim_configs:
        fiber.add_intrinsic_activity(**istim_configs)  # Add to docs to look at pyfiber docs for this

    if 'intracellular_stim' in istim_configs:
        raise NotImplementedError('Intracellular stimulation is deprecated, use intrinsic_activity instead')

    # initialize saving parameters
    saving_params = initialize_saving(
        sim_configs.get('saving', {}), fiber, fiber_ind, inner_ind, sim_path, dt, sfap='active_recs' in sim_configs
    )
    # TODO add deprecation warning for ap_end_times

    # determine protocol
    protocol_configs = sim_configs['protocol']
    t_init_ss, dt_init_ss = protocol_configs['initSS'], protocol_configs['dt_initSS']
    ap_detect_location = protocol_configs['threshold']['ap_detect_location']

    # create stimulation object
    stimulation = ScaledStim(waveform=waveform, dt=dt, tstop=tstop, t_init_ss=t_init_ss, dt_init_ss=dt_init_ss)

    if protocol_configs['mode'] != 'FINITE_AMPLITUDES':  # threshold search
        find_threshold_kws = protocol_configs.get('find_threshold_kws', {})
        if 'fail_on_end_excitation' not in find_threshold_kws:
            warnings.warn(
                'fail_on_end_excitation not specified in find_threshold_kws, defaulting to False (warning upon end excitation)'
            )
            find_threshold_kws['fail_on_end_excitation'] = False
        amp = threshold_protocol(
            fiber,
            protocol_configs,
            sim_configs,
            stimulation,
            stimamp_top,
            stimamp_bottom,
            ap_detect_location,
            find_threshold_kws,
        )
        if 'active_recs' in sim_configs:  # TODO should this be done for threshold protocol?
            calculate_save_sfap(sim_configs, fiber, saving_params, potentials_path, inner_ind, fiber_ind, 0, axontotal)
        save_variables(saving_params, fiber, stimulation)  # Save user-specified variables
        save_runtime(saving_params, time.time() - start_time)  # Save runtime of simulation
        save_thresh(saving_params, amp)  # Save threshold value to file

    else:  # finite amplitudes protocol
        time_total = 0
        amps = protocol_configs['amplitudes']
        run_sim_kws = protocol_configs.get('run_sim_kws', {})
        if 'fail_on_end_excitation' not in run_sim_kws:
            warnings.warn(
                'fail_on_end_excitation not specified in run_sim_kws, defaulting to False (warning upon end excitation)'
            )
            run_sim_kws['fail_on_end_excitation'] = False
            # TODO note that find_threshold_kws is ignored here, and run_sim_kws is ignored above

        for amp_ind, amp in enumerate(amps):
            print(f'Running amp {amp_ind} of {len(amps)}: {amp} mA')

            n_aps, _ = stimulation.run_sim(
                stimamp=amp, fiber=fiber, ap_detect_location=ap_detect_location, **run_sim_kws
            )
            if 'active_recs' in sim_configs:
                calculate_save_sfap(
                    sim_configs, fiber, saving_params, potentials_path, inner_ind, fiber_ind, amp_ind, axontotal
                )
            save_variables(saving_params, fiber, stimulation, amp_ind)  # Save user-specified variables

            time_individual = time.time() - start_time - time_total
            save_runtime(saving_params, time_individual, amp_ind)  # Save runtime of inidividual run

            save_activation(saving_params, int(n_aps), amp_ind)  # Save number of APs triggered

            time_total += time_individual

    print('Total runtime:', time.time() - start_time)


def calculate_save_sfap(  # TODO: does it even make sense to calc sfap with a threshold search?
    sim_configs: dict,
    fiber: Fiber,
    saving_params: dict,
    potentials_path: str,
    inner_ind: int,
    fiber_ind: int,
    amp_ind: int,
    axontotal: int,
):
    """Calculate and save single fiber action potential (sfap) and membrane currents if applicable.

    :param sim_configs: dictionary containing simulation configs from <sim_index>.json
    :param fiber: fiber object
    :param saving_params: dictionary containing saving parameters
    :param potentials_path: path to potentials file
    :param inner_ind: inner index
    :param fiber_ind: fiber index
    :param amp_ind: amplitude index
    :param axontotal: total number of axons in fiber
    """
    # If recording cuff is present, record sfap
    if 'active_recs' in sim_configs:
        # TODO move this param to saving init
        downsample = sim_configs.get('saving', {}).get('cap_recording', {}).get('downsample', 1)  # TODO update docs
        # TODO move this param to saving init
        save_adjusted_im = (
            sim_configs.get('saving', {}).get('cap_recording', {}).get('save_adjusted_im', False)
        )  # TODO update docs

        # generate and save sfap
        rec_potentials_path = os.path.join(
            os.path.dirname(potentials_path), f'rec_inner{inner_ind}_fiber{fiber_ind}.dat'
        )
        with open(rec_potentials_path) as rec_potentials_file:
            axontotal_rec = int(rec_potentials_file.readline())
            assert axontotal_rec == axontotal, 'Number of axons in rec_potentials file does not match potentials file'
            rec_potentials = 1000 * np.array(
                [float(i) for i in rec_potentials_file.read().splitlines()]
            )  # Need to convert to V -> mV

        # generate and save single fiber action potential, and I_membrane_current if applicable.
        membrane_currents, downsampled_time = fiber.membrane_currents(downsample)
        sfap = fiber.sfap(membrane_currents, rec_potentials)
        save_sfap(saving_params, sfap, downsampled_time, amp_ind)
        if save_adjusted_im:
            save_matrix(saving_params, membrane_currents, amp_ind)


def threshold_protocol(
    fiber,
    protocol_configs: dict,
    sim_configs: dict,
    stimulation: ScaledStim,
    stimamp_top: float,
    stimamp_bottom: float,
    ap_detect_location: float,
    find_threshold_kws: dict,
) -> float:
    """Prepare for bisection threshold search.

    :param fiber: fiber object
    :param protocol_configs: dictionary containing protocol configs from <sim_index>.json
    :param sim_configs: dictionary containing simulation configs from <sim_index>.json
    :param stimulation: instance of ScaledStim class
    :param stimamp_top: top stimamp to start bounds search
    :param stimamp_bottom: bottom stimamp to start bounds search
    :param ap_detect_location: location to detect APs for threshold search
    :param find_threshold_kws: dictionary containing keyword arguments for find_threshold
    :return: returns threshold amplitude (nA)
    """
    block_delay = 0
    if protocol_configs['mode'] == 'ACTIVATION_THRESHOLD':
        condition = ThresholdCondition.ACTIVATION
    elif protocol_configs['mode'] == 'BLOCK_THRESHOLD':
        condition = ThresholdCondition.BLOCK
        assert fiber.stim is not None, 'Fiber must have intrinsic activity for block threshold search'
        block_delay = fiber.stim.start

    # determine termination protocols for binary search
    termination_mode, termination_tolerance = handle_termination(protocol_configs)
    bounds_search_mode, bounds_search_step, max_iterations = handle_bounds_search(protocol_configs['bounds_search'])

    # submit fiber for simulation
    amp, _ = stimulation.find_threshold(
        fiber=fiber,
        condition=condition,
        bounds_search_mode=bounds_search_mode,
        bounds_search_step=bounds_search_step,
        termination_mode=termination_mode,
        termination_tolerance=termination_tolerance,
        stimamp_top=stimamp_top,
        stimamp_bottom=stimamp_bottom,
        max_iterations=max_iterations,
        ap_detect_location=ap_detect_location,
        block_delay=block_delay,
        **find_threshold_kws,
    )
    print(f'Threshold found! {amp} mA for a fiber with diameter {sim_configs["fibers"]["z_parameters"]["diameter"]}')
    return amp


# load in arguments from command line
if __name__ == "__main__":  # Allows for the safe importing of the main module
    main(*sys.argv[1:])
    print('done')

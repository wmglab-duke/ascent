"""Helper functions for saving data from NEURON simulations."""

import os
import warnings

import numpy as np
import pandas as pd
from pyfibers import Fiber, ScaledStim


def initialize_saving(
    saving_configs: dict, fiber: Fiber, fiber_ind: int, inner_ind: int, sim_path: str, dt: float, sfap: bool = False
) -> dict:
    """Initialize saving parameters.

    :param saving_configs: dictionary containing saving configurations (from sim.json)
    :param fiber: instance of Fiber class
    :param fiber_ind: index of fiber in list of fibers
    :param inner_ind: index of inner in list of inners
    :param sim_path: path to simulation directory
    :param dt: time step of stimulation (ms)
    :param sfap: whether sfap recordings will be generated
    :return: dictionary containing saving parameters
    """
    # set defaults and then load in saving configurations
    space_configs = {'vm': False, 'imembrane': False, 'gating': False, 'times': []}
    time_configs = {'vm': False, 'imembrane': False, 'gating': False, 'istim': False, 'locs': []}
    space_configs.update(saving_configs.get('space', {}))
    time_configs.update(saving_configs.get('time', {}))

    # Determine optional saving configurations and set fiber saving properties
    if space_configs['vm'] or time_configs['vm']:
        fiber.set_save_vm()
    if space_configs['gating'] or time_configs['gating']:
        fiber.set_save_gating()
    if sfap:
        fiber.set_save_im(allsec=True)
        fiber.set_save_vext()
        if space_configs['imembrane'] or time_configs['imembrane']:
            # Could be changed to support both if could save im for allsec and regular independently
            warnings.warn('saving i_membrane is not supported for sfap generation, setting to False.', stacklevel=2)
            space_configs['imembrane'] = time_configs['imembrane'] = False
    else:
        if space_configs['imembrane'] or time_configs['imembrane']:
            fiber.set_save_im()

    space_times = saving_configs['space']['times']
    locs = saving_configs['time']['locs']
    nodecount = len(fiber.nodes) if fiber else 0

    time_inds = [int(t / dt) for t in (space_times or [])]
    time_inds.sort()
    node_inds = [int((nodecount - 1) * loc) for loc in (locs or [])] if locs != 'all' else list(range(nodecount))
    node_inds.sort()
    output_path = os.path.join(sim_path, 'data', 'outputs')
    os.makedirs(output_path, exist_ok=True)
    return {
        'inner_ind': inner_ind,
        'fiber_ind': fiber_ind,
        'space_vm': space_configs['vm'],
        'space_im': space_configs['imembrane'],
        'space_gating': space_configs['gating'],
        'time_inds': time_inds,
        'time_vm': time_configs['vm'],
        'time_im': time_configs['imembrane'],
        'time_gating': time_configs['gating'],
        'istim': time_configs['istim'],
        'node_inds': node_inds,
        'ap_loctime': saving_configs.get('aploctime', False),
        'runtime': saving_configs.get('runtimes', False),
        'output_path': output_path,
    }


def save_thresh(params: dict, thresh: float):
    """Save threshold from NEURON simulation to file.

    :param params: dictionary containing saving parameters
    :param thresh: activation threshold from NEURON simulation
    """
    thresh_path = os.path.join(
        params['output_path'], f'thresh_inner{params["inner_ind"]}_fiber{params["fiber_ind"]}.dat'
    )
    np.savetxt(thresh_path, [thresh], fmt='%.6f')


def save_runtime(params: dict, runtime: float, amp_ind: int = 0):
    """Save NEURON simulation runtime to file.

    :param params: dictionary containing saving parameters
    :param runtime: runtime of NEURON simulation
    :param amp_ind: index of amplitude in list of amplitudes for finite_amplitude protocol
    """
    if params['runtime']:
        runtimes_path = os.path.join(
            params['output_path'], f'runtime_inner{params["inner_ind"]}_fiber{params["fiber_ind"]}_amp{amp_ind}.dat'
        )
        np.savetxt(runtimes_path, [runtime], fmt='%.3f')


def save_sfap(params: dict, sfap: list, downsampled_time: list, amp_ind: int = 0):
    """Save single fiber action potential (sfap).

    :param params: dictionary containing saving parameters
    :param sfap: sfap signal
    :param downsampled_time: time matching downsampling of sfap
    :param amp_ind: index of amplitude in list of amplitudes for finite_amplitude protocol
    """
    sfap_path = os.path.join(
        params['output_path'], f'SFAP_time_inner{params["inner_ind"]}_fiber{params["fiber_ind"]}_amp{amp_ind}.dat'
    )
    # create a dataframe of downsampled time and sfap
    sfap_df = pd.DataFrame({'Time (ms)': downsampled_time, 'SFAP (uV)': sfap})
    sfap_df.to_csv(sfap_path, sep=' ', float_format='%.6f', index=False)


def save_matrix(params: dict, imembrane_matrix: np.ndarray, amp_ind: int = 0):
    """Save matrix of transmembrane currents, adjusted for periaxonal current.

    :param params: dictionary containing saving parameters
    :param imembrane_matrix: the matrix, columns=sections, rows=time points
    :param amp_ind: index of amplitude in list of amplitudes for finite_amplitude protocol
    """
    adj_im_path = os.path.join(
        params['output_path'],
        f'adjusted_imembrane_inner{params["inner_ind"]}_fiber{params["fiber_ind"]}_amp{amp_ind}.npy',
    )
    # Consider using hdf5 for this and all large data, for now use np.save
    np.save(adj_im_path, imembrane_matrix)


def save_activation(params: dict, n_aps: int, amp_ind: int):
    """Save the number of action potentials that occurred at the location specified in sim config to file.

    :param params: dictionary containing saving parameters
    :param n_aps: number of action potentials that occurred
    :param amp_ind: index of amplitude
    """
    output_file_path = os.path.join(
        params['output_path'], f'activation_inner{params["inner_ind"]}_fiber{params["fiber_ind"]}_amp{amp_ind}.dat'
    )
    np.savetxt(output_file_path, [n_aps], fmt='%d')


def save_variables(params: dict, fiber: Fiber, stimulation: ScaledStim, amp_ind: int = 0):
    """Write user-specified variables to file.

    :param params: dictionary containing saving parameters
    :param fiber: instance of Fiber class
    :param stimulation: instance of ScaledStim class
    :param amp_ind: index of amplitude if protocol is FINITE_AMPLITUDES
    """
    params['time_inds'] = [t for t in params['time_inds'] if t < len(stimulation.time)]
    if fiber.vm is not None:
        target_len = max(len(vm) for vm in fiber.vm if vm is not None)
        vm_data = pd.DataFrame(list(vm) if vm is not None else [None] * target_len for vm in fiber.vm)
        vm_data = vm_data.fillna(0)
        if params['space_vm']:
            save_data(params, amp_ind, fiber, vm_data, stimulation.dt, 'vm', 'space', stimulation, 'mV')
        if params['time_vm']:
            save_data(params, amp_ind, fiber, vm_data, stimulation.dt, 'vm', 'time', stimulation, 'mV')
    if fiber.im is not None:
        target_len = max(len(im) for im in fiber.im if im is not None)
        im_data = pd.DataFrame(list(im) if im is not None else [None] * target_len for im in fiber.im)
        im_data = im_data.fillna(0)
        if params['space_im']:
            save_data(params, amp_ind, fiber, im_data, stimulation.dt, 'imembrane', 'space', stimulation, 'nA')
        if params['time_im']:
            save_data(params, amp_ind, fiber, im_data, stimulation.dt, 'imembrane', 'time', stimulation, 'nA')
    if fiber.gating is not None:
        all_gating_data = {}
        for gating_parameter, gating_data in fiber.gating.items():
            target_len = max(len(g) for g in gating_data if g is not None)
            all_gating_data[gating_parameter] = pd.DataFrame(
                [list(g) if g is not None else [None] * target_len for g in gating_data]
            )
            all_gating_data[gating_parameter] = all_gating_data[gating_parameter].fillna(0)
        if params['space_gating']:
            save_gating_data(params, all_gating_data, amp_ind, fiber, stimulation.dt, 'space', stimulation)
        if params['time_gating']:
            save_gating_data(params, all_gating_data, amp_ind, fiber, stimulation.dt, 'time', stimulation)
    if params['ap_loctime']:
        save_aploctime(params, amp_ind, fiber)
    if params['istim']:
        save_istim_as_time_function(params, fiber, stimulation)


def save_istim_as_time_function(params: dict, fiber: Fiber, stimulation: ScaledStim, amp_ind: int = 0):
    """Save Istim as a function of time to file.

    :param params: dictionary containing saving parameters
    :param fiber: instance of Fiber class
    :param stimulation: instance of ScaledStim class
    :param amp_ind: index of amplitude if protocol is FINITE_AMPLITUDES
    """
    istim_path = os.path.join(
        params['output_path'], f'istim_time_inner{params["inner_ind"]}_fiber{params["fiber_ind"]}_amp{amp_ind}.dat'
    )
    istim_data = pd.DataFrame({'Time (ms)': stimulation.time, 'Istim (nA)': np.array(fiber.syn_current)})
    istim_data.to_csv(istim_path, sep=' ', float_format='%.6f', index=False)


def save_data(
    params: dict,
    amp_ind: int,
    fiber: Fiber,
    data: pd.DataFrame,
    dt: float,
    var_type: str,
    save_type: str,
    stimulation: ScaledStim,
    units: str = None,
):
    """General method to save data to file.

    :param params: dictionary containing saving parameters
    :param amp_ind: index of the amplitude in the finite amplitude protocol
    :param fiber: instance of Fiber class
    :param data: DataFrame containing the data to be saved
    :param dt: time step of stimulation (ms)
    :param var_type: type of variable to be saved (vm, istim, gating parameters)
    :param save_type: function of variable to be saved (space or time)
    :param stimulation: instance of ScaledStim class
    :param units: units of variable (mV, nA)
    """
    file_path = os.path.join(
        params['output_path'],
        f'{var_type}_{save_type}_inner{params["inner_ind"]}_fiber{params["fiber_ind"]}_amp{amp_ind}.dat',
    )
    if save_type == 'space':
        data = data[params['time_inds']]  # save data only at user-specified times
        data.insert(0, 'Node#', list(range(len(fiber.nodes))))
    elif save_type == 'time':
        data = data.T[params['node_inds']]  # save data only at user-specified locations
        data.insert(0, 'Time', stimulation.time)
    header = handle_header(params, save_type=save_type, var_type=var_type, dt=dt, units=units)
    data.to_csv(file_path, header=header, sep=' ', float_format='%.6f', index=False)


def save_gating_data(
    params: dict, all_gating_data: dict, amp_ind: int, fiber: Fiber, dt: float, save_type: str, stimulation: ScaledStim
):
    """General method to save gating data to file.

    :param params: dictionary containing saving parameters
    :param all_gating_data: dictionary containing gating data DataFrames
    :param amp_ind: index of amplitude in finite amplitudes protocol
    :param fiber: instance of Fiber class
    :param dt: time step of simulation (ms)
    :param save_type: function of variable to be saved (space or time)
    :param stimulation: instance of ScaledStim class
    """
    if (save_type == 'space' and params['space_gating']) or (save_type == 'time' and params['time_gating']):
        for gating_param, gating_data in all_gating_data.items():
            save_data(params, amp_ind, fiber, gating_data, dt, "gating_" + gating_param, save_type, stimulation, '')


def handle_header(params: dict, save_type: str, var_type: str, dt: float = None, units: str = None):
    """Create a header for text file.

    :param params: dictionary containing saving parameters
    :param save_type: function of variable to be saved, can be function of time ('time') or space ('space')
    :param var_type: type of variable to be saved (Vm, h, mp, m, s)
    :param units: units of variable (mV, nA)
    :param dt: float value for stimulation time step (ms)
    :return: list of column headers
    """
    if save_type == 'space':  # F(x) - function of space
        return space_header(params, var_type=var_type, dt=dt, units=units)
    if save_type == 'time':  # F(t) - function of time
        return time_header(params, var_type=var_type, units=units)
    return []


def space_header(params: dict, var_type: str, dt: float, units: str = None) -> list[str]:
    """Create header for F(x) files.

    :param params: dictionary containing saving parameters
    :param var_type: type of variable to be saved (Vm, h, mp, m, s)
    :param dt: float value of stimulation time step (ms)
    :param units: units of variable (mV, nA)
    :return: returns list of strings to be used in file header
    """
    header = ['Node#']
    suffix = f'({units})' if units else ''
    for time in params['time_inds']:
        header.append(f'time{(float(time) * float(dt))}ms{suffix}')
    return header


def time_header(params: dict, var_type: str, units: str = None) -> list[str]:
    """Create header for F(t) files.

    :param params: dictionary containing saving parameters
    :param var_type: type of variable to be saved (Vm, h, mp, m, s)
    :param units: units of variable (mV, nA)
    :return: returns list of strings to be used as file header
    """
    header = ['Time(ms)']
    suffix = f'({units})' if units else ''
    if var_type != 'istim':
        for node in params['node_inds']:
            header.append(f'node{node}{suffix}')
    elif var_type == 'istim':
        header.append(f'Istim({units})')
    return header


def save_aploctime(params: dict, amp_ind: int, fiber: Fiber):
    """Save time when last NoR AP was detected for each node to file.

    :param params: dictionary containing saving parameters
    :param amp_ind: index of amplitude in finite amplitudes protocol
    :param fiber: instance of Fiber class
    """
    aploctime_path = os.path.join(
        params['output_path'], f'ap_loctime_inner{params["inner_ind"]}_fiber{params["fiber_ind"]}_amp{amp_ind}.dat'
    )
    ap_loctime_data = pd.DataFrame(
        {'Node#': list(range(len(fiber.nodes))), 'AP_LocTime (ms)': [ap.time for ap in fiber.apc]}
    )
    ap_loctime_data.to_csv(aploctime_path, sep=' ', float_format='%.6f', index=False)

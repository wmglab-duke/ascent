#!/usr/bin/env python3.7

"""Converts previous version configuration files to present version (for integration testing only).

Developer instructions:
1. Add functions below to convert Sample, Model, and Sim config JSONs to local tree format from the format saved in the
/integration_tests directories. Below are the conversions from v1.4.0->1.5.0
2. Add each function to the list of operations to perform on each config file
(SAMPLE_CONVERSION, MODEL_CONVERSION, and SIM_CONVERSION).
3. Run the integration test as normal. The below function convert_configs will be called by integration.py.
"""

import json
import os


# SAMPLE Conversion Functions
def _add_mask_space(sample_dict):
    # New parameter with v1.5.0
    sample_dict['mask_space'] = 'CARTESIAN'


# MODEL Conversion Functions
def _add_inner_tol(model_dict):
    if 'trace_interp_tol' in model_dict:
        model_dict['inner_interp_tol'] = model_dict['trace_interp_tol']
        model_dict['outer_interp_tol'] = model_dict['trace_interp_tol']
        model_dict['nerve_interp_tol'] = model_dict['trace_interp_tol']
        del model_dict['trace_interp_tol']


def _add_orders(model_dict):
    model_dict['mesh']['shape_order'] = 'quadratic'
    model_dict['solver']['sorder'] = 2


# SIM Conversion Functions
def _convert_intracellular_stim(sim_dict):
    # Warning will be thrown, 'intracellular_stim' configuration unused by PyFibers. Currently not supported in v1.5.0.
    pass


def _remove_intracellular_recording(sim_dict):
    # istim saving not allowed without PyFibers intrinsic activity
    if 'intrinsic_activity' not in sim_dict:
        sim_dict['saving']['time']['istim'] = False


def _add_ap_loc(sim_dict):
    # istim saving not allowed without PyFibers intrinsic activity
    sim_dict['protocol']['threshold']['ap_detect_location'] = 0.9


# Add functions to these lists as needed
SAMPLE_CONVERSION = [_add_mask_space]
MODEL_CONVERSION = [_add_inner_tol, _add_orders]
SIM_CONVERSION = [_convert_intracellular_stim, _remove_intracellular_recording, _add_ap_loc]


# Main conversion function called by integration.py
def convert_configs(test_index):
    """Convert older test configurations to current format.

    :param test_index: integer index of integration test.
    """
    sample_dict = load_json(f'samples/{test_index}/sample.json')
    for sc in SAMPLE_CONVERSION:
        sc(sample_dict)

    save_json(f'samples/{test_index}/sample.json', sample_dict)

    for m in os.listdir(f'samples/{test_index}/models'):
        model_dict = load_json(f'samples/{test_index}/models/{m}/model.json')

        for mc in MODEL_CONVERSION:
            mc(model_dict)

        save_json(f'samples/{test_index}/models/{m}/model.json', model_dict)

    sim_dict = load_json(f'config/user/sims/{test_index}.json')
    for sc in SIM_CONVERSION:
        sc(sim_dict)
    save_json(f'config/user/sims/{test_index}.json', sim_dict)


# Helper functions
def load_json(config_path: str):
    """Load in json data and returns to user and assume it has already been validated.

    :param config_path: the string path to load up
    :return: json data (usually dict or list)
    """
    with open(config_path) as handle:
        return json.load(handle)


def save_json(config_path: str, config_dict: dict):
    """Save dictonary configuration as JSON.

    :param config_path: the string path to save to
    :param config_dict: config data
    """
    with open(config_path, 'w') as handle:
        json.dump(config_dict, handle, indent=2)

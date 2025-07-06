#!/usr/bin/env python3.11

"""Runs integration tests for ASCENT.

The copyrights of this software are owned by Duke University. Please
refer to the LICENSE and README.md files for licensing instructions. The
source code can be found on the following GitHub repository:
https://github.com/wmglab-duke/ascent
"""
import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from convert_configs import convert_configs

parser = argparse.ArgumentParser(description='ASCENT Integration Testing')

parser.add_argument(
    'test_folder',
    type=str,
    choices=os.listdir('tests/integration_tests'),
    help='Name of the integration test to run.',
)
parser.add_argument(
    '--skip-setup',
    action='store_true',
    help='Skips test setup, only checks specified samples/ against integration_tests/.',
)
parser.add_argument(
    '--skip-test',
    action='store_true',
    help='Skips file comparison, only sets up and runs test models.',
)
save_group = parser.add_mutually_exclusive_group()
save_group.add_argument(
    '--save',
    '-s',
    action='store_true',
    help='Saves the sample folder as a new (full) test. Subtests will be skipped.',
)
save_group.add_argument(
    '--subtest',
    choices=['pre_java', 'java', 'neuron', 'full'],
    default='full',
    help='Specified pipeline portion will be tested alone (default=full).',
)


def load_json(config_path: str):
    """Load in json data and returns to user and assume it has already been validated.

    :param config_path: the string path to load up
    :return: json data (usually dict or list)
    """
    with open(config_path) as handle:
        return json.load(handle)


def setup_test_inputs(test_path: Path, test_ind: int):
    """Set up test configuration inputs.

    :param test_path: Path to test folder
    :param test_ind: integer index for test
    :returns: path to samples/ integer index
    :raises FileNotFoundError: if no mock sample and no tiff files present in test folder.
    :raises RuntimeError: if mock morphology generator fails.
    """
    # Make sure there is either mock_samples.json or .tif files
    mock_sample_path = test_path / "mock.json"
    if not mock_sample_path.exists():
        mock_sample_path = None
        if list(test_path.glob("*.tif")) is None:
            raise FileNotFoundError('No image files present in test directory')

    # handle input directory
    sample_name = load_json(test_path / "sample.json")["sample"]
    input_path = Path(f"input/{sample_name}")
    if os.path.exists(input_path):
        shutil.rmtree(input_path)
    time.sleep(1)
    input_path.mkdir(parents=True)
    if any(input_path.iterdir()):
        print(f"{input_path} is not empty")

    if mock_sample_path is not None:
        print("attempting to generate mock sample")
        mock_path = Path("config/user/mock_samples")
        mock_path.mkdir(parents=True, exist_ok=True)
        shutil.copy(mock_sample_path, f"config/user/mock_samples/{test_ind}.json")
        cp = subprocess.run(["python", "run", "mock_morphology_generator", str(test_ind)], check=True)
        if cp.returncode != 0:
            raise RuntimeError(f"Mock morphology generator failed {test_ind}")
        print("mock sample generation complete")
    else:
        for tif in test_path.glob("*.tif"):
            shutil.copy(tif, input_path)

    if os.path.exists(test_path / 'explicit_fibersets'):
        shutil.copytree(test_path / 'explicit_fibersets', input_path / 'explicit_fibersets', dirs_exist_ok=True)

    sample_path = Path(f"samples/{test_ind}")
    if os.path.exists(sample_path):
        shutil.rmtree(sample_path)
        time.sleep(1)
    model_path = sample_path / f"models/{test_ind}"
    sims_path = Path("config/user/sims")
    runs_path = Path("config/user/runs")
    sample_path.mkdir(parents=True, exist_ok=True)
    model_path.mkdir(exist_ok=True, parents=True)
    sims_path.mkdir(parents=True, exist_ok=True)
    runs_path.mkdir(exist_ok=True, parents=True)
    shutil.copy(test_path / "sample.json", sample_path)
    shutil.copy(test_path / "model.json", model_path)
    shutil.copy(test_path / "sim.json", f"config/user/sims/{test_ind}.json")

    run_template = load_json("config/templates/run.json")
    run_template["models"] = [test_ind]
    run_template["sample"] = test_ind
    run_template["sims"] = [test_ind]
    run_template["export_behavior"] = "overwrite"

    with open(f"config/user/runs/{test_ind}.json", "w") as handle:
        json.dump(run_template, handle, indent=2)

    convert_configs(test_ind)

    return sample_path


def setup_java_test(test_path: Path, test_ind: int):
    """Set up test configuration to only test the java pipeline portion.

    :param test_path: Path to test folder
    :param test_ind: integer index for test
    :returns: path to samples/ integer index
    """
    sample_path = setup_test_inputs(test_path, test_ind)

    pre_java_dirs = [
        'slides',
    ]
    pre_java_files = [
        'sample.obj',
        f'models/{test_ind}/model.obj',
        f'models/{test_ind}/sims/{test_ind}/sim.obj',
        f'models/{test_ind}/sims/{test_ind}/explicit.txt',
    ]

    for sim in os.listdir(test_path / f'models/{test_ind}/sims'):
        pre_java_dirs.extend([f'models/{test_ind}/sims/{sim}/fibersets', f'models/{test_ind}/sims/{sim}/waveforms'])

    for pjd in pre_java_dirs:
        os.makedirs(sample_path / pjd, exist_ok=True)
        shutil.copytree(test_path / pjd, sample_path / pjd, dirs_exist_ok=True)

    for pjf in pre_java_files:
        if os.path.exists(test_path / pjf):
            shutil.copyfile(test_path / pjf, sample_path / pjf)

    return sample_path


def setup_neuron_test(test_path: Path, test_ind: int):
    """Set up test configuration to only test the NEURON pipeline portion.

    :param test_path: Path to test folder
    :param test_ind: integer index for test
    :returns: path to samples/ integer index
    """
    sample_path = setup_java_test(test_path, test_ind)

    pre_submit_dirs = [f'models/{test_ind}/mesh']
    pre_submit_files = []
    dummy_files = [f'models/{test_ind}/mesh/mesh.mph']

    for sim in os.listdir(test_path / f'models/{test_ind}/sims'):
        pre_submit_dirs.append(f'models/{test_ind}/sims/{sim}/fibersets_bases')
        for n_sim in os.listdir(test_path / f'models/{test_ind}/sims/{sim}/n_sims'):
            pre_submit_dirs.extend([f'models/{test_ind}/sims/{sim}/n_sims/{n_sim}/data/inputs'])
            pre_submit_files.extend(
                [
                    f'models/{test_ind}/sims/{sim}/n_sims/{n_sim}/{n_sim}.json',
                ]
            )

    sim_json = load_json(test_path / 'sim.json')
    for cuff_idx, (cuff_json, contact_weights) in enumerate(sim_json['active_srcs'].items()):
        cuff_name = cuff_json.split('.')[0]
        for contact_idx in range(len(contact_weights[0])):
            dummy_files.append(
                f'models/{test_ind}/bases/{contact_idx}_Cuff {cuff_idx}_{cuff_name} Contact {contact_idx+1}.mph'
            )

    for psd in pre_submit_dirs:
        os.makedirs(sample_path / psd, exist_ok=True)
        shutil.copytree(test_path / psd, sample_path / psd, dirs_exist_ok=True)

    for psf in pre_submit_files:
        shutil.copyfile(test_path / psf, sample_path / psf)

    for df in dummy_files:
        dummy_path = sample_path / df
        dummy_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dummy_path, 'w') as f:
            f.write('dummy')

    return sample_path


def import_n_sims(test_ind, test_name):
    """Import n_sims to /samples folder.

    :param test_ind: integer index for test
    :param test_name: string name of the test
    :returns: number of missing n_sims
    """
    cp = subprocess.run(["python", "run", "import_n_sims", str(test_ind)])
    if cp.returncode != 0:
        print(
            f"Import failed for {test_ind}_{test_name}. NEURON simulations may not be finished - try re-running "
            f"with --skip-setup."
        )
    else:
        time.sleep(1)
    return cp.returncode


def move_test(test_ind, test_name, subtest, copy=True):
    """Move integration test from /samples to /output.

    :param test_ind: integer index for test
    :param test_name: string name of the test
    :param subtest: string name of the subtest
    :param copy: if false, /samples directory will be removed
    """
    out_path = 'output/' + f'{test_ind}_{test_name}-{subtest}_test'
    if os.path.exists(out_path):
        shutil.rmtree(out_path)
    time.sleep(1)
    shutil.copytree(f'samples/{test_ind}', out_path)
    time.sleep(1)
    if not copy:
        shutil.rmtree(f'samples/{test_ind}')
    for root, _, files in os.walk(out_path):
        for file in files:
            if file.endswith(".mph") or file.endswith(".png") or file.endswith(".tif"):
                os.remove(os.path.join(root, file))


def run_pre_java_test(test_path: Path, test_ind: int, test_name: str):
    """Check pipeline outputs from input up to the Java (COMSOL) handoff.

    :param test_path: Path to test folder
    :param test_ind: integer index for test
    :param test_name: string name of the test
    :raises RuntimeError: if pipeline fails
    """
    print('------------------------ pre_java pipeline ------------------------')

    # Import input files
    _ = setup_test_inputs(test_path, test_ind)

    # Run pre-java pre_java pipeline
    cp = subprocess.run(["python", "run", "pipeline", "-b", "pre_java", "--test", "-E", "overwrite", str(test_ind)])
    if cp.returncode != 0:
        raise RuntimeError(f"Pre-Java pipeline failed for {test_ind}_{test_name}")

    move_test(test_ind, test_name, 'pre_java')


def run_java_test(test_path: Path, test_ind: int, test_name: str):
    """Check pipeline from java handoff up to the NEURON submission.

    :param test_path: Path to test folder
    :param test_ind: integer index for test
    :param test_name: string name of the test
    :raises RuntimeError: if pipeline fails
    """
    print('------------------------ Java pipeline ------------------------')

    # Import pre-java output files
    _ = setup_java_test(test_path, test_ind)

    # Run COMSOL and export Ve
    cp = subprocess.run(["python", "run", "pipeline", "--test", "-E", "overwrite", str(test_ind)])
    if cp.returncode != 0:
        raise RuntimeError(f"Java pipeline failed for {test_ind}_{test_name}")

    move_test(test_ind, test_name, 'pre_java')


def run_neuron_test(test_path: Path, test_ind: int, test_name: str):
    """Check pipeline from the NEURON submission to the end.

    :param test_path: Path to test folder
    :param test_ind: integer index for test
    :param test_name: string name of the test
    :raises RuntimeError: if pipeline fails
    """
    print('------------------------ NEURON pipeline ------------------------')

    # Import post-java output files
    _ = setup_neuron_test(test_path, test_ind)

    # Export n_sims
    cp = subprocess.run(["python", "run", "pipeline", "--test", "-E", "overwrite", str(test_ind)])
    if cp.returncode != 0:
        raise RuntimeError(f"Post-Java failed for {test_ind}_{test_name}")
    time.sleep(5)

    # Submit fibers
    os.chdir('submit')
    cp = subprocess.run(["python", "submit.py", "-s", str(test_ind)])
    if cp.returncode != 0:
        raise RuntimeError(f"NEURON submission failed for {test_ind}_{test_name}")
    os.chdir('..')

    import_n_sims(test_ind, test_name)
    move_test(test_ind, test_name, 'neuron', copy=True)


def run_full_test(test_path: Path, test_ind: int, test_name: str):
    """Check full ASCENT pipeline.

    :param test_path: Path to test folder
    :param test_ind: integer index for test
    :param test_name: string name of the test
    :raises RuntimeError: if pipeline fails
    """
    print('------------------------ Full pipeline ------------------------')

    _ = setup_test_inputs(test_path, test_ind)

    cp = subprocess.run(["python", "run", "pipeline", "--test", "-E", "overwrite", str(test_ind)])
    if cp.returncode != 0:
        raise RuntimeError(f"Pipeline failed for {test_ind}_{test_name}")
    time.sleep(5)

    # Submit fibers
    os.chdir('submit')
    cp = subprocess.run(["python", "submit.py", "-s", str(test_ind)])
    if cp.returncode != 0:
        raise RuntimeError(f"NEURON submission failed for {test_ind}_{test_name}")
    os.chdir('..')

    import_n_sims(test_ind, test_name)
    move_test(test_ind, test_name, 'full', copy=True)


def check_test(test_path: Path, test_ind: int, test_name: str, subtest: str):
    """Check integration test against specified folder.

    :param test_path: Path to test folder
    :param test_ind: integer index for test
    :param test_name: string name of the test
    :param subtest: string name of the subtest
    """
    ignore_dict = load_json('tests/test_ignore.json')
    sys.path.append(os.getcwd())
    output_folder = f'output/{test_ind}_{test_name}-{subtest}_test'
    isdiff = importlib.import_module('scripts.compare').compare_directories(
        test_path, output_folder, ignore_dict[subtest + '_test']
    )
    if isdiff:
        print(f'!!! {test_ind}_{test_name}-{subtest} integration test failed')


def save_test(test_path, test_ind, test_name, subtest):
    """Save integration test.

    :param test_path: Path to test folder
    :param test_ind: integer index for test
    :param test_name: string name of the test
    :param subtest: string name of the subtest
    """
    output_folder = Path('output') / f'{test_ind}_{test_name}-{subtest}_test'
    assert output_folder.exists(), f"{output_folder} not found"
    shutil.copytree(output_folder, test_path, dirs_exist_ok=True)
    shutil.copyfile(f'config/user/sims/{test_ind}.json', test_path / 'sim.json')
    shutil.copyfile(test_path / f'models/{test_ind}/model.json', test_path / 'model.json')
    print(f'Created test for {test_ind}_{test_name}')


def run_test():
    """Run integration test from specified folder.

    :raises ValueError: if env.json does not exist
    :raises ValueError: if save and any subtest other than 'full' was passed
    :raises RuntimeError: if NEURON sims are missing
    """
    env_path = Path("config") / 'system' / 'env.json'
    if not env_path.exists():
        raise ValueError(f'env_path does not exist, so likely not in ASCENT working directory:\n\t{env_path}')
    env_config = load_json(env_path)
    project_path = Path(env_config['ASCENT_PROJECT_PATH'])

    # FORCE PROGRAM TO BE IN ASCENT WORKING DIRECTORY
    if not Path.cwd() == project_path:
        raise ValueError('You are trying to run this script from a directory other than your ASCENT working directory')

    args = parser.parse_args()
    test_folder = args.test_folder

    test_ind, test_name = test_folder.split('_')
    test_ind = int(test_ind)
    test_path = Path(f"tests/integration_tests/{test_folder}")

    pre_java, java, neuron, full = False, False, False, True
    if args.subtest == 'pre_java':
        pre_java = True
    elif args.subtest == 'java':
        java = True
    elif args.subtest == 'neuron':
        neuron = True

    if any((pre_java, java, neuron)):
        full = False
        if args.save:
            raise ValueError('Only "full" --subtest can be passed with --save')

    if not args.skip_setup:
        if pre_java:
            run_pre_java_test(test_path, test_ind, test_name)
        elif java:
            run_java_test(test_path, test_ind, test_name)
        elif neuron:
            run_neuron_test(test_path, test_ind, test_name)
        elif full:
            run_full_test(test_path, test_ind, test_name)

    if not args.skip_test and not args.save:
        if args.subtest in ['neuron', 'full']:
            import_n_sims(test_ind, test_name)
        move_test(test_ind, test_name, args.subtest)
        check_test(test_path, test_ind, test_name, args.subtest)

    if args.save:
        skips = import_n_sims(test_ind, test_name)
        if skips == 0:
            move_test(test_ind, test_name, 'full', copy=True)
            save_test(test_path, test_ind, test_name, 'full')
        else:
            raise RuntimeError('Missing simulations, failed to create test')


if __name__ == "__main__":
    run_test()

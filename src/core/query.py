#!/usr/bin/env python3.7

"""Defines Query class.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing
instructions. The source code can be found on the following GitHub
repository: https://github.com/wmglab-duke/ascent
"""

import os
import pickle
import warnings

import numpy as np
import pandas as pd

from src.core import Sample, Simulation, Slide
from src.utils import Config, Configurable, Object, Saveable, SetupMode


class Query(Configurable, Saveable):
    """Query is for analyzing data after running NEURON simulations.

    IMPORTANT: MUST BE RUN FROM PROJECT LEVEL
    """

    def __init__(self, criteria: str | dict):
        """Set up Query object.

        :param criteria: dictionary of search criteria
        """
        # set up superclasses
        Configurable.__init__(self)

        self._ran: bool = False  # marker will be set to True one self.run() is called (as is successful)

        if isinstance(criteria, str):
            # this must be the path to the criteria
            self.add(SetupMode.NEW, Config.CRITERIA, criteria)
        elif isinstance(criteria, dict):
            # criteria was passed in as a dictionary!
            self.add(SetupMode.OLD, Config.CRITERIA, criteria)

        self._result = None  # begin with empty result

    def run(self):  # noqa C901
        """Build query result using criteria.

        :raises TypeError: if any indices are not integers
        :raises IndexError: If no sample results are found
        :return: self
        """
        # initialize empty result
        result = {}

        # preliminarily find sample, model, and sim filter indices if applicable (else None)
        sample_indices = self.search(Config.CRITERIA, 'indices', 'sample', optional=True)
        if isinstance(sample_indices, int):
            sample_indices = [sample_indices]

        model_indices = self.search(Config.CRITERIA, 'indices', 'model', optional=True)
        if isinstance(model_indices, int):
            model_indices = [model_indices]

        sim_indices = self.search(Config.CRITERIA, 'indices', 'sim', optional=True)
        if isinstance(sim_indices, int):
            sim_indices = [sim_indices]

        # check that all sets of indices contain only integers
        for indices in (sample_indices, model_indices, sim_indices):
            if indices is not None and not all(isinstance(i, int) for i in indices):
                raise TypeError('Encountered a non-integer index. Check your search criteria.')

        # criteria for each layer
        sample_criteria = self.search(Config.CRITERIA, 'sample', optional=True)
        model_criteria = self.search(Config.CRITERIA, 'model', optional=True)
        sim_criteria = self.search(Config.CRITERIA, 'sim', optional=True)

        # control if missing sim criteria or both sim and model criteria
        include_downstream = self.search(Config.CRITERIA, 'include_downstream', optional=True)

        # labeling for samples level
        samples_key = 'samples'
        samples_dir = samples_key

        # init list of samples in result
        result[samples_key] = []

        # loop samples
        for sample in os.listdir(samples_dir):
            # skip this sample if applicable
            if sample.startswith('.') or (sample_indices is not None and int(sample) not in sample_indices):
                continue

            # if applicable, check against sample criteria
            if sample_criteria is not None and not self._match(
                sample_criteria,
                self.load(os.path.join(samples_dir, sample, 'sample.json')),
            ):
                continue

            # labeling for models level
            models_key = 'models'
            models_dir = os.path.join(samples_dir, sample, models_key)

            # post-filtering, add empty SAMPLE to result
            # important to remember that this is at END of list
            result[samples_key].append({'index': int(sample), models_key: []})

            # if no downstream criteria and NOT including downstream, skip lower loops
            # note also that the post loop removal of samples will be skipped (as we desire in this case)
            if (
                (model_criteria is None)
                and (model_indices is None)
                and (sim_criteria is None)
                and (sim_indices is None)
                and (not include_downstream)
            ):
                continue

            # loop models
            for model in os.listdir(models_dir):
                # if there are filter indices for models, use them
                if model.startswith('.') or (model_indices is not None and int(model) not in model_indices):
                    continue

                # if applicable, check against model criteria
                if model_criteria is not None and not self._match(
                    model_criteria,
                    self.load(os.path.join(models_dir, model, 'model.json')),
                ):
                    continue

                # labeling for sims level
                sims_key = 'sims'
                sims_dir = os.path.join(models_dir, model, sims_key)

                # post-filtering, add empty MODEL to result
                # important to remember that this is at END of list
                result[samples_key][-1][models_key].append({'index': int(model), sims_key: []})

                # if no downstream criteria and NOT including downstream, skip lower loops
                # note also that the post loop removal of models will be skipped (as we desire in this case)
                if sim_criteria is None and not include_downstream:
                    continue

                # loop sims
                for sim in os.listdir(sims_dir):
                    if sim.startswith('.') or (sim_indices is not None and int(sim) not in sim_indices):
                        continue

                    # if applicable, check against model criteria
                    if sim_criteria is not None and not self._match(
                        sim_criteria,
                        self.load(os.path.join('config', 'user', 'sims', sim + '.json')),
                    ):
                        continue

                    # post-filtering, add SIM to result
                    result[samples_key][-1][models_key][-1][sims_key].append(int(sim))

                # remove extraneous model if no sims were found
                # only reached if sim_criteria not None
                if len(result[samples_key][-1][models_key][-1][sims_key]) == 0:
                    result[samples_key][-1][models_key].pop(-1)

            # remove extraneous sample if no sims were found
            # only reached if model_criteria not None
            if len(result[samples_key][-1][models_key]) == 0:
                result[samples_key].pop(-1)

        if len(result['samples']) == 0:
            raise IndexError("Query run did not return any sample results. Check your indices and try again.")

        self._result = result

        return self

    def summary(self) -> dict:
        """Return result of self.run().

        :raises LookupError: If no results (i.e. Query.run() has not been called)
        :return: result as a dict
        """
        if self._result is None:
            raise LookupError(
                "There are no query results. You must call Query.run() before fetching result via Query.summary()"
            )

        return self._result

    def get_config(self, mode: Config, indices: list[int]) -> dict:
        """Load .json config file for given mode and indices.

        :param mode: Config enum (e.g. Config.SAMPLE)
        :param indices: list of indices (e.g. [0, 1, 2]). These are sample, model, and sim indices, respectively.
            For a sample, pass only one index. For a model, pass two indices. For a sim, pass three indices.
        :return: config file as a dict
        """
        return self.load(self.build_path(mode, indices))

    @staticmethod
    def get_object(mode: Object, indices: list[int]) -> Sample | Simulation:
        """Load pickled object for given mode and indices.

        :param mode: mode of object (e.g. Object.SAMPLE)
        :param indices: indices of object (e.g. [0, 0, 0]). These are the sample, model, and sim indices, respectively.
            For a sample, pass only [sample_index]. For a model, pass [sample_index, model_index].
        :return: object
        """
        with open(Query.build_path(mode, indices), 'rb') as obj:
            return pickle.load(obj)

    @staticmethod
    def build_path(
        mode: Config | Object,
        indices: list[int] = None,
        just_directory: bool = False,
    ) -> str:
        """Build path to config or object file for given mode and indices.

        :param mode: from Config or Object enum (e.g. Config.SAMPLE)
        :param indices: list of indices (e.g. [0, 1, 2]). These are sample, model, and sim indices, respectively.
            For just a sample or model, pass [0] or [0, 1], respectively.
        :param just_directory: if True, return path to directory containing file, not the path to the file itself
        :raises ValueError: if invalid mode is chosen
        :return: path
        """
        if indices is None:
            indices = [
                0,
                0,
                0,
            ]  # dummy values... will be stripped from path later bc just_directory is set to True
            just_directory = True

        if mode == Config.SAMPLE:
            result = os.path.join('samples', str(indices[0]), 'sample.json')
        elif mode == Config.MODEL:
            result = os.path.join('samples', str(indices[0]), 'models', str(indices[1]), 'model.json')
        elif mode == Config.SIM:
            result = os.path.join('config', 'user', 'sims', f'{indices[0]}.json')
        elif mode == Object.SAMPLE:
            result = os.path.join('samples', str(indices[0]), 'sample.obj')
        elif mode == Object.SIMULATION:
            result = os.path.join(
                'samples',
                str(indices[0]),
                'models',
                str(indices[1]),
                'sims',
                str(indices[2]),
                'sim.obj',
            )
        else:
            raise ValueError(f'INVALID MODE: {type(mode)}')

        if just_directory:
            result = os.path.join(*result.split(os.sep)[:-1])

        return result  # noqa: R504

    def _match(self, criteria: dict, data: dict) -> bool:
        for key in criteria.keys():
            # ensure key is valid in data
            if key not in data:
                raise KeyError(f"Criterion key {key} not found in data")

            # corresponding values
            c_val = criteria[key]
            d_val = data[key]

            # now lots of control flow - dependent on the types of the variables
            # if c_val is a dict, recurse
            if isinstance(c_val, dict):
                if not self._match(c_val, d_val):
                    return False

            # neither c_val nor d_val are list
            elif not any(isinstance(v, list) for v in (c_val, d_val)):
                if c_val != d_val:
                    return False

            # c_val IS list, d_val IS NOT list
            elif isinstance(c_val, list) and not isinstance(d_val, list):
                if d_val not in c_val:
                    return False

            # c_val IS NOT list, d_val IS list
            elif not isinstance(c_val, list) and isinstance(d_val, list):
                # "partial matches" indicates that other values may be present in d_val
                if not self.search(Config.CRITERIA, 'partial_matches') or c_val not in d_val:
                    return False

            # both c_val and d_val are list
            else:  # all([isinstance(v, list) for v in (c_val, d_val)]):
                # "partial matches" indicates that other values may be present in d_val
                if not self.search(Config.CRITERIA, 'partial_matches') or not all(c_i in d_val for c_i in c_val):
                    return False

        return True

    def excel_output(
        self,
        filepath: str,
        sample_keys=None,
        model_keys=None,
        sim_keys=None,
        individual_indices: bool = True,
        config_paths: bool = True,
        column_width: int = None,
        console_output: bool = True,
        optional_keys=False,
    ):
        """Output summary of query.

        NOTE: for all key lists, the values themselves are lists, functioning as a JSON pointer.

        :param: filepath: output filepath
        :param: sample_keys: Sample keys to output. Defaults to [].
        :param: model_keys: Model keys to output. Defaults to [].
        :param: sim_keys: Sim keys to output. Defaults to [].
        :param: individual_indices: Include column for each index. Defaults tp True.
        :param: config_paths: Include column for each config path. Defaults to True.
        :param: column_width: Column width for Excel document. Defaults to None (system default).
        :param: console_output: Print progress to console. Defaults to True.
        :param optional_keys: If True, check parameter presence in config files as optional. Defaults to False.
        """
        sims: dict = {}
        sample_keys: list[list] = sample_keys if sample_keys else []
        model_keys: list[list] = model_keys if model_keys else []
        sim_keys: list[list] = sim_keys if sim_keys else []

        # SAMPLE
        sample_results: dict
        for sample_results in self._result.get('samples', []):
            sample_index: int = sample_results['index']
            sample_config_path: str = self.build_path(Config.SAMPLE, [sample_index])
            sample_config: dict = self.load(sample_config_path)
            self.add(SetupMode.OLD, Config.SAMPLE, sample_config)

            if console_output:
                print(f'sample: {sample_index}')

            # MODEL
            model_results: dict
            for model_results in sample_results.get('models', []):
                model_index = model_results['index']
                model_config_path: str = self.build_path(Config.MODEL, [sample_index, model_index])
                model_config: dict = self.load(model_config_path)
                self.add(SetupMode.OLD, Config.MODEL, model_config)

                if console_output:
                    print(f'\tmodel: {model_index}')

                # SIM
                for sim_index in model_results.get('sims', []):
                    sim_config_path, sim_dir, sim_object = self.handle_sim(
                        sim_index,
                        sample_index,
                        model_index,
                        console_output,
                        sims,
                        config_paths,
                        sample_keys,
                        model_keys,
                        sim_keys,
                        individual_indices,
                    )

                    # NSIM
                    for nsim_index, (
                        potentials_product_index,
                        waveform_index,
                    ) in enumerate(sim_object.master_product_indices):
                        self.handle_nsim(
                            sim_dir,
                            nsim_index,
                            sim_object,
                            potentials_product_index,
                            sample_keys,
                            model_keys,
                            sim_keys,
                            sample_index,
                            model_index,
                            sim_index,
                            individual_indices,
                            waveform_index,
                            config_paths,
                            sims,
                            sample_config_path,
                            model_config_path,
                            sim_config_path,
                            optional_keys,
                        )

                    # "prune" old configs
                    self.remove(Config.SIM)
                self.remove(Config.MODEL)
            self.remove(Config.SAMPLE)

        # build Excel file, with one sim per sheet
        writer = pd.ExcelWriter(filepath)
        for sim_index, sheet_data in sims.items():
            sheet_name = f'Sim {sim_index}'
            pd.DataFrame(sheet_data).to_excel(writer, sheet_name=sheet_name, header=False, index=False)
            if column_width is not None:
                writer.sheets[sheet_name].set_column(0, 256, column_width)
            else:
                writer.sheets[sheet_name].set_column(0, 256)

        writer.save()

    def handle_sim(  # noqa: D102
        self,
        sim_index: int,
        sample_index: int,
        model_index: int,
        console_output: bool,
        sims: dict,
        config_paths: str,
        sample_keys: list[int] = None,
        model_keys: list[int] = None,
        sim_keys: list[int] = None,
        individual_indices: bool = True,
    ):
        sim_config_path = self.build_path(Config.SIM, indices=[sim_index])
        sim_config = self.load(sim_config_path)
        self.add(SetupMode.OLD, Config.SIM, sim_config)
        sim_object: Simulation = self.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])
        sim_dir = self.build_path(
            Object.SIMULATION,
            [sample_index, model_index, sim_index],
            just_directory=True,
        )
        if console_output:
            print(f'\t\tsim: {sim_index}')
        # init sheet if necessary
        if str(sim_index) not in sims.keys():
            # base header
            sample_parts = [
                'Sample Index',
                *['->'.join(['sample'] + key) for key in sample_keys],
            ]
            model_parts = [
                'Model Index',
                *['->'.join(['model'] + key) for key in model_keys],
            ]
            sim_parts = [
                'Sim Index',
                *['->'.join(['sim'] + key) for key in sim_keys],
            ]
            header = [
                'Indices',
                *(sample_parts if individual_indices else sample_parts[1:]),
                *(model_parts if individual_indices else model_parts[1:]),
                *(sim_parts if individual_indices else sim_parts[1:]),
            ]
            if individual_indices:
                header += ['Nsim Index']
            # populate with nsim factors
            for fib_key_name in sim_object.fiberset_key:
                header.append(fib_key_name)
            for wave_key_name in sim_object.wave_key:
                header.append(wave_key_name)
            # add paths
            if config_paths:
                header += [
                    'Sample Config Path',
                    'Model Config Path',
                    'Sim Config Path',
                    'NSim Path',
                ]
            # set header as first row
            sims[str(sim_index)] = [header]
        return sim_config_path, sim_dir, sim_object

    def handle_nsim(  # noqa: D102
        self,
        sim_dir: str,
        nsim_index: int,
        sim_object: Simulation,
        potentials_product_index: int,
        sample_keys: list,
        model_keys: list,
        sim_keys: list,
        sample_index: int,
        model_index: int,
        sim_index: int,
        individual_indices: bool,
        waveform_index: int,
        config_paths: bool,
        sims: list[str],
        sample_config_path: str,
        model_config_path: str,
        sim_config_path: str,
        optional_keys,
    ):
        nsim_dir = os.path.join(sim_dir, 'n_sims', str(nsim_index))
        (
            active_src_index,
            *active_rec_index,
            fiberset_index,
        ) = sim_object.potentials_product[potentials_product_index]
        # fetch additional sample, model, and sim values
        # that's one juicy list comprehension right there
        values = [
            [self.search(config, *key, optional=optional_keys) for key in category]
            for category, config in zip(
                [sample_keys, model_keys, sim_keys],
                [Config.SAMPLE, Config.MODEL, Config.SIM],
            )
        ]
        # base row data
        sample_parts = [sample_index, *values[0]]
        model_parts = [model_index, *values[1]]
        sim_parts = [sim_index, *values[2]]
        row = [
            f'{sample_index}_{model_index}_{sim_index}_{nsim_index}',
            *(sample_parts if individual_indices else sample_parts[1:]),
            *(model_parts if individual_indices else model_parts[1:]),
            *(sim_parts if individual_indices else sim_parts[1:]),
        ]
        if individual_indices:
            row += [nsim_index]
        # populate factors (same order as header)
        for fib_key_value in sim_object.fiberset_product[fiberset_index]:
            row.append(fib_key_value)
        for wave_key_value in sim_object.wave_product[waveform_index]:
            row.append(wave_key_value)
        # add paths
        if config_paths:
            row += [
                sample_config_path,
                model_config_path,
                sim_config_path,
                nsim_dir,
            ]
        # add to sim sheet
        sims[str(sim_index)].append(row)

    def import_tm_current_matrix(
        self, nsim
    ):  # This should move to common data extraction and allow for any amps/fibers/inners/so on
        """Extract current amplitude, number of axons, time vector, and transmembrane current matrix from a binary file.

        :param nsim: nsim index to pull data from
        :return: time_vector: time points correlating with transmembrane currents
        :return: current_matrix: transmembrane current matrix
        """
        sample_results = self._result.get('samples', [])[0]
        model_results = sample_results.get('models', [])[0]
        sim = model_results.get('sims', [])[0]
        # Pulls data from first fiber in each nsim.
        imembrane_file_name = os.path.join(
            os.getcwd(),
            f"samples/{sample_results['index']}/models/{model_results['index']}/sims/{sim}/n_sims/"
            f"{nsim}/data/outputs/adjusted_imembrane_inner0_fiber0_amp0.npy",
        )
        current_matrix = np.load(imembrane_file_name)  # should be columns=section and rows = time step
        waveform_file = os.path.join(
            os.getcwd(),
            f"samples/{sample_results['index']}/models/{model_results['index']}/sims/{sim}/n_sims/"
            f"{nsim}/data/inputs/waveform.dat",
        )
        wfdata = np.loadtxt(waveform_file)
        sfap_file = os.path.join(
            os.getcwd(),
            f"samples/{sample_results['index']}/models/{model_results['index']}/sims/{sim}/n_sims/"
            f"{nsim}/data/outputs/SFAP_time_inner0_fiber0_amp0.dat",
        )
        sfapdata = np.loadtxt(sfap_file, skiprows=1)
        return wfdata[1], sfapdata[:, 0], current_matrix

    def common_data_extraction(  # noqa C901
        self,
        data_types: list[str],
        sim_indices: list[int] = None,
        q_fiber_indices: list[int] | str = 'all',
        ignore_missing: bool = False,
        amp_indices: int | str = 'all',
    ) -> list[dict]:
        """Extract data from a simulation for specified data types.

        This method extracts common data from a simulation for each specified data type and returns
        a list of dictionaries containing the extracted data.

        Options for data types include:
            - 'sfap': SFAP data
            - 'threshold': Threshold data
            - 'runtime': Runtime data
            - 'activation': Activation data
            - 'istim': Istim data
            - 'time_gating': Time gating data
            - 'time_vm': Time voltage data
            - 'space_gating': Space gating data
            - 'space_vm': Space voltage data
            - 'aploctime': AP location time data
            - 'apendtimes': AP end times data

        :param q_fiber_indices: A list of fiber indices to include. ('all' for all fibers)
        :param sim_indices: A list of simulation indices to include.
        :param ignore_missing: If True, missing data will not cause an error.
        :param data_types: A list of strings representing the data types to extract.
        :param amp_indices: A list of amplitude indices to include. ('all' for all amplitudes)
        :raises LookupError: If no results (i.e. Query.run() has not been called)
        :raises TypeError: If data_types is not a list
        :raises ValueError: If an invalid data type is provided
        :return: A list of dictionaries containing the extracted data.
        """
        # assert that data_types is a list
        if not isinstance(data_types, list):
            raise TypeError('data_types must be a list of strings.')

        # validation
        if self._result is None:
            raise LookupError("No query results, Query.run() must be called before calling analysis methods.")

        if sim_indices is None:
            sim_indices = self.search(Config.CRITERIA, 'indices', 'sim')

        alldat = []

        # loop samples
        sample_results: dict
        for sample_results in self._result.get('samples', []):
            sample_index = sample_results['index']
            sample_object: Sample = self.get_object(Object.SAMPLE, [sample_index])
            slide: Slide = sample_object.slides[0]
            n_inners = sum(len(fasc.inners) for fasc in slide.fascicles)

            # loop models
            for model_results in sample_results.get('models', []):
                model_index = model_results['index']

                for sim_index in sim_indices:
                    sim_object = self.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

                    # whether the comparison key is for 'fiber' or 'wave', the nsims will always be in order!
                    # this realization allows us to simply loop through the factors in sim.factors[key] and treat the
                    # indices as if they were the nsim indices
                    for nsim_index, (
                        potentials_product_index,
                        waveform_index,
                    ) in enumerate(sim_object.master_product_indices):
                        (
                            active_src_index,
                            *active_rec_index,
                            fiberset_index,
                        ) = sim_object.potentials_product[potentials_product_index]
                        # fetch outer->inner->fiber and out->inner maps
                        out_in_fib, out_in = sim_object.fiberset_map_pairs[fiberset_index]

                        # build base dirs for fetching thresholds
                        sim_dir = self.build_path(
                            Object.SIMULATION,
                            [sample_index, model_index, sim_index],
                            just_directory=True,
                        )
                        n_sim_dir = os.path.join(sim_dir, 'n_sims', str(nsim_index))

                        # fetch all data
                        for inner in range(n_inners):
                            outer = [index for index, inners in enumerate(out_in) if inner in inners][0]
                            available_fiber_ind = out_in_fib[outer][out_in[outer].index(inner)]
                            if q_fiber_indices == 'all':
                                fiber_indices = available_fiber_ind
                            else:
                                fiber_indices = q_fiber_indices
                            for local_fiber_index, _ in enumerate(available_fiber_ind):
                                master_index = sim_object.indices_n_to_fib(fiberset_index, inner, local_fiber_index)

                                if master_index in fiber_indices:
                                    # set index for finite amps
                                    if sim_object.configs[Config.SIM.value]['protocol']['mode'] == 'FINITE_AMPLITUDES':
                                        amp_indices = (
                                            amp_indices
                                            if amp_indices != 'all'
                                            else range(
                                                len(sim_object.configs[Config.SIM.value]['protocol']['amplitudes'])
                                            )
                                        )
                                    else:
                                        amp_indices = [0]

                                    for amp_ind in amp_indices:
                                        data = {
                                            'sample': sample_results['index'],
                                            'model': model_results['index'],
                                            'sim': sim_index,
                                            'nsim': nsim_index,
                                            'inner': inner,
                                            'fiber': local_fiber_index,
                                            'master_fiber_index': master_index,
                                            'fiberset_index': fiberset_index,
                                            'waveform_index': waveform_index,
                                            'active_src_index': active_src_index,
                                            'active_rec_index': active_rec_index,
                                            'amp_ind': amp_ind,
                                        }
                                        for data_type in data_types:
                                            if data_type == 'sfap':
                                                self.retrieve_sfap_data(data, n_sim_dir, ignore_missing, alldat)
                                            elif data_type == 'threshold':
                                                self.retrieve_threshold_data(data, n_sim_dir, ignore_missing, alldat)
                                            elif data_type == 'runtime':
                                                self.retrieve_runtime_data(data, n_sim_dir, alldat)
                                            elif data_type == 'activation':
                                                self.retrieve_activation_data(data, n_sim_dir, alldat)
                                            elif data_type == 'istim':
                                                self.retrieve_istim_data(data, n_sim_dir, alldat)
                                            elif data_type == 'time_gating':
                                                self.retrieve_time_gating_data(data, n_sim_dir, alldat)
                                            elif data_type == 'time_vm':
                                                self.retrieve_time_vm_data(data, n_sim_dir, alldat)
                                            elif data_type == 'space_gating':
                                                self.retrieve_space_gating_data(data, n_sim_dir, alldat)
                                            elif data_type == 'space_vm':
                                                self.retrieve_space_vm_data(data, n_sim_dir, alldat)
                                            elif data_type == 'aploctime':
                                                self.retrieve_aploctime_data(data, n_sim_dir, alldat)
                                            else:
                                                raise ValueError(f'Invalid data type: {data_type}')
                                        # add the data to list
                                        alldat.append(data.copy())
        return pd.DataFrame(alldat)

    def retrieve_sfap_data(self, data: dict, n_sim_dir: str, ignore_missing: bool, alldat: list[dict]):  # noqa: D
        sfap_path = os.path.join(
            n_sim_dir,
            'data',
            'outputs',
            f'SFAP_time_inner{data["inner"]}_fiber{data["fiber"]}_amp0.dat',
        )
        if ignore_missing:
            try:
                sfap = np.loadtxt(sfap_path, skiprows=1)
            except OSError:
                sfap = np.array([[np.nan, np.nan]])
                warnings.warn('Missing SFAP, but continuing.', stacklevel=2)
        else:
            sfap = np.loadtxt(sfap_path, skiprows=1)

        data['SFAP_times'] = sfap[:, 0]
        data['SFAP'] = sfap[:, 1]

    def retrieve_threshold_data(self, data: dict, n_sim_dir: str, ignore_missing: bool, alldat: list[dict]):  # noqa: D
        thresh_path = os.path.join(
            n_sim_dir,
            'data',
            'outputs',
            f'thresh_inner{data["inner"]}_fiber{data["fiber"]}.dat',
        )
        if ignore_missing:
            try:
                threshold = np.loadtxt(thresh_path)
            except OSError:
                threshold = np.array(np.nan)
                warnings.warn('Missing threshold, but continuing.', stacklevel=2)
        else:
            threshold = np.loadtxt(thresh_path)

        if threshold.size > 1:
            threshold = threshold[-1]

        data['threshold'] = threshold

    def retrieve_runtime_data(self, data: dict, n_sim_dir: str, alldat: list[dict]):  # noqa: D
        runtime_path = os.path.join(
            n_sim_dir,
            'data',
            'outputs',
            f'runtime_inner{data["inner"]}_fiber{data["fiber"]}_amp{data["amp_ind"]}.dat',
        )
        with open(runtime_path) as runtime_file:
            runtime = float(runtime_file.read().replace('s', ''))
        data['runtime'] = runtime

    def retrieve_activation_data(self, data: dict, n_sim_dir: str, alldat: list[dict]):  # noqa: D
        activation_path = os.path.join(
            n_sim_dir,
            'data',
            'outputs',
            f'activation_inner{data["inner"]}_fiber{data["fiber"]}_amp{data["amp_ind"]}.dat',
        )
        with open(activation_path) as activation_file:
            n_aps = int(activation_file.read())
        data['n_aps'] = n_aps

    def retrieve_aploctime_data(self, data: dict, n_sim_dir: str, alldat: list[dict]):  # noqa: D
        aploctime_path = os.path.join(
            n_sim_dir,
            'data',
            'outputs',
            f'ap_loctime_inner{data["inner"]}_fiber{data["fiber"]}_amp{data["amp_ind"]}.dat',
        )
        ap_loctime = np.loadtxt(aploctime_path)
        data['ap_loctime'] = ap_loctime

    def retrieve_istim_data(self, data: dict, n_sim_dir: str, alldat: list[dict]):  # noqa: D
        istim_path = os.path.join(
            n_sim_dir,
            'data',
            'outputs',
            f'Istim_inner{data["inner"]}_fiber{data["fiber"]}_amp{data["amp_ind"]}.dat',
        )
        istim_data = pd.read_csv(istim_path, sep='\t')
        data['istim_data'] = istim_data

    def retrieve_time_gating_data(self, data: dict, n_sim_dir: str, alldat: list[dict]):  # noqa: D
        gating_params = ['h', 'm', 'mp', 's']
        data['gating_time_data'] = {}
        for gating_param in gating_params:
            gating_time_path = os.path.join(
                n_sim_dir,
                'data',
                'outputs',
                f'gating_{gating_param}_time_inner{data["inner"]}_fiber{data["fiber"]}_amp{data["amp_ind"]}.dat',
            )
            gating_time_data = pd.read_csv(gating_time_path, sep=' ')
            data['gating_time_data'][gating_param] = gating_time_data

    def retrieve_time_vm_data(self, data: dict, n_sim_dir: str, alldat: list[dict]):  # noqa: D
        vm_time_path = os.path.join(
            n_sim_dir,
            'data',
            'outputs',
            f'Vm_time_inner{data["inner"]}_fiber{data["fiber"]}_amp{data["amp_ind"]}.dat',
        )
        vm_time_data = pd.read_csv(vm_time_path, sep=' ')
        data['vm_time_data'] = vm_time_data

    def retrieve_space_gating_data(self, data: dict, n_sim_dir: str, alldat: list[dict]):  # noqa: D
        gating_params = ['h', 'm', 'mp', 's']
        data['gating_space_data'] = {}
        for gating_param in gating_params:
            gating_space_path = os.path.join(
                n_sim_dir,
                'data',
                'outputs',
                f'gating_{gating_param}_space_inner{data["inner"]}_fiber{data["fiber"]}_amp{data["amp_ind"]}.dat',
            )
            gating_space_data = pd.read_csv(gating_space_path, sep=' ')
            data['gating_space_data'][gating_param] = gating_space_data

    def retrieve_space_vm_data(self, data: dict, n_sim_dir: str, alldat: list[dict]):  # noqa: D
        vm_space_path = os.path.join(
            n_sim_dir,
            'data',
            'outputs',
            f'Vm_space_inner{data["inner"]}_fiber{data["fiber"]}_amp{data["amp_ind"]}.dat',
        )
        vm_space_data = pd.read_csv(vm_space_path, sep=' ')
        data['vm_space_data'] = vm_space_data

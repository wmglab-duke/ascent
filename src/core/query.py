#!/usr/bin/env python3.7

"""Defines Query class.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing
instructions. The source code can be found on the following GitHub
repository: https://github.com/wmglab-duke/ascent
"""

import os
import pickle
import struct
import warnings

import numpy as np
import pandas as pd
from scipy import stats as stats

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

    def sfap_data(
        self,
        fiber_indices: list[int] = None,
        all_fibers: bool = False,
        ignore_missing: bool = False,
        amplitude_indices: tuple[int] = (0,),
    ):
        """Obtain SFAP data as a pandas DataFrame for user-defined fiber indices or all fibers.

        :param fiber_indices: list of fiber indexes to pull SFAP data for. Default: single fiber 0.
        :param all_fibers: If True, all fiber's SFAP data will be pulled. If False, only fiber_indices will be pulled.
        :param ignore_missing: if True, missing threshold data will not cause an error.
        :param amplitude_indices: list of amplitude indices to pull SFAP data for. Default: single amplitude 0.
        :raises LookupError: If no results (called before Query.run())
        :return: pandas DataFrame of SFAP data.
        """
        if self._result is None:
            raise LookupError("No query results, Query.run() must be called before calling analysis methods.")
        if fiber_indices is None:
            fiber_indices = [0]
        [samples, models, sims] = list(self.configs['criteria']['indices'].values())

        # Note: simplify/clean this function. Inspired by threshold_data for first quick approach.
        sample_results: dict
        for sample_results in self._result.get('samples', []):
            sample_index = sample_results['index']
            sample_object: Sample = self.get_object(Object.SAMPLE, [sample_index])
            slide: Slide = sample_object.slides[0]
            n_inners = sum(len(fasc.inners) for fasc in slide.fascicles)

            # loop models
            for model_results in sample_results.get('models', []):
                model_index = model_results['index']

                for sim_index in sims:
                    sim_object = self.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

                    # whether the comparison key is for 'fiber' or 'wave', the nsims will always be in order!
                    # this realization allows us to simply loop through the factors in sim.factors[key] and treat the
                    # indices as if they were the nsim indices
                    #   Better optimized method: loop over master_indices to only obtain data for desired fibers.
                    #       Need to find another way to obtain nsim_index...
                    master_indices = []
                    for i in sim_object.master_product_indices:
                        if i[0] in fiber_indices:
                            master_indices.append(i)

                    # init SFAP container for this model, sim, nsim
                    sfap_data: list[dict] = []
                    for nsim_index, (
                        potentials_product_index,
                        waveform_index,
                    ) in enumerate(sim_object.master_product_indices):
                        (
                            active_src_index,
                            active_rec_index,
                            fiberset_index,
                        ) = sim_object.potentials_product[potentials_product_index]
                        # fetch outer->inner->fiber and out->inner maps
                        out_in_fib, out_in = sim_object.fiberset_map_pairs[fiberset_index]

                        # build base dirs for fetching SFAPs
                        sim_dir = self.build_path(
                            Object.SIMULATION,
                            [sample_index, model_index, sim_index],
                            just_directory=True,
                        )
                        n_sim_dir = os.path.join(sim_dir, 'n_sims', str(nsim_index))

                        # fetch all SFAPs
                        for inner in range(n_inners):
                            outer = [index for index, inners in enumerate(out_in) if inner in inners][0]

                            for local_fiber_index, _ in enumerate(out_in_fib[outer][out_in[outer].index(inner)]):
                                master_index = sim_object.indices_n_to_fib(fiberset_index, inner, local_fiber_index)

                                sfap = []
                                # Get all amplitudes
                                for amp in amplitude_indices:
                                    sfap_path = os.path.join(
                                        n_sim_dir,
                                        'data',
                                        'outputs',
                                        f'SFAP_time_inner{inner}_fiber{local_fiber_index}_amp{amp}.dat',
                                    )
                                    if ignore_missing:
                                        try:
                                            sfap_amp = np.loadtxt(sfap_path, skiprows=1)
                                        except OSError:
                                            sfap_amp = np.array([[np.nan, np.nan]])
                                            warnings.warn('Missing SFAP, but continuing.', stacklevel=2)
                                    else:
                                        sfap_amp = np.loadtxt(sfap_path, skiprows=1)
                                    sfap.append(sfap_amp)

                                for i, row in enumerate(sfap[0]):
                                    base = {
                                        'sample': sample_results['index'],
                                        'model': model_results['index'],
                                        'sim': sim_index,
                                        'nsim': nsim_index,
                                        'inner': inner,
                                        'fiber': local_fiber_index,
                                        'index': master_index,
                                        'fiberset_index': fiberset_index,
                                        'waveform_index': waveform_index,
                                        'active_src_index': active_src_index,
                                        'active_rec_index': active_rec_index,
                                        'SFAP_times': row[0] - 1.2,
                                    }
                                    for j, sfap_amp in enumerate(sfap):
                                        base[f'SFAP{j}'] = sfap_amp[i][1]
                                    sfap_data.append(base)

        sfap_data = pd.DataFrame(sfap_data)
        return sfap_data.loc[sfap_data['index'].isin(fiber_indices)] if not all_fibers else sfap_data

    def threshold_data(
        self,
        sim_indices: list[int] = None,
        ignore_missing=False,
        meanify=False,
    ):
        """Obtain threshold data as a pandas DataFrame.

        Waveform, fiberset, and active_src indices are per your sim configuration file.

        :param sim_indices: list of simulation indices to include in the threshold data.
        :param ignore_missing: if True, missing threshold data will not cause an error.
        :param meanify: if True, the threshold data will be returned as a mean of each nsim.
        :raises LookupError: If no results (called before Query.run())
        :return: pandas DataFrame of thresholds.
        """
        # quick helper class for storing data values

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

                        # init thresholds container for this model, sim, nsim
                        thresholds: list[float] = []

                        # fetch all thresholds
                        for inner in range(n_inners):
                            outer = [index for index, inners in enumerate(out_in) if inner in inners][0]

                            for local_fiber_index, _ in enumerate(out_in_fib[outer][out_in[outer].index(inner)]):
                                master_index = sim_object.indices_n_to_fib(fiberset_index, inner, local_fiber_index)

                                thresh_path = os.path.join(
                                    n_sim_dir,
                                    'data',
                                    'outputs',
                                    f'thresh_inner{inner}_fiber{local_fiber_index}.dat',
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
                                if meanify is True:
                                    thresholds.append(abs(threshold))
                                else:
                                    alldat.append(
                                        {
                                            'sample': sample_results['index'],
                                            'model': model_results['index'],
                                            'sim': sim_index,
                                            'nsim': nsim_index,
                                            'inner': inner,
                                            'fiber': local_fiber_index,
                                            'index': master_index,
                                            'fiberset_index': fiberset_index,
                                            'waveform_index': waveform_index,
                                            'active_src_index': active_src_index,  # Note: only report src or rec
                                            'active_rec_index': active_rec_index,  # Doesn't make sense to do both
                                            'threshold': abs(threshold),
                                        }
                                    )

                        if meanify is True:
                            if len(thresholds) == 0:
                                alldat.append(
                                    {
                                        'sample': sample_results['index'],
                                        'model': model_results['index'],
                                        'sim': sim_index,
                                        'nsim': nsim_index,
                                        'fiberset_index': fiberset_index,
                                        'waveform_index': waveform_index,
                                        'active_src_index': active_src_index,
                                        'active_rec_index': active_rec_index,
                                        'mean': np.nan,
                                    }
                                )
                            else:
                                thresholds: np.ndarray = np.array(thresholds)

                                alldat.append(
                                    {
                                        'sample': sample_results['index'],
                                        'model': model_results['index'],
                                        'sim': sim_index,
                                        'nsim': nsim_index,
                                        'fiberset_index': fiberset_index,
                                        'waveform_index': waveform_index,
                                        'active_src_index': active_src_index,
                                        'active_rec_index': active_rec_index,
                                        'mean': np.mean(thresholds),
                                        'std': np.std(thresholds, ddof=1),
                                        'sem': stats.sem(thresholds),
                                    }
                                )

        return pd.DataFrame(alldat)

    def excel_output(  # noqa: C901
        self,
        filepath: str,
        sample_keys=None,
        model_keys=None,
        sim_keys=None,
        individual_indices: bool = True,
        config_paths: bool = True,
        column_width: int = None,
        console_output: bool = True,
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
        :param: console_output: Print progress to console. Defaults to False.
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

                    # NSIM
                    for nsim_index, (
                        potentials_product_index,
                        waveform_index,
                    ) in enumerate(sim_object.master_product_indices):
                        nsim_dir = os.path.join(sim_dir, 'n_sims', str(nsim_index))
                        (
                            active_src_index,
                            fiberset_index,
                        ) = sim_object.potentials_product[potentials_product_index]
                        # fetch additional sample, model, and sim values
                        # that's one juicy list comprehension right there
                        values = [
                            [self.search(config, *key) for key in category]
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

    def import_tm_current_matrix(self, nsim):
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
            f"{nsim}/data/outputs/Imembrane_inner0_fiber0_amp0.dat",
        )

        with open(imembrane_file_name, 'rb') as file:
            alldata = file.read()
            # Currently it is in native format, might need to be in standard format.
            _, _, tstop, _, _, dt, _, _, axon_num, vector_size, _ = struct.unpack(
                "@iidiidiidii", alldata[:56]  # 56 is the total number of bytes correlating with the format
            )
            current_matrix = np.array(struct.unpack_from(f"{vector_size}d", alldata[56:]))
        file.close()

        # Build current matrix and time vectors from file data
        current_matrix = current_matrix.reshape(
            ((int)(vector_size / axon_num), -1), order='F'
        )  # Matlab and Fortran ('F order') both use column-major layout as the default
        time_vector = np.arange(0, dt * (vector_size / axon_num), dt)

        return tstop, time_vector, current_matrix

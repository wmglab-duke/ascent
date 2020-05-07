import os
import pickle
from typing import Union, List, Tuple

import numpy as np
import matplotlib.colorbar as cbar
import matplotlib.colors as mplcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as tick

from core import FiberSet
from src.core import Sample, Simulation, Slide
from src.utils import Exceptionable, Configurable, Saveable, SetupMode, Config, Object


class Query(Exceptionable, Configurable, Saveable):
    """
    IMPORTANT: MUST BE RUN FROM PROJECT LEVEL
    """

    def __init__(self, criteria: Union[str, dict]):
        """
        :param exceptions_config:
        """

        # set up superclasses
        Configurable.__init__(self)
        Exceptionable.__init__(self, SetupMode.NEW)

        self._ran: bool = False  # marker will be set to True one self.run() is called (as is successful)

        if isinstance(criteria, str):
            # this must be the path to the criteria
            self.add(SetupMode.NEW, Config.CRITERIA, criteria)
        elif isinstance(criteria, dict):
            # criteria was passed in as a dictionary!
            self.add(SetupMode.OLD, Config.CRITERIA, criteria)

        self._result = None  # begin with empty result

    def run(self):
        """
        Build query result using criteria
        :return: result as a dict
        """

        # initialize empty result
        result = {}

        # preliminarily find sample, model, and sim filter indices if applicable (else None)
        sample_indices = self.search(Config.CRITERIA, 'indices', 'sample')
        model_indices = self.search(Config.CRITERIA, 'indices', 'model')
        sim_indices = self.search(Config.CRITERIA, 'indices', 'sim')

        # criteria for each layer
        sample_criteria = self.search(Config.CRITERIA, 'sample')
        model_criteria = self.search(Config.CRITERIA, 'model')
        sim_criteria = self.search(Config.CRITERIA, 'sim')

        # control if missing sim criteria or both sim and model criteria
        include_downstream = self.search(Config.CRITERIA, 'include_downstream')

        # labeling for samples level
        samples_key = 'samples'
        samples_dir = samples_key

        # init list of samples in result
        result[samples_key] = []

        # loop samples
        for sample in os.listdir(samples_dir):
            # skip this sample if applicable
            if sample_indices is not None and int(sample) not in sample_indices:
                continue

            # if applicable, check against sample criteria
            if sample_criteria is not None:
                if not self._match(
                        sample_criteria,
                        self.load(os.path.join(samples_dir, sample, 'sample.json'))
                ):
                    continue

            # labeling for models level
            models_key = 'models'
            models_dir = os.path.join(samples_dir, sample, models_key)

            # post-filtering, add empty SAMPLE to result
            # important to remember that this is at END of list
            result[samples_key].append({
                'index': int(sample),
                models_key: []
            })

            # if no downstream criteria and NOT including downstream, skip lower loops
            # note also that the post loop removal of samples will be skipped (as we desire in this case)
            if (model_criteria is None) and (model_indices is None) \
                    and (sim_criteria is None) and (sim_indices is None) and (not include_downstream):
                continue

            # loop models
            for model in os.listdir(models_dir):
                # if there are filter indices for models, use them
                if model_indices is not None and int(model) not in model_indices:
                    continue

                # if applicable, check against model criteria
                if model_criteria is not None:
                    if not self._match(
                            model_criteria,
                            self.load(os.path.join(models_dir, model, 'model.json'))
                    ):
                        continue

                # labeling for sims level
                sims_key = 'sims'
                sims_dir = os.path.join(models_dir, model, sims_key)

                # post-filtering, add empty MODEL to result
                # important to remember that this is at END of list
                result[samples_key][-1][models_key].append({
                    'index': int(model),
                    sims_key: []
                })

                # if no downstream criteria and NOT including downstream, skip lower loops
                # note also that the post loop removal of models will be skipped (as we desire in this case)
                if sim_criteria is None and not include_downstream:
                    continue

                # loop sims
                for sim in os.listdir(sims_dir):
                    if sim_indices is not None and int(sim) not in sim_indices:
                        continue

                    # if applicable, check against model criteria
                    if sim_criteria is not None:
                        if not self._match(
                                sim_criteria,
                                self.load(os.path.join('config', 'user', 'sims', sim + '.json'))
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

        self._result = result

        return self

    def summary(self) -> dict:
        """
        Return result of self.run()... maybe add result statistics? (e.g. counts of samples, models, sims, etc.)
        :return:
        """
        if self._result is None:
            self.throw(53)

        return self._result

    def get_config(self, mode: Config, indices: List[int]) -> dict:
        """

        :return:
        """
        return self.load(self.build_path(mode, indices))

    def get_object(self, mode: Object, indices: List[int]) -> Union[Sample, Simulation]:
        """

        :return:
        """
        with open(self.build_path(mode, indices), 'rb') as obj:
            return pickle.load(obj)

    def build_path(self, mode: Union[Config, Object], indices: List[int] = None, just_directory: bool = False) -> str:
        """

        :param just_directory:
        :param mode:
        :param indices:
        :return:
        """

        result = str()
        # just_directory = False

        if indices is None:
            indices = [0, 0, 0]  # dummy values... will be stripped from path later bc just_directory is set to True
            just_directory = True

        if mode == Config.SAMPLE:
            result = os.path.join('samples', str(indices[0]), 'sample.json')
        elif mode == Config.MODEL:
            result = os.path.join('samples', str(indices[0]), 'models', str(indices[1]), 'model.json')
        elif mode == Config.SIM:
            result = os.path.join('config', 'user', 'sims', '.json'.format(indices[0]))
        elif mode == Object.SAMPLE:
            result = os.path.join('samples', str(indices[0]), 'sample.obj')
        elif mode == Object.SIMULATION:
            result = os.path.join('samples', str(indices[0]), 'models', str(indices[1]), 'sims', str(indices[2]),
                                  'sim.obj')
        else:
            print('INVALID MODE:'.format(type(mode)))
            self.throw(55)

        if just_directory:
            result = os.path.join(*result.split(os.sep)[:-1])

        return result

    def _match(self, criteria: dict, data: dict) -> bool:
        """

        :param criteria:
        :param data:
        :return:
        """

        for key in criteria.keys():

            # ensure key is valid in data
            if key not in data:
                print('ERRONEOUS KEY: '.format(key))
                self.throw(54)

            # corresponding values
            c_val = criteria[key]
            d_val = data[key]

            # now lots of control flow - dependent on the types of the variables

            # if c_val is a dict, recurse
            if type(c_val) is dict:
                if not self._match(c_val, d_val):
                    # print('fail 0')
                    return False

            # neither c_val nor d_val are list
            elif not any([type(v) is list for v in (c_val, d_val)]):
                if not c_val == d_val:
                    # print('fail 1')
                    return False

            # c_val IS list, d_val IS NOT list
            elif type(c_val) is list and type(d_val) is not list:
                if d_val not in c_val:
                    # print('fail 2')
                    return False

            # c_val IS NOT list, d_val IS list
            elif type(c_val) is not list and type(d_val) is list:
                # "partial matches" indicates that other values may be present in d_val
                if not self.search(Config.CRITERIA, 'partial_matches') or c_val not in d_val:
                    # print('fail 3')
                    return False

            # both c_val and d_val are list
            else:  # all([type(v) is list for v in (c_val, d_val)]):
                # "partial matches" indicates that other values may be present in d_val
                if not self.search(Config.CRITERIA, 'partial_matches') or not all([c_i in d_val for c_i in c_val]):
                    # print('fail 4')
                    return False

        return True

    def heatmaps(self,
                 plot: bool = True,
                 plot_mode: str = 'average',
                 colorbar_mode: str = 'subplot',
                 save_path: str = None,
                 plot_outers: bool = False,
                 colormap_str: str = 'viridis',
                 reverse_colormap: bool = True):
        """
        TODO: implement plot_mode and colorbar_mode (current implementation assumes single fiber and fills fascicle)

        :param reverse_colormap:
        :param colormap_str:
        :param plot_outers:
        :param save_path:
        :param plot: bool signalling whether or not to plot the figure
        :param plot_mode:
            'average': each inner is filled with the color corresponding to the average of its fiber thresholds
            'individual': each fiber is plotted individually with its corresponding color
        :param colorbar_mode:
            'subplot': one colorbar/colormap per subplot (i.e., one colorbar for each nsim)
            'figure': one colorbar for the entire figure (i.e., all colors are on same scale)
        :return: generated figure
        """

        print('WARNING: plot_mode and colorbar_mode not yet implemented')

        if self._result is None:
            self.throw(66)

        # loop samples
        sample_results: dict
        for sample_results in self._result.get('samples', []):
            sample_index = sample_results['index']
            sample_object: Sample = self.get_object(Object.SAMPLE, [sample_index])
            sample_config: dict = self.get_config(Config.SAMPLE, [sample_index])
            slide = sample_object.slides[0]
            n_inners = sum(len(fasc.inners) for fasc in slide.fascicles)

            print('sample: {}'.format(sample_index))

            # loop models
            model_results: dict
            for model_results in sample_results.get('models', []):
                model_index = model_results['index']

                print('\tmodel: {}'.format(model_index))

                # calculate orientation point location (i.e., contact location)
                orientation_point = None
                if slide.orientation_point_index is not None:
                    r = slide.nerve.mean_radius() * 1.1  # scale up so orientation point is outside nerve
                    theta = np.arctan2(*tuple(np.flip(slide.nerve.points[slide.orientation_point_index][:2])))
                    theta += np.deg2rad(
                        self.get_config(Config.MODEL, [sample_index, model_index]).get('cuff').get('rotate').get(
                            'add_ang')
                    )
                    orientation_point = r * np.cos(theta), r * np.sin(theta)

                # loop sims
                for sim_index in model_results.get('sims', []):
                    sim_object = self.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

                    print('\t\tsim: {}'.format(sim_index))

                    # init figure with subplots
                    master_product_count = len(sim_object.master_product_indices)
                    rows = int(np.floor(np.sqrt(master_product_count)))
                    cols = int(np.ceil(master_product_count / rows))
                    figure, axes = plt.subplots(rows, cols, constrained_layout=True)

                    # loop nsims
                    for n, (potentials_product_index, waveform_index) in enumerate(sim_object.master_product_indices):
                        active_src_index, fiberset_index = sim_object.potentials_product[potentials_product_index]

                        # fetch axis
                        ax: plt.Axes = axes.reshape(-1)[n]
                        ax.axis('off')

                        # fetch sim information
                        sim_dir = self.build_path(Object.SIMULATION, [sample_index, model_index, sim_index],
                                                  just_directory=True)
                        n_sim_dir = os.path.join(sim_dir, 'n_sims', str(n))
                        fiberset_dir = os.path.join(sim_dir, 'fibersets', str(fiberset_index))

                        # fetch thresholds, then find min and max
                        thresholds = []
                        missing_indices = []
                        for i in range(n_inners):
                            thresh_path = os.path.join(n_sim_dir, 'data', 'outputs',
                                                       'thresh_inner{}_fiber0.dat'.format(i))
                            if os.path.exists(thresh_path):
                                thresholds.append(np.loadtxt(thresh_path)[2])
                            else:
                                missing_indices.append(i)
                                print('MISSING: {}'.format(thresh_path))
                        max_thresh = max(thresholds)
                        min_thresh = min(thresholds)

                        # generate colors from colorbar and thresholds
                        cmap = plt.cm.get_cmap(colormap_str)

                        if reverse_colormap:
                            cmap = cmap.reversed()

                        colors = []
                        offset = 0
                        for i in range(n_inners):
                            actual_i = i - offset
                            if i not in missing_indices:
                                colors.append(cmap((thresholds[actual_i] - min_thresh) / (max_thresh - min_thresh)))
                            else:
                                # NOTE: PLOTS MISSING VALUES AS RED
                                offset += 1
                                colors.append((1, 0, 0, 1))

                        # figure title -- make arbitrary, hard-coded subplot title modifications here (add elif's)
                        title = ''
                        for fib_key_name, fib_key_value in zip(sim_object.fiberset_key,
                                                               sim_object.fiberset_product[fiberset_index]):

                            if fib_key_name == 'fibers->z_parameters->diameter':
                                title = r'{} {}nm'.format(title, int(fib_key_value * 1000))
                            else:
                                # default title
                                title = '{} {}:{}'.format(title, fib_key_name, fib_key_value)

                        for wave_key_name, wave_key_value in zip(sim_object.wave_key,
                                                                 sim_object.wave_product[waveform_index]):
                            # default title
                            title = '{} {}:{}'.format(title, wave_key_name, wave_key_value)

                        ax.set_title(title)

                        # plot orientation point if applicable
                        if orientation_point is not None:
                            ax.plot(*orientation_point, 'r.', markersize=20)

                        # plot slide (nerve and fascicles, defaulting to no outers)
                        sample_object.slides[0].plot(final=False, fix_aspect_ratio=True, fascicle_colors=colors,
                                                     ax=ax, outers_flag=plot_outers, inner_format='k-')

                        # colorbar
                        plt.colorbar(
                            mappable=plt.cm.ScalarMappable(
                                cmap=cmap,
                                norm=mplcolors.Normalize(vmin=min_thresh, vmax=max_thresh)
                            ),
                            ticks=tick.MaxNLocator(nbins=5),
                            ax=ax,
                            orientation='vertical',
                            label=r'mA',
                        )

                    # set super title
                    plt.suptitle(
                        'Activation thresholds: {} (model {})'.format(
                            sample_config.get('sample'),
                            model_index
                        ),
                        size='x-large'
                    )

                    # plot figure
                    if plot:
                        plt.show()

                    # save figure as png
                    if save_path is not None:
                        plt.savefig(
                            '{}{}{}_{}_{}.png'.format(
                                save_path, os.sep, sample_index, model_index, sim_index
                            ), dpi=400
                        )

        return plt.gcf()

    def barcharts_compare_models(self,
                                 sim_index: int = None,
                                 model_indices: List[int] = None,
                                 model_labels: List[str] = None,
                                 title: str = 'Activation Thresholds',
                                 plot: bool = True,
                                 save_path: str = None):
        """

        :param nsim_indices:
        :param plot:
        :param save_path:
        :return:
        """

        # quick helper class for storing data values
        class DataPoint():
            def __init__(self, value: float, error: float = None):
                self.value = value
                self.error = error

        # warning
        print('NOTE: assumes a SINGLE dimension for the selected sim (functionality defined otherwise)')

        # validation
        if self._result is None:
            self.throw(66)

        if model_indices is None:
            model_indices = self.search(Config.CRITERIA, 'indices', 'model')

        if model_labels is None:
            model_labels = ['Model {}'.format(i) for i in model_indices]

        if sim_index is None:
            sim_index = self.search(Config.CRITERIA, 'indices', 'sim')[0]

        if not len(model_labels) == len(model_indices):
            self.throw(67)

        # more metadata
        sample_indices = [sample_result['index'] for sample_result in self._result['samples']]
        comparison_key: str = self.get_object(Object.SIMULATION, [sample_indices[0], model_indices[0], sim_index]).factors.keys()[0]

        # summary of functionality
        print('For samples {}, comparing sim {} of models {} along dimension \"{}\"'.format(
            sample_indices,
            sim_index,
            model_indices,
            comparison_key)
        )

        # loop samples
        sample_results: dict
        for sample_results in self._result.get('samples', []):
            sample_index = sample_results['index']
            sample_object: Sample = self.get_object(Object.SAMPLE, [sample_index])
            sample_config: dict = self.get_config(Config.SAMPLE, [sample_index])
            slide: Slide = sample_object.slides[0]
            n_inners = sum(len(fasc.inners) for fasc in slide.fascicles)

            print('sample: {}'.format(sample_index))

            # init fig, ax
            fig: plt.Figure
            ax: plt.Axes
            fig, ax = plt.subplots()

            # x label
            xlabel = '->'.split(comparison_key)[-1]
            if xlabel == 'diameter':
                ax.set_xlabel('Axon Diameter (µm)')
            else:
                ax.set_xlabel(xlabel)
            # y label
            ax.set_ylabel('Activation Threshold (mA)')

            # init x group labels
            xlabels = []
            first_iteration: bool = True  # for appending to xlabels (only do this first time around)

            # init master data container (indices or outer list correspond to each model)
            sample_data: List[List[DataPoint]] = []

            # loop models
            model_results: dict
            for model_results in sample_results.get('models', []):
                model_index = model_results['index']

                print('\tmodel: {}'.format(model_index))

                # init data container for this model
                model_data: List[DataPoint] = []

                # sim index is already set from input, so no need to loop
                sim_object = self.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

                # validate sim object
                if len(sim_object.factors) is not 1:
                    self.throw(68)
                if not sim_object.factors.keys()[0] == comparison_key:
                    self.throw(69)

                # whether the comparison key is for 'fiber' or 'wave', the nsims will always be in order!
                # this realization allows us to simply loop through the factors in sim.factors[key] and treat the
                # indices as if they were the nsim indices
                for nsim_index, nsim_value in enumerate(sim_object.factors[comparison_key]):

                    # this x group label
                    if first_iteration:
                        xlabels.append(nsim_value)

                    # default fiberset index to 0
                    fiberset_index: int = 0
                    if comparison_key.split('->')[0] == 'fiber':
                        fiberset_index = nsim_index  # if dimension is fibers, use correct fiberset

                    # fetch outer->inner->fiber and out->inner maps
                    out_in_fib, out_in = sim_object.fiberset_map_pairs[fiberset_index]

                    # build base dirs for fetching thresholds
                    sim_dir = self.build_path(Object.SIMULATION,
                                              [sample_index, model_index, sim_index],
                                              just_directory=True)
                    n_sim_dir = os.path.join(sim_dir, 'n_sims', str(nsim_index))

                    # init thresholds for this model, sim, nsim
                    thresholds: List[float] = []

                    for inner in range(n_inners):
                        outer = [index for index, inners in enumerate(out_in) if inner in inners][0]
                        for local_fiber_index, _ in enumerate(out_in_fib[outer][out_in[outer].index(inner)]):
                            thresh_path = os.path.join(n_sim_dir,
                                                       'data',
                                                       'outputs',
                                                       'thresh_inner{}_fiber{}.dat'.format(inner, local_fiber_index))
                            thresholds.append(np.loadtxt(thresh_path)[2])

                    thresholds: np.ndarray = np.array(thresholds)

                    model_data.append(DataPoint(np.mean(thresholds), np.std(thresholds, ddof=1)))

                sample_data.append(model_data)

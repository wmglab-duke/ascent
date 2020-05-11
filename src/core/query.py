import os
import pickle
import re
from typing import Union, List, Tuple

import numpy as np
import matplotlib.colorbar as cbar
import matplotlib.colors as mplcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as tick

from core import FiberSet
from src.core import Sample, Simulation, Slide
from src.utils import Exceptionable, Configurable, Saveable, SetupMode, Config, Object, FiberXYMode


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
                 reverse_colormap: bool = True,
                 rows_override: int = None,
                 colorbar_aspect: int =None,
                 title_toggle: bool = True,
                 colomap_bounds_override: List[List[Tuple[float, float]]] = None,
                 track_colormap_bounds: bool = False,
                 subplot_title_toggle: bool = True):
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

        if track_colormap_bounds:
            print('WARNING: track_colormap_bounds assumes \n'
                  '\t1) single or first sim and\n'
                  '\t2) nsims are in order, starting from 0')

        if self._result is None:
            self.throw(66)


        # loop samples
        sample_results: dict
        for num_sam, sample_results in enumerate(self._result.get('samples', [])):
            sample_index = sample_results['index']
            sample_object: Sample = self.get_object(Object.SAMPLE, [sample_index])
            sample_config: dict = self.get_config(Config.SAMPLE, [sample_index])
            slide = sample_object.slides[0]
            n_inners = sum(len(fasc.inners) for fasc in slide.fascicles)

            # init colormap bounds tracking
            tracking_sim_index = None
            colormap_bounds_tracking: List[Tuple[float, float]] = []

            # offset for consecutive samples with colormap bounds override


            print('sample: {}'.format(sample_index))

            # loop models
            model_results: dict
            for model_results in sample_results.get('models', []):
                model_index = model_results['index']

                print('\tmodel: {}'.format(model_index))

                # calculate orientation point location (i.e., contact location)
                orientation_point = None
                if slide.orientation_point_index is not None:
                    r = slide.nerve.mean_radius() * 1.15  # scale up so orientation point is outside nerve
                    theta = np.arctan2(*tuple(np.flip(slide.nerve.points[slide.orientation_point_index][:2])))
                    theta += np.deg2rad(
                        self.get_config(Config.MODEL, [sample_index, model_index]).get('cuff').get('rotate').get(
                            'add_ang')
                    )
                    orientation_point = r * np.cos(theta), r * np.sin(theta)

                # loop sims
                for sim_index in model_results.get('sims', []):
                    sim_object = self.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

                    # update tracking colormap bounds
                    if track_colormap_bounds:

                        if tracking_sim_index is None:
                            tracking_sim_index = sim_index

                        if sim_index == tracking_sim_index:
                            if len(colormap_bounds_tracking) == 0:
                                colormap_bounds_tracking = [(1e10, 0)] * len(sim_object.master_product_indices)

                    print('\t\tsim: {}'.format(sim_index))

                    # init figure with subplots
                    master_product_count = len(sim_object.master_product_indices)
                    rows = int(np.floor(np.sqrt(master_product_count))) if rows_override is None else rows_override
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

                        # update tracking colormap bounds
                        if track_colormap_bounds and sim_index == tracking_sim_index:
                            colormap_bounds_tracking[n] = (
                                min(colormap_bounds_tracking[n][0], min_thresh),
                                max(colormap_bounds_tracking[n][1], max_thresh)
                            )

                            # override colormap bounds
                        if colomap_bounds_override is not None:
                            assert len(colomap_bounds_override[num_sam]) - 1 >= n, 'Not enough colormap bounds tuples provided!'
                            min_thresh, max_thresh = colomap_bounds_override[num_sam][n]

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

                        if subplot_title_toggle:
                            ax.set_title(title)

                        # plot orientation point if applicable
                        if orientation_point is not None:
                            # ax.plot(*tuple(slide.nerve.points[slide.orientation_point_index][:2]), 'b*')
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
                            aspect=colorbar_aspect if colorbar_aspect is not None else 20
                        )

                    # set super title
                    if title_toggle:
                        plt.suptitle(
                            'Activation thresholds: {} (model {})'.format(
                                sample_config.get('sample'),
                                model_index
                            ),
                            size='x-large'
                        )

                    # plt.tight_layout()

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

            if track_colormap_bounds:
                print('BOUNDS:\n[')
                for bounds in colormap_bounds_tracking:
                    print('\t{},'.format(bounds))
                print(']')



        return plt.gcf()

    def barcharts_compare_models(self,
                                 sim_index: int = None,
                                 model_indices: List[int] = None,
                                 model_labels: List[str] = None,
                                 title: str = 'Activation Thresholds',
                                 plot: bool = True,
                                 save_path: str = None,
                                 width: float = 0.8,
                                 capsize: float = 5,
                                 fascicle_filter_indices: List[int] = None,
                                 logscale: bool = False):
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
        comparison_key: str = \
            list(self.get_object(Object.SIMULATION, [sample_indices[0], model_indices[0], sim_index]).factors.keys())[0]

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
            xlabel = comparison_key.split('->')[-1]
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
                if not list(sim_object.factors.keys())[0] == comparison_key:
                    self.throw(69)

                # whether the comparison key is for 'fiber' or 'wave', the nsims will always be in order!
                # this realization allows us to simply loop through the factors in sim.factors[key] and treat the
                # indices as if they were the nsim indices
                for nsim_index, nsim_value in enumerate(sim_object.factors[comparison_key]):

                    # this x group label
                    if first_iteration:
                        # print(nsim_value)
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

                    # init thresholds container for this model, sim, nsim
                    thresholds: List[float] = []

                    # fetch all thresholds
                    for inner in range(n_inners):

                        outer = [index for index, inners in enumerate(out_in) if inner in inners][0]

                        if (fascicle_filter_indices is not None) and (outer not in fascicle_filter_indices):
                            continue

                        for local_fiber_index, _ in enumerate(out_in_fib[outer][out_in[outer].index(inner)]):
                            thresh_path = os.path.join(n_sim_dir,
                                                       'data',
                                                       'outputs',
                                                       'thresh_inner{}_fiber{}.dat'.format(inner, local_fiber_index))
                            thresholds.append(np.loadtxt(thresh_path)[2])

                    thresholds: np.ndarray = np.array(thresholds)

                    model_data.append(
                        DataPoint(np.mean(thresholds), np.std(thresholds, ddof=1) if len(thresholds) > 1 else None))

                first_iteration = False

                sample_data.append(model_data)

            # make the bars
            x_vals = np.arange(len(sample_data[0]))
            n_models = len(sample_data)
            effective_width = width / n_models

            for model_index, model_data in enumerate(sample_data):
                errors = [data.error for data in model_data]
                errors_valid = all([data.error is not None for data in model_data])
                ax.bar(
                    x=x_vals - ((n_models - 1) * effective_width / 2) + (effective_width * model_index),
                    height=[data.value for data in model_data],
                    width=effective_width,
                    label=model_labels[model_index],
                    yerr=errors if errors_valid else None,
                    capsize=capsize
                )

            # add x-axis values
            ax.set_xticks(x_vals)
            ax.set_xticklabels(xlabels)

            # set log scale
            if logscale:
                ax.set_yscale('log')

            # title
            title = '{} for sample {}'.format(title, sample_config['sample'])
            if fascicle_filter_indices is not None:
                if len(fascicle_filter_indices) == 1:
                    title = '{} (fascicle {})'.format(title, fascicle_filter_indices[0])
                else:
                    title = '{} (fascicles {})'.format(title, ', '.join([str(i) for i in fascicle_filter_indices]))
            plt.title(title)

            # add legend
            plt.legend()

            # plot!
            if plot:
                plt.show()

        def barcharts_compare_models(self,
                                     sim_index: int = None,
                                     model_indices: List[int] = None,
                                     model_labels: List[str] = None,
                                     title: str = 'Activation Thresholds',
                                     plot: bool = True,
                                     save_path: str = None,
                                     width: float = 0.8,
                                     capsize: float = 5,
                                     fascicle_filter_indices: List[int] = None,
                                     logscale: bool = False):
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
        comparison_key: str = \
            list(self.get_object(Object.SIMULATION, [sample_indices[0], model_indices[0], sim_index]).factors.keys())[0]

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
            xlabel = comparison_key.split('->')[-1]
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
                if not list(sim_object.factors.keys())[0] == comparison_key:
                    self.throw(69)

                # whether the comparison key is for 'fiber' or 'wave', the nsims will always be in order!
                # this realization allows us to simply loop through the factors in sim.factors[key] and treat the
                # indices as if they were the nsim indices
                for nsim_index, nsim_value in enumerate(sim_object.factors[comparison_key]):

                    # this x group label
                    if first_iteration:
                        # print(nsim_value)
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

                    # init thresholds container for this model, sim, nsim
                    thresholds: List[float] = []

                    # fetch all thresholds
                    for inner in range(n_inners):

                        outer = [index for index, inners in enumerate(out_in) if inner in inners][0]

                        if (fascicle_filter_indices is not None) and (outer not in fascicle_filter_indices):
                            continue

                        for local_fiber_index, _ in enumerate(out_in_fib[outer][out_in[outer].index(inner)]):
                            thresh_path = os.path.join(n_sim_dir,
                                                       'data',
                                                       'outputs',
                                                       'thresh_inner{}_fiber{}.dat'.format(inner, local_fiber_index))
                            thresholds.append(np.loadtxt(thresh_path)[2])

                    thresholds: np.ndarray = np.array(thresholds)

                    model_data.append(
                        DataPoint(np.mean(thresholds), np.std(thresholds, ddof=1) if len(thresholds) > 1 else None))

                first_iteration = False

                sample_data.append(model_data)

            # make the bars
            x_vals = np.arange(len(sample_data[0]))
            n_models = len(sample_data)
            effective_width = width / n_models

            for model_index, model_data in enumerate(sample_data):
                errors = [data.error for data in model_data]
                errors_valid = all([data.error is not None for data in model_data])
                ax.bar(
                    x=x_vals - ((n_models - 1) * effective_width / 2) + (effective_width * model_index),
                    height=[data.value for data in model_data],
                    width=effective_width,
                    label=model_labels[model_index],
                    yerr=errors if errors_valid else None,
                    capsize=capsize
                )

            # add x-axis values
            ax.set_xticks(x_vals)
            ax.set_xticklabels(xlabels)

            # set log scale
            if logscale:
                ax.set_yscale('log')

            # title
            title = '{} for sample {}'.format(title, sample_config['sample'])
            if fascicle_filter_indices is not None:
                if len(fascicle_filter_indices) == 1:
                    title = '{} (fascicle {})'.format(title, fascicle_filter_indices[0])
                else:
                    title = '{} (fascicles {})'.format(title, ', '.join([str(i) for i in fascicle_filter_indices]))
            plt.title(title)

            # add legend
            plt.legend()

            # plot!
            if plot:
                plt.show()

    def barcharts_compare_samples_2(self,
                                    sim_index: int = None,
                                    sample_indices: int = None,
                                    model_indices: List[int] = None,
                                    sample_labels: List[str] = None,
                                    model_labels: List[str] = None,
                                    title: str = 'Activation Thresholds',
                                    ylabel: str = 'Activation Threshold (mA)',
                                    xlabel_override: str = None,
                                    plot: bool = True,
                                    save_path: str = None,
                                    width: float = 0.8,
                                    capsize: float = 5,
                                    fascicle_filter_indices: List[int] = None,
                                    logscale: bool = False,
                                    calculation: str = 'mean',
                                    merge_bars: bool = False):
        """

        :param calculation: 'mean', 'i##'
        :param sim_index:
        :param nsim_indices:
        :param plot:
        :param save_path:
        :return:
        """

        def get_ratio_value(percent: float, values: np.ndarray):
            index: int = int(np.floor(percent * len(values)))
            value = np.sort(values)[index]
            return value

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
            # default to first model results
            print('Defaulting to model indices from first sample results.')
            model_indices = [model.get('index') for model in self._result.get('samples')[0].get('models')]

        if sample_indices is None:
            sample_indices = [sample_result['index'] for sample_result in self._result['samples']]

        if sample_labels is None:
            sample_labels = ['Model {}'.format(i) for i in sample_indices]

        if sim_index is None:
            sim_index = self.search(Config.CRITERIA, 'indices', 'sim')[0]

        if not len(sample_labels) == len(sample_indices):
            self.throw(70)

        comparison_key: str = \
            list(self.get_object(Object.SIMULATION, [sample_indices[0], model_indices[0], sim_index]).factors.keys())[0]

        # summary of functionality
        print('For models {}, comparing samples {} with sim {} along dimension \"{}\"'.format(
            model_indices,
            sample_indices,
            sim_index,
            comparison_key)
        )

        # loop models
        model_results: dict
        for model_index in model_indices:
            # model_index = model_results['index']

            print('model: {}'.format(model_index))

            # init fig, ax
            fig: plt.Figure
            ax: plt.Axes
            fig, ax = plt.subplots()

            # x label (with override if applicable)
            xlabel = comparison_key.split('->')[-1]
            if xlabel == 'diameter':
                ax.set_xlabel('Axon Diameter (µm)')
            else:
                ax.set_xlabel(xlabel)
            ax.set_xlabel(ax.get_xlabel() if xlabel_override is None else xlabel_override)

            # y label
            ax.set_ylabel(ylabel)

            # init x group labels
            xlabels = []
            first_iteration: bool = True  # for appending to xlabels (only do this first time around)

            # init master data container (indices or outer list correspond to each model)
            model_data: List[List[DataPoint]] = []

            # loop samples
            sample_results: dict
            for sample_results in self._result.get('samples', []):
                sample_index = sample_results['index']
                sample_object: Sample = self.get_object(Object.SAMPLE, [sample_index])
                sample_config: dict = self.get_config(Config.SAMPLE, [sample_index])
                slide: Slide = sample_object.slides[0]
                n_inners = sum(len(fasc.inners) for fasc in slide.fascicles)

                print('\tsample: {}'.format(sample_index))

                # init data container for this model
                sample_data: List[DataPoint] = []

                # sim index is already set from input, so no need to loop
                sim_object = self.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

                # validate sim object
                if len(sim_object.factors) is not 1:
                    self.throw(68)
                if not list(sim_object.factors.keys())[0] == comparison_key:
                    self.throw(69)

                # whether the comparison key is for 'fiber' or 'wave', the nsims will always be in order!
                # this realization allows us to simply loop through the factors in sim.factors[key] and treat the
                # indices as if they were the nsim indices
                for nsim_index, nsim_value in enumerate(sim_object.factors[comparison_key]):

                    print('\t\tnsim: {}'.format(nsim_index))

                    # this x group label
                    if first_iteration:
                        # print(nsim_value)
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

                    # init thresholds container for this model, sim, nsim
                    thresholds: List[float] = []

                    # fetch all thresholds
                    xy_mode_name: str = sim_object.search(Config.SIM, 'fibers', 'xy_parameters', 'mode')
                    xy_mode: FiberXYMode = [mode for mode in FiberXYMode if str(mode).split('.')[-1] == xy_mode_name][0]
                    if not xy_mode == FiberXYMode.SL_PSEUDO_INTERP:

                        for inner in range(n_inners):

                            outer = [index for index, inners in enumerate(out_in) if inner in inners][0]

                            if (fascicle_filter_indices is not None) and (outer not in fascicle_filter_indices):
                                continue

                            for local_fiber_index, _ in enumerate(out_in_fib[outer][out_in[outer].index(inner)]):
                                thresh_path = os.path.join(n_sim_dir,
                                                           'data',
                                                           'outputs',
                                                           'thresh_inner{}_fiber{}.dat'.format(inner,
                                                                                               local_fiber_index))
                                thresholds.append(np.loadtxt(thresh_path)[2])
                    else:
                        thresholds.append(np.loadtxt(os.path.join(n_sim_dir,
                                                                  'data',
                                                                  'outputs',
                                                                  'thresh_inner0_fiber0.dat'))[2])

                    thresholds: np.ndarray = np.array(thresholds)

                    data = None
                    if calculation == 'mean':
                        data = DataPoint(np.mean(thresholds),
                                         np.std(thresholds, ddof=1) if len(thresholds) > 1 else None)
                    elif re.match('i[0-9]+', calculation):
                        ratio = int(calculation.split('i')[1]) / 100.0
                        data = DataPoint(get_ratio_value(ratio, thresholds), None)

                    assert data is not None, 'Illegal calculation option: {}'.format(calculation)

                    sample_data.append(data)

                first_iteration = False

                model_data.append(sample_data)

            # make the bar groups
            x_vals = np.arange(len(model_data[0]))
            n_samples = len(model_data)
            effective_width = width / n_samples

            if not merge_bars:

                for sample_index, sample_data in enumerate(model_data):
                    errors = [data.error for data in sample_data]
                    errors_valid = all([data.error is not None for data in sample_data])
                    ax.bar(
                        x=x_vals - ((n_samples - 1) * effective_width / 2) + (effective_width * sample_index),
                        height=[data.value for data in sample_data],
                        width=effective_width,
                        label=sample_labels[sample_index],
                        yerr=errors if errors_valid else None,
                        capsize=capsize
                    )
            else:

                nsim_values = self.get_object(Object.SIMULATION, [sample_indices[0],
                                                                  model_index,
                                                                  sim_index]).factors[comparison_key]
                for n in range(len(nsim_values)):
                    values = np.array([sample_data[n].value for sample_data in model_data])
                    ax.bar(
                        x=x_vals[n],
                        height=np.mean(values),
                        width=width,
                        # label=,
                        yerr=np.std(values, ddof=1) if len(values) > 1 else None,
                        capsize=capsize,
                    )

                # set all same color
                facecolor = ax.patches[0].get_facecolor()
                for patch in ax.patches[1:]:
                    patch.set_facecolor(facecolor)

            # add x-axis values
            ax.set_xticks(x_vals)
            ax.set_xticklabels(xlabels)

            for rect in ax.patches:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() / 2, height + ax.get_ylim()[1] / 100, str(round(height, 2)),
                        ha='center', va='bottom')

            # set log scale
            if logscale:
                ax.set_yscale('log')

            # title
            model_name = model_labels[model_index] if model_labels is not None else str(model_index)
            title = '{} for model {}'.format(title, model_name)
            if fascicle_filter_indices is not None:
                if len(fascicle_filter_indices) == 1:
                    title = '{} (fascicle {})'.format(title, fascicle_filter_indices[0])
                else:
                    title = '{} (fascicles {})'.format(title, ', '.join([str(i) for i in fascicle_filter_indices]))
            plt.title(title)

            # add legend
            plt.legend()

            plt.tight_layout()

            # plot!
            if plot:
                plt.show()

            # save figure as png
            if save_path is not None:
                plt.savefig(
                    '{}{}{}_{}_{}.png'.format(
                        save_path, os.sep, '-'.join([str(s) for s in sample_indices]), model_index, sim_index
                    ), dpi=400
                )

    def barcharts_compare_samples(self,
                                  sim_index: int = None,
                                  model_indices: List[int] = None,
                                  model_labels: List[str] = None,
                                  title: str = 'Activation Thresholds',
                                  plot: bool = True,
                                  save_path: str = None,
                                  width: float = 0.8,
                                  capsize: float = 5,
                                  fascicle_filter_indices: List[int] = None,
                                  logscale: bool = False):
        """

        :param nsim_indices:
        :param plot:
        :param save_path:
        :return:
        ERIC WORKING HERE
        """

        def get_percent_response_threshold_value(percent: float, values: np.ndarray):
            index: int = int(np.floor(percent * len(values)))
            value = np.sort(values)[index]
            return value

        # quick helper class for storing data values
        class DataPoint():
            def __init__(self, value: float, error: float = None):
                self.value = value
                self.error = error

        class ResponseDataPoint():
            def __init__(self, vector: np.ndarray):
                self.i20: float = get_percent_response_threshold_value(0.2, vector)
                self.i50: float = get_percent_response_threshold_value(0.5, vector)
                self.i80: float = get_percent_response_threshold_value(0.8, vector)
                self.i100: float = np.max(vector)

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
        comparison_key: str = \
            list(self.get_object(Object.SIMULATION, [sample_indices[0], model_indices[0], sim_index]).factors.keys())[0]

        # summary of functionality
        print('For samples {}, comparing sim {} of models {} along dimension \"{}\"'.format(
            sample_indices,
            sim_index,
            model_indices,
            comparison_key)
        )

        # loop models
        model_index: int
        model_results: dict

        master_data: List[List[List[ResponseDataPoint]]] = []
        # init data container for this model

        for model_index in model_indices:
            print('\tmodel: {}'.format(model_index))
            model_data: List[List[ResponseDataPoint]] = []
            sample_results: dict

            # loop samples
            for sample_results in self._result.get('samples', []):
                sample_index = sample_results['index']
                print('sample: {}'.format(sample_index))

                # init master data container (indices or outer list correspond to each model)
                sample_data: List[ResponseDataPoint] = []

                sample_object: Sample = self.get_object(Object.SAMPLE, [sample_index])
                sample_config: dict = self.get_config(Config.SAMPLE, [sample_index])
                slide: Slide = sample_object.slides[0]
                n_inners = sum(len(fasc.inners) for fasc in slide.fascicles)

                # sim index is already set from input, so no need to loop
                sim_object = self.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

                # validate sim object
                if len(sim_object.factors) is not 1:
                    self.throw(68)
                if not list(sim_object.factors.keys())[0] == comparison_key:
                    self.throw(69)

                # whether the comparison key is for 'fiber' or 'wave', the nsims will always be in order!
                # this realization allows us to simply loop through the factors in sim.factors[key] and treat the
                # indices as if they were the nsim indices
                for nsim_index, nsim_value in enumerate(sim_object.factors[comparison_key]):

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

                    # init thresholds container for this model, sim, nsim
                    thresholds: List[float] = []

                    # fetch all thresholds
                    for inner in range(n_inners):

                        outer = [index for index, inners in enumerate(out_in) if inner in inners][0]

                        if (fascicle_filter_indices is not None) and (outer not in fascicle_filter_indices):
                            continue

                        for local_fiber_index, _ in enumerate(out_in_fib[outer][out_in[outer].index(inner)]):
                            thresh_path = os.path.join(n_sim_dir,
                                                       'data',
                                                       'outputs',
                                                       'thresh_inner{}_fiber{}.dat'.format(inner, local_fiber_index))
                            if os.path.exists(thresh_path):
                                thresholds.append(np.loadtxt(thresh_path)[2])

                    thresholds: np.ndarray = np.array(thresholds)
                    sample_data.append(ResponseDataPoint(thresholds if len(
                        thresholds) > 1 else None))  # TODO I will set std to none, calculate flag (20, 50, 80...
                model_data.append(sample_data)
            master_data.append(model_data)

            print('here')

            # # make the bars
            # x_vals = np.arange(len(sample_data[0]))
            # n_models = len(sample_data)
            # effective_width = width / n_models
            #
            # for model_index, model_data in enumerate(sample_data):  # todo for every sample in model
            #     errors = [data.error for data in model_data]
            #     errors_valid = all([data.error is not None for data in model_data])  # TODO keep this method but take mean and variance of those bars
            #     ax.bar(
            #         x=x_vals - ((n_models - 1) * effective_width / 2) + (effective_width * model_index),
            #         height=[data.value for data in model_data],
            #         width=effective_width,
            #         label=model_labels[model_index],
            #         yerr=errors if errors_valid else None,
            #         capsize=capsize
            #     )
            #
            # # add x-axis values
            # ax.set_xticks(x_vals)
            # ax.set_xticklabels(xlabels)
            #
            # # set log scale
            # if logscale:
            #     ax.set_yscale('log')
            #
            # # title
            # title = '{} for sample {}'.format(title, sample_config['sample'])
            # if fascicle_filter_indices is not None:
            #     if len(fascicle_filter_indices) == 1:
            #         title = '{} (fascicle {})'.format(title, fascicle_filter_indices[0])
            #     else:
            #         title = '{} (fascicles {})'.format(title, ', '.join([str(i) for i in fascicle_filter_indices]))
            # plt.title(title)
            #
            # # add legend
            # plt.legend()
            #
            # # plot!
            # if plot:
            #     plt.show()

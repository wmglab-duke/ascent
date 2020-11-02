import os
import pickle
import re
from typing import Union, List, Tuple

import numpy as np
import matplotlib.colorbar as cbar
import matplotlib.colors as mplcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
from scipy import stats as stats
import matplotlib.patches as mpatches
import pandas as pd

from src.core import Sample, Simulation, Slide, FiberSet
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
        if isinstance(sample_indices, int):
            sample_indices = [sample_indices]

        model_indices = self.search(Config.CRITERIA, 'indices', 'model')
        if isinstance(model_indices, int):
            model_indices = [model_indices]

        sim_indices = self.search(Config.CRITERIA, 'indices', 'sim')
        if isinstance(sim_indices, int):
            sim_indices = [sim_indices]

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
            if sample.startswith('.'):
                continue
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
                if model.startswith('.'):
                    continue
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
                    if sim.startswith('.'):
                        continue
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
            result = os.path.join('config', 'user', 'sims', '{}.json'.format(indices[0]))
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
                 save_path: str = None,
                 plot_outers: bool = False,
                 rows_override: int = None,
                 colorbar_mode: str = 'subplot',
                 colormap_str: str = 'coolwarm',
                 colorbar_text_size_override: int = None,
                 reverse_colormap: bool = True,
                 colorbar_aspect: int = None,
                 colomap_bounds_override: List[List[Tuple[float, float]]] = None,
                 track_colormap_bounds: bool = False,
                 track_colormap_bounds_offset_ratio: float = 0.0,
                 missing_color: Tuple[int, int, int, int] = (1, 0, 0, 1),
                 title_toggle: bool = True,
                 subplot_title_toggle: bool = True,
                 tick_count: int = 5,
                 tick_bounds: bool = False,
                 show_orientation_point: bool = True,
                 subplot_assign: str = 'standard',
                 min_max_ticks: bool = False):

        """
        Generate activation thresholds heatmaps
        
        Each plot represents a single 1-dimensional simulation, with each subplot representing a single value from the
        parameter that is being iterated over. For instace, a sim with many different fiber diamaters will have each subplot
        represent a single fiber diameter. In a future release, multidimensional sims will be accounted for; this may
        illicit changing the underlying data structure.

        Args:
            plot (bool, optional): Show plots via matplotlib. Defaults to True.
            plot_mode (str, optional): TODO
                'average': each inner is filled with the color corresponding to the average of its fiber thresholds
                'individual': each fiber is plotted individually with its corresponding color. 
                Defaults to 'average'.
            save_path (str, optional): Path to which plots are saved as PNG files. If None, will not save. Defaults to None.
            plot_outers (bool, optional): Draw outer perineurium trace. Defaults to False.
            rows_override (int, optional):
                Force number of rows; this number <= number of items in sim dimension (i.e., fiber diameters).
                If None, an arrangement closest to a square will be chosen. Defaults to None.
            colorbar_mode (str, optional): TODO
                'subplot': one colorbar/colormap per subplot (i.e., one colorbar for each nsim)
                'figure': one colorbar for the entire figure (i.e., all colors are on same scale).
                Defaults to 'subplot'.
            colormap_str (str, optional): Matplotlib colormap theme. Defaults to 'coolwarm'.
            colorbar_text_size_override (int, optional): Override system default for colorbar text size. Defaults to None.
            reverse_colormap (bool, optional): Invert direction of colormap. Defaults to True.
            colorbar_aspect (int, optional): Override system default for color aspect ratio. Defaults to None.
            colomap_bounds_override (List[List[Tuple[float, float]]], optional):
                List (an item per sim/figure), where each item is a list of tuples (bounds for each subplot).
                These bounds may be generated as output by toggling the `track_colormap_bounds` parameter.  Defaults to None.
            track_colormap_bounds (bool, optional): Output colormap bounds in format described above. Defaults to False.
            track_colormap_bounds_offset_ratio (float, optional):
                Step bound extremes towards mean by ratio. This can be helpful when a few fascicle have thresholds that
                are drastically different than the rest of the fascicles. Assumes sims are in order, starting from 0.
                Defaults to 0.0.
            missing_color (Tuple[int, int, int, int], optional): 
                RGBA Color to represent missing thresholds. Defaults to (1, 0, 0, 1) (red).
            title_toggle (bool, optional): Plot title. Defaults to True.
            subplot_title_toggle (bool, optional): Plot subplot title. Defaults to True.
            tick_count (int, optional): Colorbar tick count. Defaults to 2.
            tick_bounds (bool, optional): Ticks only at min and max of colorbar (override tick_count). Defaults to False.
            show_orientation_point (bool, optional):
                If an orientation mask was used, plot the direction as a dot outside of the nerve trace. Defaults to True.

        Returns:
            matplotlib.pyplot.Figure: Handle to final figure (uses .gcf())
            :param min_max_ticks:
            :param subplot_assign:
        """
        
        if self._result is None:
            self.throw(66)

        def _renumber_subplot(my_n: int, my_rows: int, my_cols: int):

            classic_indices = [[0 for x in range(my_cols)] for y in range(my_rows)]
            renumber_indices = [[0 for x in range(my_cols)] for y in range(my_rows)]

            if my_n == 0:
                new_n = 0
            else:
                ind = 0
                for row_ind in range(my_rows):
                    for col_ind in range(my_cols):
                        classic_indices[row_ind][col_ind] = ind
                        ind += 1

                ind = 0
                for col_ind in range(my_cols):
                    for row_ind in range(my_rows):
                        renumber_indices[row_ind][col_ind] = ind
                        ind += 1

                # find row
                for row_ind in range(my_rows):
                    if renumber_indices[row_ind].__contains__(my_n):
                        rw = row_ind
                        cl = renumber_indices[row_ind].index(my_n)
                        new_n = classic_indices[rw][cl]

            return new_n


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
                    #theta = np.arctan2(*tuple(np.flip(slide.nerve.points[slide.orientation_point_index][:2])))
                    theta = np.arctan2(*tuple(np.flip(slide.orientation_point)))
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
                    # figure, axes = plt.subplots(2, 5, constrained_layout=False, figsize=(25, 20))
                    figure, axes = plt.subplots(rows, cols, constrained_layout=False, figsize=(25, 20))
                    axes = axes.reshape(-1)

                    for ax in axes:
                        ax.axis('off')

                    # loop nsims
                    for n, (potentials_product_index, waveform_index) in enumerate(sim_object.master_product_indices):
                        active_src_index, fiberset_index = sim_object.potentials_product[potentials_product_index]

                        # fetch axis
                        ax: plt.Axes = axes[n if subplot_assign is "standard" else _renumber_subplot(n, 2, 5)]
                        ax.axis('off')

                        # fetch sim information
                        sim_dir = self.build_path(Object.SIMULATION, [sample_index, model_index, sim_index],
                                                  just_directory=True)
                        n_sim_dir = os.path.join(sim_dir, 'n_sims', str(n))
                        fiberset_dir = os.path.join(sim_dir, 'fibersets', str(fiberset_index))

                        # fetch thresholds, then find min and max
                        thresholds = []
                        missing_indices = []

                        if plot_mode is 'fiber0':
                            for i in range(n_inners):
                                thresh_path = os.path.join(n_sim_dir, 'data', 'outputs',
                                                           'thresh_inner{}_fiber0.dat'.format(i))
                                if os.path.exists(thresh_path):
                                    threshold = abs(np.loadtxt(thresh_path))
                                    if len(np.atleast_1d(threshold)) > 1:
                                        threshold = threshold[-1]
                                    if threshold > 20:
                                        missing_indices.append(i)
                                        print('TOO BIG: {}'.format(thresh_path))
                                    else:
                                        thresholds.append(threshold)
                                else:
                                    missing_indices.append(i)
                                    print('MISSING: {}'.format(thresh_path))
                        elif plot_mode is 'fibers':
                            for inner_ind in range(n_inners):
                                for fiber_ind in range(len(sim_object.fibersets[0].out_to_fib[inner_ind][0])):
                                    thresh_path = os.path.join(n_sim_dir, 'data', 'outputs',
                                                               'thresh_inner{}_fiber{}.dat'.format(
                                                                   inner_ind,
                                                                   fiber_ind
                                                               ))
                                    if os.path.exists(thresh_path):
                                        threshold = abs(np.loadtxt(thresh_path))
                                        if len(np.atleast_1d(threshold)) > 1:
                                            threshold = threshold[-1]
                                        thresholds.append(threshold)
                                    else:
                                        missing_indices.append((inner_ind, fiber_ind))
                                        print('MISSING: {}'.format(thresh_path))

                        max_thresh = np.max(thresholds)
                        min_thresh = np.min(thresholds)

                        # update tracking colormap bounds
                        if track_colormap_bounds and sim_index == tracking_sim_index:
                            colormap_bounds_tracking[n] = (
                                min(colormap_bounds_tracking[n][0], min_thresh * (1 + track_colormap_bounds_offset_ratio)),
                                max(colormap_bounds_tracking[n][1], max_thresh * (1 - track_colormap_bounds_offset_ratio))
                            )

                            # override colormap bounds
                        if colomap_bounds_override is not None:
                            # assert len(colomap_bounds_override[
                            #                num_sam]) - 1 >= n, 'Not enough colormap bounds tuples provided!'
                            # min_thresh, max_thresh = colomap_bounds_override[num_sam][n]
                            min_thresh, max_thresh = colomap_bounds_override[n]

                        # generate colors from colorbar and thresholds
                        cmap = plt.cm.get_cmap(colormap_str)

                        if reverse_colormap:
                            cmap = cmap.reversed()

                        colors = []
                        offset = 0
                        if plot_mode is 'fiber0':
                            for i in range(n_inners):
                                actual_i = i - offset
                                if i not in missing_indices:
                                    colors.append(tuple(cmap((thresholds[actual_i] - min_thresh) / (max_thresh - min_thresh))))
                                else:
                                    # NOTE: PLOTS MISSING VALUES AS RED
                                    offset += 1
                                    colors.append(missing_color)
                        elif plot_mode is 'fibers':
                            loop_fiber = 0
                            for inner_ind in range(n_inners):
                                actual_i = inner_ind - offset
                                for fiber_ind in range(len(sim_object.fibersets[0].out_to_fib[inner_ind][0])):
                                    if (inner_ind, fiber_ind) not in missing_indices:
                                        colors.append(tuple(cmap((thresholds[loop_fiber] - min_thresh) / (max_thresh - min_thresh))))
                                        loop_fiber += 1
                                    else:
                                        # NOTE: PLOTS MISSING VALUES AS RED
                                        offset += 1
                                        colors.append(missing_color)

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

                        # set title
                        if subplot_title_toggle:
                            ax.set_title(title, fontsize=10)

                        # plot orientation point if applicable
                        if orientation_point is not None and show_orientation_point is True:
                            # ax.plot(*tuple(slide.nerve.points[slide.orientation_point_index][:2]), 'b*')
                            ax.plot(*orientation_point, '.', markersize=20, color='grey')

                        if plot_mode is 'fiber0':
                            # plot slide (nerve and fascicles, defaulting to no outers)
                            sample_object.slides[0].plot(final=False, fix_aspect_ratio=True, fascicle_colors=colors,
                                                         ax=ax, outers_flag=plot_outers, inner_format='k-')
                        elif plot_mode is 'fibers':
                            sample_object.slides[0].plot(final=False, fix_aspect_ratio=True, ax=ax,
                                                         outers_flag=plot_outers, inner_format='k-')
                            sim_object.fibersets[0].plot(ax=ax, fiber_colors=colors, size=3)

                        # colorbar
                        cb_label = r'mA'
                        cb: cbar.Colorbar = plt.colorbar(
                            mappable=plt.cm.ScalarMappable(
                                cmap=cmap,
                                norm=mplcolors.Normalize(vmin=min_thresh, vmax=max_thresh)
                            ),
                            ticks=tick.MaxNLocator(nbins=tick_count) if not min_max_ticks else [min_thresh, max_thresh],
                            ax=ax,
                            orientation='vertical',
                            #label=cb_label,
                            aspect=colorbar_aspect if colorbar_aspect is not None else 20
                        )

                        cb.ax.set_yticklabels(['{:.2f}'.format(min_thresh), '{:.2f}'.format(max_thresh)])

                        # colorbar font size
                        if colorbar_text_size_override is not None:
                            # cb.set_label(cb_label, fontsize=colorbar_text_size_override)
                            cb.ax.tick_params(labelsize=colorbar_text_size_override)

                        # if tick_bounds:
                        #     cb.set_ticks([np.ceil(min_thresh * 100) / 100, np.floor(max_thresh * 100) / 100])

                    # set super title
                    if title_toggle:
                        plt.suptitle(
                            'Activation thresholds: {} (model {})'.format(
                                sample_config.get('sample'),
                                model_index
                            ),
                            size='x-large'
                        )

                    plt.tight_layout(pad=5.0)

                    # save figure as png
                    if save_path is not None:
                        if not os.path.exists(save_path):
                            os.mkdir(save_path)
                        dest = '{}{}{}_{}_{}.png'.format(save_path, os.sep, sample_index, model_index, sim_index)
                        figure.savefig(dest, dpi=200)
                        # print('done')

                    # plot figure
                    if plot:
                        plt.show()

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
                # ax.set_xlabel(xlabel)
                ax.set_xlabel('Pulse Width (\u03bcs)')
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
                        xlabels.append(int(nsim_value*1000))

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
                            threshold = np.loadtxt(thresh_path)
                            if threshold.size > 1:
                                threshold = threshold[-1]
                            thresholds.append(abs(threshold))

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
            # if fascicle_filter_indices is not None:
            #     if len(fascicle_filter_indices) == 1:
            #         title = '{} (fascicle {})'.format(title, fascicle_filter_indices[0])
            #     else:
            #         title = '{} (fascicles {})'.format(title, ', '.join([str(i) for i in fascicle_filter_indices]))

            title = 'Sensitivity of Thresholds to Unspecified Material Conductivities: 1 \u03bcm MRG Fiber'.format(title, sample_config['sample'])
            plt.title(title)

            for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                         ax.get_xticklabels() + ax.get_yticklabels()):
                item.set_fontsize(20)

            # add legend
            plt.legend(fontsize=16)

            # plot!
            if plot:
                plt.show()

        # def barcharts_compare_models(self,
        #                              sim_index: int = None,
        #                              model_indices: List[int] = None,
        #                              model_labels: List[str] = None,
        #                              title: str = 'Activation Thresholds',
        #                              plot: bool = True,
        #                              save_path: str = None,
        #                              width: float = 0.8,
        #                              capsize: float = 5,
        #                              fascicle_filter_indices: List[int] = None,
        #                              logscale: bool = False):
        #     """

        #     :param nsim_indices:
        #     :param plot:
        #     :param save_path:
        #     :return:
        #     """

        # # quick helper class for storing data values
        # class DataPoint():
        #     def __init__(self, value: float, error: float = None):
        #         self.value = value
        #         self.error = error

        # # warning
        # print('NOTE: assumes a SINGLE dimension for the selected sim (functionality defined otherwise)')

        # # validation
        # if self._result is None:
        #     self.throw(66)

        # if model_indices is None:
        #     model_indices = self.search(Config.CRITERIA, 'indices', 'model')

        # if model_labels is None:
        #     model_labels = ['Model {}'.format(i) for i in model_indices]

        # if sim_index is None:
        #     sim_index = self.search(Config.CRITERIA, 'indices', 'sim')[0]

        # if not len(model_labels) == len(model_indices):
        #     self.throw(67)

        # # more metadata
        # sample_indices = [sample_result['index'] for sample_result in self._result['samples']]
        # comparison_key: str = \
        #     list(self.get_object(Object.SIMULATION, [sample_indices[0], model_indices[0], sim_index]).factors.keys())[0]

        # # summary of functionality
        # print('For samples {}, comparing sim {} of models {} along dimension \"{}\"'.format(
        #     sample_indices,
        #     sim_index,
        #     model_indices,
        #     comparison_key)
        # )

        # # loop samples
        # sample_results: dict
        # for sample_results in self._result.get('samples', []):
        #     sample_index = sample_results['index']
        #     sample_object: Sample = self.get_object(Object.SAMPLE, [sample_index])
        #     sample_config: dict = self.get_config(Config.SAMPLE, [sample_index])
        #     slide: Slide = sample_object.slides[0]
        #     n_inners = sum(len(fasc.inners) for fasc in slide.fascicles)

        #     print('sample: {}'.format(sample_index))

        #     # init fig, ax
        #     fig: plt.Figure
        #     ax: plt.Axes
        #     fig, ax = plt.subplots()

        #     # x label
        #     xlabel = comparison_key.split('->')[-1]
        #     if xlabel == 'diameter':
        #         ax.set_xlabel('Axon Diameter (µm)')
        #     else:
        #         ax.set_xlabel(xlabel)
        #     # y label
        #     ax.set_ylabel('Activation Threshold (mA)')

        #     # init x group labels
        #     xlabels = []
        #     first_iteration: bool = True  # for appending to xlabels (only do this first time around)

        #     # init master data container (indices or outer list correspond to each model)
        #     sample_data: List[List[DataPoint]] = []

        #     # loop models
        #     model_results: dict
        #     for model_results in sample_results.get('models', []):
        #         model_index = model_results['index']

        #         print('\tmodel: {}'.format(model_index))

        #         # init data container for this model
        #         model_data: List[DataPoint] = []

        #         # sim index is already set from input, so no need to loop
        #         sim_object = self.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

        #         # validate sim object
        #         if len(sim_object.factors) is not 1:
        #             self.throw(68)
        #         if not list(sim_object.factors.keys())[0] == comparison_key:
        #             self.throw(69)

        #         # whether the comparison key is for 'fiber' or 'wave', the nsims will always be in order!
        #         # this realization allows us to simply loop through the factors in sim.factors[key] and treat the
        #         # indices as if they were the nsim indices
        #         for nsim_index, nsim_value in enumerate(sim_object.factors[comparison_key]):

        #             # this x group label
        #             if first_iteration:
        #                 # print(nsim_value)
        #                 xlabels.append(nsim_value)

        #             # default fiberset index to 0
        #             fiberset_index: int = 0
        #             if comparison_key.split('->')[0] == 'fiber':
        #                 fiberset_index = nsim_index  # if dimension is fibers, use correct fiberset

        #             # fetch outer->inner->fiber and out->inner maps
        #             out_in_fib, out_in = sim_object.fiberset_map_pairs[fiberset_index]

        #             # build base dirs for fetching thresholds
        #             sim_dir = self.build_path(Object.SIMULATION,
        #                                       [sample_index, model_index, sim_index],
        #                                       just_directory=True)
        #             n_sim_dir = os.path.join(sim_dir, 'n_sims', str(nsim_index))

        #             # init thresholds container for this model, sim, nsim
        #             thresholds: List[float] = []

        #             # fetch all thresholds
        #             for inner in range(n_inners):

        #                 outer = [index for index, inners in enumerate(out_in) if inner in inners][0]

        #                 if (fascicle_filter_indices is not None) and (outer not in fascicle_filter_indices):
        #                     continue

        #                 for local_fiber_index, _ in enumerate(out_in_fib[outer][out_in[outer].index(inner)]):
        #                     thresh_path = os.path.join(n_sim_dir,
        #                                                'data',
        #                                                'outputs',
        #                                                'thresh_inner{}_fiber{}.dat'.format(inner, local_fiber_index))
        #                     threshold = np.loadtxt(thresh_path)
        #                     if len(threshold) > 1:
        #                         threshold = threshold[-1]
        #                     thresholds.append(threshold)

        #             thresholds: np.ndarray = np.array(thresholds)

        #             model_data.append(
        #                 DataPoint(np.mean(thresholds), np.std(thresholds, ddof=1) if len(thresholds) > 1 else None))

        #         first_iteration = False

        #         sample_data.append(model_data)

        #     # make the bars
        #     x_vals = np.arange(len(sample_data[0]))
        #     n_models = len(sample_data)
        #     effective_width = width / n_models

        #     for model_index, model_data in enumerate(sample_data):
        #         errors = [data.error for data in model_data]
        #         errors_valid = all([data.error is not None for data in model_data])
        #         ax.bar(
        #             x=x_vals - ((n_models - 1) * effective_width / 2) + (effective_width * model_index),
        #             height=[data.value for data in model_data],
        #             width=effective_width,
        #             label=model_labels[model_index],
        #             yerr=errors if errors_valid else None,
        #             capsize=capsize
        #         )

        #     # add x-axis values
        #     ax.set_xticks(x_vals)
        #     ax.set_xticklabels(xlabels)

        #     # set log scale
        #     if logscale:
        #         ax.set_yscale('log')

        #     # title
        #     title = '{} for sample {}'.format(title, sample_config['sample'])
        #     if fascicle_filter_indices is not None:
        #         if len(fascicle_filter_indices) == 1:
        #             title = '{} (fascicle {})'.format(title, fascicle_filter_indices[0])
        #         else:
        #             title = '{} (fascicles {})'.format(title, ', '.join([str(i) for i in fascicle_filter_indices]))
        #     plt.title(title)

        #     # add legend
        #     plt.legend()

        #     # plot!
        #     if plot:
        #         plt.show()

    def barcharts_compare_samples(self,
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
                                  merge_bars: bool = False,
                                  label_bar_heights=None):
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

        if len(list(self.get_object(Object.SIMULATION,
                                    [sample_indices[0], model_indices[0], sim_index]).factors.keys())) > 0:
            comparison_key: str = list(self.get_object(Object.SIMULATION,
                                                       [sample_indices[0], model_indices[0], sim_index])
                                       .factors.keys())[0]
        else:
            comparison_key = 'fibers->z_parameters->diameter'

        # summary of functionality
        print('For models {}, comparing samples {} with sim {} along dimension \"{}\"'.format(
            model_indices,
            sample_indices,
            sim_index,
            comparison_key)
        )

        # loop models
        model_results: dict
        my_data = [[] for _ in model_indices]
        for model_index, model in enumerate(model_indices):
            # model_index = model_results['index']

            print('model: {}'.format(model))

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

                #patch - remove TODO
                if sample_index == 71 and model_index == 1:
                    model = model+1
                #patch - remove TODO
                if sample_index == 79 and model_index == 1:
                    model = model+1

                sample_object: Sample = self.get_object(Object.SAMPLE, [sample_index])
                sample_config: dict = self.get_config(Config.SAMPLE, [sample_index])
                slide: Slide = sample_object.slides[0]
                n_inners = sum(len(fasc.inners) for fasc in slide.fascicles)

                print('\tsample: {}'.format(sample_index))

                # init data container for this model
                sample_data: List[DataPoint] = []

                # sim index is already set from input, so no need to loop
                sim_object = self.get_object(Object.SIMULATION, [sample_index, model, sim_index])

                if not sim_object.factors:
                    sim_object.factors: dict = {comparison_key: [
                        sim_object.configs['sims']['fibers']['z_parameters']['diameter']]}  # comparison_key, [0.8]

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
                                              [sample_index, model, sim_index],
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
                                # if exist, else print
                                if os.path.exists(thresh_path):
                                    threshold = np.loadtxt(thresh_path)
                                    if len(np.atleast_1d(threshold)) > 1:
                                        threshold = threshold[-1]
                                    thresholds.append(threshold)
                                else:
                                    print(thresh_path)
                    else:
                        thresholds.append(np.loadtxt(os.path.join(n_sim_dir,
                                                                  'data',
                                                                  'outputs',
                                                                  'thresh_inner0_fiber0.dat')))

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

                if not self.get_object(Object.SIMULATION, [sample_indices[0],
                                                           model,
                                                           sim_index]).factors:
                    sim_object.factors: dict = {
                        comparison_key: [sim_object.configs['sims']['fibers']['z_parameters']['diameter']]}
                    nsim_values = [sim_object.configs['sims']['fibers']['z_parameters']['diameter']]

                else:
                    nsim_values = self.get_object(Object.SIMULATION, [sample_indices[0],
                                                                      model,
                                                                      sim_index]).factors[comparison_key]

                for n in range(len(nsim_values)):
                    my_data[model_index].append([])
                    values = np.array([sample_data[n].value for sample_data in model_data])

                    # index model, then index n_sim
                    my_data[model_index][n] = stats.variation(values)

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

            # label bar heights
            if label_bar_heights:
                for rect in ax.patches:
                    height = rect.get_height()
                    ax.text(rect.get_x() + rect.get_width() / 2, height + ax.get_ylim()[1] / 100, str(round(height, 2)),
                            ha='center', va='bottom')

            # set log scale
            if logscale:
                ax.set_yscale('log')

            # title
            model_name = model_labels[model_index] if model_labels is not None else str(model)
            title = '{} for {}'.format(title, model_name)
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
                        save_path, os.sep, '-'.join([str(s) for s in sample_indices]), model, sim_index
                    ), dpi=400
                )

        assert my_data is not None
        # make the bar groups
        x_vals = np.arange(len(my_data[0]))
        n_models = len(my_data)
        effective_width = width / n_models
        # init fig, ax
        fig: plt.Figure
        ax: plt.Axes
        fig, ax = plt.subplots()

        for model_index in range(len(my_data)):
            ax.bar(
                x=x_vals - ((n_models - 1) * effective_width / 2) + (effective_width * model_index),
                height=[data for data in my_data[model_index]],
                # width=effective_width,
                width=0.2,#effective_width,
                yerr=None,
                capsize=capsize
            )

        # x label (with override if applicable)
        xlabel = comparison_key.split('->')[-1]
        if xlabel == 'diameter':
            ax.set_xlabel('Axon Diameter (µm)')
        else:
            ax.set_xlabel(xlabel)
        ax.set_xlabel(ax.get_xlabel() if xlabel_override is None else xlabel_override)
        # my_ylabel: str = 'Coefficient of Variation'

        # y label
        # ax.set_ylabel(my_ylabel)

        # add x-axis values
        ax.set_xticks(x_vals)
        ax.set_xticklabels(xlabels)
        # add legend
        # blue_patch = mpatches.Patch(color=ax.patches[0].get_facecolor(), label='Purdue')
        # orange_patch = mpatches.Patch(color=ax.patches[1].get_facecolor(), label='MicroLeads')
        # green_patch = mpatches.Patch(color=ax.patches[2].get_facecolor(), label='CorTec')
        # plt.legend(handles=[blue_patch, orange_patch, green_patch])
        # plt.title('Rat Abdominal Cuff Comparison for Myelinated Fibers')
        # plt.title('Rat Abdominal Cuff Comparison for Unmyelinated Fibers')
        plt.show()

        return ax

    def excel_output(self,
                        filepath: str,
                        sample_keys: List[list] = [],
                        model_keys: List[list] = [],
                        sim_keys: List[list] = [],
                        individual_indices: bool = True,
                        config_paths: bool = True,
                        column_width: int = None,
                        console_output: bool = True):
        """Output summary of query.

        NOTE: for all key lists, the values themselves are lists, functioning as a JSON pointer.

        Args:
            filepath (str): output filepath
            sample_keys (list, optional): Sample keys to output. Defaults to [].
            model_keys (list, optional): Model keys to output. Defaults to [].
            sim_keys (list, optional): Sim keys to output. Defaults to [].
            individual_indices (bool, optional): Include column for each index. Defaults tp True.
            config_paths (bool, optional): Include column for each config path. Defaults to True.
            column_width (int, optional): Column width for Excel document. Defaults to None (system default).
            console_output (bool, optional): Print progress to console. Defaults to False.
        """

        sims: dict = {}

        # SAMPLE
        sample_results: dict
        for sample_results in self._result.get('samples', []):
            sample_index: int = sample_results['index']
            sample_config_path: str = self.build_path(Config.SAMPLE, [sample_index])
            sample_config: dict = self.load(sample_config_path)
            self.add(SetupMode.OLD, Config.SAMPLE, sample_config);
            
            if console_output:
                print('sample: {}'.format(sample_index))

            # MODEL
            model_results: dict
            for model_results in sample_results.get('models', []):
                model_index = model_results['index']
                model_config_path: str = self.build_path(Config.MODEL, [sample_index, model_index])
                model_config: dict = self.load(model_config_path)
                self.add(SetupMode.OLD, Config.MODEL, model_config);
                
                if console_output:
                    print('\tmodel: {}'.format(model_index))

                # SIM
                for sim_index in model_results.get('sims', []):
                    sim_config_path = self.build_path(Config.SIM, indices=[sim_index])
                    sim_config = self.load(sim_config_path)
                    self.add(SetupMode.OLD, Config.SIM, sim_config)
                    sim_object: Simulation = self.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])
                    sim_dir = self.build_path(Object.SIMULATION, [sample_index, model_index, sim_index], just_directory=True)
                    
                    if console_output:
                        print('\t\tsim: {}'.format(sim_index))
                    
                    # init sheet if necessary
                    if str(sim_index) not in sims.keys():
                        # base header
                        sample_parts = ['Sample Index', *['->'.join(['sample'] + key) for key in sample_keys]]
                        model_parts = ['Model Index', *['->'.join(['model'] + key) for key in model_keys]]
                        sim_parts = ['Sim Index', *['->'.join(['sim'] + key) for key in sim_keys]]
                        header = [
                            'Indices',
                            *(sample_parts if individual_indices else sample_parts[1:]),
                            *(model_parts if individual_indices else model_parts[1:]),
                            *(sim_parts if individual_indices else sim_parts[1:])
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
                            header += ['Sample Config Path', 'Model Config Path', 'Sim Config Path', 'NSim Path']
                        # set header as first row
                        sims[str(sim_index)] = [header]

                    # NSIM
                    for nsim_index, (potentials_product_index, waveform_index) in enumerate(sim_object.master_product_indices):
                        nsim_dir = os.path.join(sim_dir, 'n_sims', str(nsim_index))
                        # TODO: address active_src_index?
                        active_src_index, fiberset_index = sim_object.potentials_product[potentials_product_index]
                        # fetch additional sample, model, and sim values
                        # that's one juicy list comprehension right there
                        values = [[self.search(config, *key) for key in category] 
                                  for category, config in zip([sample_keys, model_keys, sim_keys], [Config.SAMPLE, Config.MODEL, Config.SIM])]
                        # base row data
                        sample_parts = [sample_index, *values[0]]
                        model_parts = [model_index, *values[1]]
                        sim_parts = [sim_index, *values[2]]
                        row = [
                            '{}_{}_{}_{}'.format(sample_index, model_index, sim_index, nsim_index),
                            *(sample_parts if individual_indices else sample_parts[1:]),
                            *(model_parts if individual_indices else model_parts[1:]),
                            *(sim_parts if individual_indices else sim_parts[1:])
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
                            row += [sample_config_path, model_config_path, sim_config_path, nsim_dir]
                        # add to sim sheet
                        sims[str(sim_index)].append(row)
        
                    # "prune" old configs
                    self.remove(Config.SIM)
                self.remove(Config.MODEL)
            self.remove(Config.SAMPLE)

        # build Excel file, with one sim per sheet
        writer = pd.ExcelWriter(filepath)
        for sim_index, sheet_data in sims.items():
            sheet_name = 'Sim {}'.format(sim_index)
            pd.DataFrame(sheet_data).to_excel(writer, sheet_name=sheet_name, header=False, index=False)
            if column_width is not None:
                writer.sheets[sheet_name].set_column(0, 256, column_width)
            else:
                writer.sheets[sheet_name].set_column(0, 256)

        writer.save()

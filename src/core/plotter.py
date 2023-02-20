"""Defines plotting functions used for analyzing data.

See ``examples/analysis`` for examples of how to use.
"""

import json
import os
import warnings
from typing import List

import matplotlib.colorbar as cbar
import matplotlib.colors as mplcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy as np
import pandas as pd

from src.core import Query
from src.utils import Config, Object


def heatmaps(
    *facetdata,
    data=None,
    ax=None,
    **kwargs,
):
    """Create heatmap for a single axis using the _HeatmapPlotter class.

    To create a single heatmap, call the class directly
    Use a Seaborn ``FacetGrid`` to create multiple heatmaps in one figure, using the ``FacetGrid.map()`` method.
    Note that data cannot be aggregated across n_sims
    (e.g., each call of ``heatmaps()`` must recieve only one threshold per fiber).

    :param facetdata: Recieves data from ``FacetGrid`` if using to plot an array.
    :param data: DataFrame to plot, used if manually passing data.
    :param ax: Axis to plot on.
    :param kwargs: Arguments to be passed to ``_HeatmapPlotter`` class constructor.
    :return: Plotting axis.
    """
    if data is None:
        data = pd.concat(facetdata, axis=1)
    # initialize heatmap plotter and pass in all arguments
    plotter = _HeatmapPlotter(data, **kwargs)
    if ax is None:
        ax = plt.gca()

    plotter.plot(ax)

    return ax


class _HeatmapPlotter:
    """Class used to contruct heatmap plots.

    This class should not be called directly by the user. Rather, the
    user should call the ``heatmaps()`` function, which will pass any
    keyword arguments to this class's constructor.
    """

    def __init__(
        self,
        data,
        mode: str = 'fibers',
        sample_object=None,
        sim_object=None,
        missing_color='red',
        suprathresh_color='blue',
        subthresh_color='green',
        cutoff_thresh=None,
        cmap=None,
        colorbar=True,
        min_max_ticks=False,
        cuff_orientation=False,
        plot_outers=False,
        cbar_kws=None,
        scatter_kws=None,
        line_kws=None,
        min_thresh=None,
        max_thresh=None,
        color=None,
    ):
        """Initialize heatmap plotter.

        :param data: DataFrame containing data to plot.
        :param mode: Plotting mode. There are multiple options:

            * ``'fibers'``: Plot a point for each fiber, using a heatmap of thresholds for color.
            * ``'fibers_on_off'``: Plot a point for each fiber. If the fiber threshold is above cutoff_thresh,
              suprathresh_color is used. Otherwise, subthresh_color is used.
            * ``'inners'``: Plot each inner as filled in, using a heatmap of thresholds for color.
              The mean threshold for that inner is used,
              thus if only one fiber is present per inner, that threshold is used.
            * ``'inners_on_off'``: Plot each inner as filled in. If the mean inner threshold is above cutoff_thresh,
              suprathresh_color is used. Otherwise, subthresh_color is used.

        :param sample_object: Sample object to use for plotting. Automatically loaded if not provided.
        :param sim_object: Simulation object to use for plotting. Automatically loaded if not provided.
        :param missing_color: Color to use for missing data.
        :param suprathresh_color: Color to use for suprathresh data.
        :param subthresh_color: Color to use for subthresh data.
        :param cutoff_thresh: Threshold to use for plotting on_off modes.
        :param cmap: Color map to override default.
        :param colorbar: Whether to add a colorbar.
        :param min_max_ticks: Whether to add only the minimum and maximum ticks to the colorbar.
        :param cuff_orientation: Whether to plot a point for the cuff orientation.
        :param plot_outers: Whether to plot the fascicle outers.
        :param cbar_kws: Keyword arguments to pass to matplotlib.colorbar.Colorbar.
        :param scatter_kws: Keyword arguments to pass to matplotlib.pyplot.scatter.
        :param line_kws: Keyword arguments to pass to matplotlib.pyplot.plot.
        :param min_thresh: Minimum threshold to use for plotting. Use this to override the default minimum.
        :param max_thresh: Maximum threshold to use for plotting. Use this to override the default maximum.
        :param color: Color passed in by seaborn when using FacetGrid. Not used.
        """
        # add variables to self from input args
        self.min_thresh = self.max_thresh = None
        self.mappable = None
        self.fiber_colors = self.inner_colors = None
        self.sample_index = self.sim_index = self.model_index = self.n_sim_index = None
        self.plot_outers = plot_outers
        self.cmap = cmap
        self.min_max_ticks = min_max_ticks
        self.colorbar = colorbar
        self.cutoff_thresh = cutoff_thresh
        self.missing_color = missing_color
        self.suprathresh_color = suprathresh_color
        self.subthresh_color = subthresh_color
        self.mode = mode
        self.sample = sample_object
        self.sim = sim_object
        self.color = color
        self.cbar_kws = cbar_kws if cbar_kws is not None else {}
        self.scatter_kws = scatter_kws if scatter_kws is not None else {}
        self.scatter_kws.setdefault('s', 100)
        self.line_kws = line_kws if line_kws is not None else {}
        self.max_thresh = max(data.threshold) if max_thresh is None else max_thresh
        self.min_thresh = min(data.threshold) if min_thresh is None else min_thresh
        self.cuff_orientation = cuff_orientation

        # run setup in preparation for plotting
        self.validate(data)
        self.get_objects()
        self.create_cmap()
        self.determine_colors(data)

    def plot(self, ax):
        """Make heatmap plot.

        :param ax: Axis to plot on.
        :return: Plotting axis.
        """
        self.set_ax(ax)

        if self.colorbar and self.mode != 'on_off':
            self.add_colorbar(ax)

        if self.cuff_orientation:
            self.plot_cuff_orientation(ax)

        self.plot_inners_fibers(ax)

        return ax

    def plot_inners_fibers(self, ax):
        """Plot inners and fibers using the colors determined in determine_colors().

        :param ax: axis to plot on
        """
        self.sample.slides[0].plot(
            final=False,
            fix_aspect_ratio=True,
            fascicle_colors=self.inner_colors,
            ax=ax,
            outers_flag=self.plot_outers,
            inner_format='k-',
            line_kws=self.line_kws,
        )
        if np.any([bool(x) for x in self.fiber_colors]):
            self.scatter_kws['c'] = self.fiber_colors
            self.sim.fibersets[0].plot(ax=ax, scatter_kws=self.scatter_kws)

    def create_cmap(self):
        """Create color map and mappable for assigning colorbar and ticks."""
        if self.cmap is None:
            cmap = plt.cm.get_cmap('viridis')
            cmap.set_bad(color='w')
            cmap = cmap.reversed()
            self.cmap = cmap
        mappable = plt.cm.ScalarMappable(
            cmap=self.cmap,
            norm=mplcolors.Normalize(vmin=self.min_thresh, vmax=self.max_thresh),
        )
        self.mappable = mappable

    def set_ax(self, ax):
        """Remove axis elements.

        :param ax: axis to plot on
        """
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel('')
        ax.set_ylabel('')

    def determine_colors(self, threshdf):
        """Determine colors for inners and fibers based on user selected mode.

        :param threshdf: DataFrame of thresholds.
        """

        def _mapthresh(thresh):
            return tuple(self.cmap((thresh - self.min_thresh) / (self.max_thresh - self.min_thresh)))

        inner_color_list = []
        fiber_color_list = []
        for inner in pd.unique(threshdf.inner):
            # get inner threshold and add the appropriate color to the list
            innerthresh = np.mean(threshdf.query(f'inner=={inner}').threshold)
            if innerthresh is np.nan:
                inner_color_list.append(self.missing_color)
                warnings.warn(
                    'Missing at least one fiber threshold, color will appear as missing color (defaults to red).',
                    stacklevel=2,
                )
            elif self.mode == 'inners':
                inner_color_list.append(_mapthresh(innerthresh))
            elif self.mode == 'inners_on_off':
                inner_color_list.append(
                    self.suprathresh_color if innerthresh > self.cutoff_thresh else self.subthresh_color
                )
            else:
                inner_color_list.append(None)
        for fiber_index in pd.unique(threshdf['index']):
            # get fiber threshold and add the appropriate color to the list
            fiberthresh = np.mean(threshdf.query(f'index=={fiber_index}').threshold)
            if fiberthresh is np.nan:
                warnings.warn(
                    'Missing fiber threshold, color will appear as missing color (defaults to red).', stacklevel=2
                )
                fiber_color_list.append(self.missing_color)
            elif self.mode == 'fibers':
                fiber_color_list.append(_mapthresh(fiberthresh))
            elif self.mode == 'fibers_on_off':
                fiber_color_list.append(
                    self.suprathresh_color if fiberthresh > self.cutoff_thresh else self.subthresh_color
                )
            else:
                fiber_color_list.append(None)
        # set colors for inners and fibers
        self.inner_colors, self.fiber_colors = inner_color_list, fiber_color_list

    def add_colorbar(self, ax):
        """Add colorbar to heatmap plot.

        :param ax: axis to plot on
        """
        # set default ticks if not provided
        if 'ticks' not in self.cbar_kws:
            self.cbar_kws['ticks'] = (
                tick.AutoLocator() if not self.min_max_ticks else [self.min_thresh, self.max_thresh]
            )
        # generate colorbar
        cb_label = r'mA'
        cb: cbar.Colorbar = plt.colorbar(mappable=self.mappable, ax=ax, **self.cbar_kws)
        cb.ax.set_title(cb_label)

    def get_objects(self):
        """Get sample and sim objects for plotting."""
        if self.sample is None:
            self.sample = Query.get_object(Object.SAMPLE, [self.sample_index])
        if self.sim is None:
            self.sim = Query.get_object(Object.SIMULATION, [self.sample_index, self.model_index, self.sim_index])

    def validate(self, data):
        """Check that data is valid for plotting.

        :param data: DataFrame of thresholds.
        """
        assert self.mode in ['fibers', 'inners', 'fibers_on_off', 'inners_on_off']
        if self.mode in ['fibers_on_off', 'inners_on_off']:
            assert self.cutoff_thresh is not None, 'Must provide cutoff threshold for on/off mode.'
        # make sure only one sample, model, sim, and nsim for this plot
        for index in ['sample', 'model', 'sim', 'nsim']:
            assert (
                len(pd.unique(data[index])) == 1
            ), f'Only one {index} allowed for this plot. Append something like q.threshold_data.query(\'{index}==0\')'
            setattr(self, index + '_index', pd.unique(data[index])[0])

    def plot_cuff_orientation(self, ax):
        """Plot the orientation of the cuff.

        :param ax: axis to plot on
        """
        # calculate orientation point location (i.e., contact location)
        # get radius of sample
        try:
            r = self.sample.slides[0].nerve.mean_radius()
        except AttributeError:
            r = self.sample.slides[0].fascicles[0].outer.mean_radius()
        # get orientation angle from slide
        theta = self.sample.slides[0].orientation_angle if self.sample.slides[0].orientation_angle is not None else 0
        # load add_ang from model.json cofiguration file
        with open(Query.build_path(Config.MODEL, [self.sample_index, self.model_index])) as f:
            model_config = json.load(f)
        # add any cuff rotation
        theta += np.deg2rad(model_config.get('cuff').get('rotate').get('add_ang'))
        ax.scatter(r * 1.2 * np.cos(theta), r * 1.2 * np.sin(theta), 300, 'red', 'o')


def ap_loctime(
    query_object: Query,
    n_sim_filter: List[int] = None,
    plot: bool = False,
    n_sim_label_override: str = None,
    model_labels: List[str] = None,
    save: bool = False,
    subplots=False,
    nodes_only=False,
    amp=0,
):
    """Plot time and location of action potential initiation.

    :param query_object: Query object to use for plotting.
    :param n_sim_filter: List of n_sim values to plot.
    :param plot: Whether to plot the data.
    :param n_sim_label_override: Label to use for n_sim.
    :param model_labels: Labels to use for models.
    :param save: Whether to save the plot.
    :param subplots: Whether to plot in subplots.
    :param nodes_only: Whether to plot only nodes.
    :param amp: Amplitude of action potential.
    """
    # loop samples
    for sample_index, sample_results in [(s['index'], s) for s in query_object._result.get('samples')]:
        print(f'sample: {sample_index}')

        # loop models
        for model_index, model_results in [(m['index'], m) for m in sample_results.get('models')]:
            print(f'\tmodel: {model_index}')

            # loop sims
            for sim_index in model_results.get('sims', []):
                print(f'\t\tsim: {sim_index}')

                sim_object = query_object.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

                if subplots is True:
                    fig, axs = plt.subplots(ncols=len(sim_object.master_product_indices), nrows=2, sharey="row")

                # loop nsims
                for n_sim_index, (potentials_product_index, _waveform_index) in enumerate(
                    sim_object.master_product_indices
                ):
                    print(f'\t\t\tnsim: {n_sim_index}')

                    active_src_index, fiberset_index = sim_object.potentials_product[potentials_product_index]

                    # skip if not in existing n_sim filter
                    if n_sim_filter is not None and n_sim_index not in n_sim_filter:
                        print('\t\t\t\t(skip)')
                        continue

                    # directory of data for this (sample, model, sim)
                    sim_dir = query_object.build_path(
                        Object.SIMULATION, [sample_index, model_index, sim_index], just_directory=True
                    )

                    # directory for specific n_sim
                    n_sim_dir = os.path.join(sim_dir, 'n_sims', str(n_sim_index))

                    # directory of fiberset (i.e., points and potentials) associated with this n_sim
                    fiberset_dir = os.path.join(sim_dir, 'fibersets', str(fiberset_index))

                    # the simulation outputs for this n_sim
                    outputs_path = os.path.join(n_sim_dir, 'data', 'outputs')

                    # path of the first inner, first fiber vm(t) data
                    vm_t_path = os.path.join(outputs_path, f'ap_loctime_inner0_fiber0_amp{amp}.dat')

                    # load vm(t) data (see path above)
                    # each row is a snapshot of the voltages at each node [mV]
                    # the first column is the time [ms]
                    # first row is holds column labels, so this is skipped (time, node0, node1, ...)
                    aploc_data = np.loadtxt(vm_t_path, skiprows=0)

                    aploc_data[np.where(aploc_data == 0)] = float('Inf')

                    time = min(aploc_data)

                    node = np.argmin(aploc_data)

                    # create message about AP time and location findings
                    message = f't: {time} ms, node: {node + 1} (of {len(aploc_data) + 2})'
                    if time != float('inf'):
                        print(f'\t\t\t\t{message}')
                    else:
                        print('No action potential occurred.')
                        continue

                    # plot the AP location with voltage trace
                    # create subplots
                    if plot or save:
                        if subplots is not True:
                            fig, axes = plt.subplots(1, 1)
                            axes = [axes]
                        else:
                            axes = [axs[0][n_sim_index], axs[1][n_sim_index]]
                        # load fiber coordinates
                        fiber = np.loadtxt(os.path.join(fiberset_dir, '0.dat'), skiprows=1)
                        nodefiber = fiber[0::11, :]

                        # plot fiber coordinates in 2D
                        if nodes_only is not True:
                            axes[0].plot(fiber[:, 0], fiber[:, 2], 'b.', label='fiber')
                        else:
                            axes[0].plot(nodefiber[:, 0], nodefiber[:, 2], 'b.', label='fiber')

                        # plot AP location
                        axes[0].plot(fiber[11 * node, 0], fiber[11 * node, 2], 'r*', markersize=10)

                        # location display settings
                        n_sim_label = (
                            f'n_sim: {n_sim_index}' if (n_sim_label_override is None) else n_sim_label_override
                        )
                        model_label = '' if (model_labels is None) else f', {model_labels[model_index]}'
                        axes[0].set_xlabel('x location, µm')

                        axes[0].set_title(f'{n_sim_label}{model_label}')
                        if subplots is not True:
                            axes[0].legend(['fiber', f'AP ({message})'])
                        else:
                            axes[0].legend(['fiber', 'AP'])

                        plt.tight_layout()

                        # voltages display settings
                        if subplots is not True or n_sim_index == 0:
                            axes[0].set_ylabel('z location, µm')
                        plt.tight_layout()

                    # display
                    if save:
                        plt.savefig(
                            f'out/analysis/ap_time_loc_{sample_index}_{model_index}_{sim_index}_{n_sim_index}.png',
                            dpi=300,
                        )

                    if plot:
                        plt.show()

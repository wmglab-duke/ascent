import os
from typing import List, Tuple

import matplotlib.colorbar as cbar
import matplotlib.colors as mplcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy as np

from src.core import Query, Sample
from src.utils import Config, Object


def heatmaps(
    query_object: Query,
    plot: bool = True,
    plot_mode: str = 'fibers',
    save_path: str = None,
    plot_outers: bool = False,
    rows_override: int = None,
    add_colorbar: bool = True,
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
    min_max_ticks: bool = False,
    cutoff_thresh: bool = 0,
    suprathresh_color: Tuple[int, int, int, int] = (0, 1, 0, 1),
    subthresh_color: Tuple[int, int, int, int] = (0, 0, 1, 1),
    select_fascicles: List = None,
    alltitle=True,
    microamps=False,
    suptitle_override=None,
    dotsize=10,
    cbar_label_func='title',  # 'title' or 'label'
):
    """
    Generate activation thresholds heatmaps

    Each plot represents a single 1-dimensional simulation,
    with each subplot representing a single value from the
    parameter that is being iterated over.
    For instace, a sim with many different fiber diamaters will have each subplot
    represent a single fiber diameter.
    In a future release, multidimensional sims will be accounted for; this may
    illicit changing the underlying data structure.

    Args:
        plot (bool, optional): Show plots via matplotlib. Defaults to True.
        plot_mode (str, optional):
            'average': each inner is filled with the color corresponding to the average of its fiber thresholds
            'individual': each fiber is plotted individually with its corresponding color.
            Defaults to 'average'.
        save_path (str, optional): Path to which plots are saved as PNG files.
            If None, will not save. Defaults to None.
        plot_outers (bool, optional): Draw outer perineurium trace. Defaults to False.
        rows_override (int, optional):
            Force number of rows; this number <= number of items in sim dimension (i.e., fiber diameters).
            If None, an arrangement closest to a square will be chosen. Defaults to None.
        colorbar_mode (str, optional):
            'subplot': one colorbar/colormap per subplot (i.e., one colorbar for each nsim)
            'figure': one colorbar for the entire figure (i.e., all colors are on same scale).
            Defaults to 'subplot'.
        colormap_str (str, optional): Matplotlib colormap theme. Defaults to 'coolwarm'.
        colorbar_text_size_override (int, optional): Override system default for colorbar text size.
            Defaults to None.
        reverse_colormap (bool, optional): Invert direction of colormap. Defaults to True.
        colorbar_aspect (int, optional): Override system default for color aspect ratio. Defaults to None.
        colomap_bounds_override (List[List[Tuple[float, float]]], optional):
            List (an item per sim/figure), where each item is a list of tuples (bounds for each subplot).
            These bounds may be generated as output by toggling the `track_colormap_bounds` parameter.
                Defaults to None.
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
        tick_bounds (bool, optional): Ticks only at min and max of colorbar (override tick_count).
            Defaults to False.
        show_orientation_point (bool, optional):
            If an orientation mask was used, plot the direction as a dot outside of the nerve trace.
                Defaults to True.
        :param subthresh_color:
        :param suprathresh_color:
        :param cutoff_thresh:
        :param show_orientation_point:
        :param tick_bounds:
        :param tick_count:
        :param subplot_title_toggle:
        :param title_toggle:
        :param missing_color:
        :param track_colormap_bounds_offset_ratio:
        :param track_colormap_bounds:
        :param colorbar_aspect:
        :param reverse_colormap:
        :param colorbar_text_size_override:
        :param colormap_str:
        :param colorbar_mode:
        :param plot_outers:
        :param rows_override:
        :param save_path:
        :param plot:
        :param add_colorbar:
        :param plot_mode:
        :param colomap_bounds_override:
        :param min_max_ticks:
        :param subplot_assign:

    Returns:
        matplotlib.pyplot.Figure: Handle to final figure (uses .gcf())
    """

    if query_object._result is None:
        query_object.throw(66)

    def _renumber_subplot(my_n: int, my_rows: int, my_cols: int):

        classic_indices = [[0 for x in range(my_cols)] for y in range(my_rows)]
        renumber_indices = [[0 for x in range(my_cols)] for y in range(my_rows)]
        new_n = 0

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
    for sample_results in query_object._result.get('samples', []):
        sample_index = sample_results['index']
        sample_object: Sample = query_object.get_object(Object.SAMPLE, [sample_index])
        sample_config: dict = query_object.get_config(Config.SAMPLE, [sample_index])
        slide = sample_object.slides[0]
        n_inners = sum(len(fasc.inners) for fasc in slide.fascicles)

        # init colormap bounds tracking
        tracking_sim_index = None
        colormap_bounds_tracking: List[Tuple[float, float]] = []

        # offset for consecutive samples with colormap bounds override

        print(f'sample: {sample_index}')

        # loop models
        model_results: dict
        for model_results in sample_results.get('models', []):
            model_index = model_results['index']

            print(f'\tmodel: {model_index}')

            # calculate orientation point location (i.e., contact location)
            orientation_point = None
            if slide.orientation_point is not None:
                r = slide.nerve.mean_radius() * 1.15  # scale up so orientation point is outside nerve
                theta = np.arctan2(*tuple(np.flip(slide.orientation_point)))
                theta += np.deg2rad(
                    query_object.get_config(Config.MODEL, [sample_index, model_index])
                    .get('cuff')
                    .get('rotate')
                    .get('add_ang')
                )
                orientation_point = r * np.cos(theta), r * np.sin(theta)

            # loop sims
            for sim_index in model_results.get('sims', []):
                sim_object = query_object.get_object(Object.SIMULATION, [sample_index, model_index, sim_index])

                # update tracking colormap bounds
                if track_colormap_bounds:

                    if tracking_sim_index is None:
                        tracking_sim_index = sim_index

                    if sim_index == tracking_sim_index and len(colormap_bounds_tracking) == 0:
                        colormap_bounds_tracking = [(1e10, 0)] * len(sim_object.master_product_indices)

                print(f'\t\tsim: {sim_index}')

                # init figure with subplots
                master_product_count = len(sim_object.master_product_indices)
                rows = int(np.floor(np.sqrt(master_product_count))) if rows_override is None else rows_override
                cols = int(np.ceil(master_product_count / rows))
                figure, axes = plt.subplots(rows, cols, constrained_layout=False, figsize=(25, 20))
                axes = np.array(axes)
                axes = axes.reshape(-1)

                # loop nsims
                for n, (potentials_product_index, waveform_index) in enumerate(sim_object.master_product_indices):
                    (
                        active_src_index,
                        fiberset_index,
                    ) = sim_object.potentials_product[potentials_product_index]

                    # fetch axis
                    ax: plt.Axes = axes[n if subplot_assign == "standard" else _renumber_subplot(n, 2, 5)]
                    # fetch sim information
                    sim_dir = query_object.build_path(
                        Object.SIMULATION,
                        [sample_index, model_index, sim_index],
                        just_directory=True,
                    )
                    n_sim_dir = os.path.join(sim_dir, 'n_sims', str(n))

                    # fetch thresholds, then find min and max
                    thresholds = []
                    missing_indices = []

                    if plot_mode == 'fiber0' or plot_mode == 'on_off':
                        if n_inners == 1:
                            query_object.throw(131)
                        for i in range(n_inners):
                            if select_fascicles is None or select_fascicles[i]:
                                thresh_path = os.path.join(
                                    n_sim_dir,
                                    'data',
                                    'outputs',
                                    f'thresh_inner{i}_fiber0.dat',
                                )
                                if os.path.exists(thresh_path):
                                    threshold = abs(np.loadtxt(thresh_path))
                                    if len(np.atleast_1d(threshold)) > 1:
                                        threshold = threshold[-1]
                                    if threshold > 500:
                                        missing_indices.append(i)
                                        print(f'TOO BIG: {thresh_path}')
                                    else:
                                        thresholds.append(threshold)
                                else:
                                    missing_indices.append(i)
                                    print(f'MISSING: {thresh_path}')
                            else:
                                thresholds.append(np.nan)

                    elif plot_mode == 'fibers':
                        for i in range(len(sim_object.fibersets[0].fibers)):
                            inner_ind, fiber_ind = sim_object.indices_fib_to_n(0, i)
                            if select_fascicles is None or select_fascicles[inner_ind]:
                                thresh_path = os.path.join(
                                    n_sim_dir,
                                    'data',
                                    'outputs',
                                    f'thresh_inner{inner_ind}_fiber{fiber_ind}.dat',
                                )
                                if os.path.exists(thresh_path):
                                    threshold = abs(np.loadtxt(thresh_path))
                                    if len(np.atleast_1d(threshold)) > 1:
                                        threshold = threshold[-1]
                                    thresholds.append(threshold)
                                else:
                                    missing_indices.append((inner_ind, fiber_ind))
                                    print(f'MISSING: {thresh_path}')
                            else:
                                for _ in range(len(sim_object.fibersets[0].out_to_fib[inner_ind][0])):
                                    thresholds.append(np.nan)
                    if microamps:
                        thresholds = [x * 1000 for x in thresholds]
                    max_thresh = np.nanmax(thresholds)
                    min_thresh = np.nanmin(thresholds)

                    # update tracking colormap bounds
                    if track_colormap_bounds and sim_index == tracking_sim_index:
                        colormap_bounds_tracking[n] = (
                            min(
                                colormap_bounds_tracking[n][0],
                                min_thresh * (1 + track_colormap_bounds_offset_ratio),
                            ),
                            max(
                                colormap_bounds_tracking[n][1],
                                max_thresh * (1 - track_colormap_bounds_offset_ratio),
                            ),
                        )

                    # override colormap bounds
                    if colomap_bounds_override is not None:
                        min_thresh, max_thresh = colomap_bounds_override[n]

                    # generate colors from colorbar and thresholds
                    cmap = plt.cm.get_cmap(colormap_str)
                    cmap.set_bad(color='w')

                    if reverse_colormap:
                        cmap = cmap.reversed()

                    colors = []
                    offset = 0
                    if plot_mode == 'fiber0':
                        for i in range(n_inners):
                            actual_i = i - offset
                            if i not in missing_indices:
                                if select_fascicles is not None and not select_fascicles[actual_i]:
                                    colors.append(cmap(np.nan))  # missing_color
                                else:
                                    mapped = (thresholds[actual_i] - min_thresh) / (max_thresh - min_thresh)
                                    colors.append(tuple(cmap(mapped)))

                            elif actual_i in missing_indices:
                                # NOTE: PLOTS MISSING VALUES AS RED
                                offset += 1
                                colors.append(missing_color)  # missing_color

                    elif plot_mode == 'fibers':
                        loop_fiber = 0
                        for i in range(len(sim_object.fibersets[0].fibers)):
                            inner_ind, fiber_ind = sim_object.indices_fib_to_n(0, i)
                            if (inner_ind, fiber_ind) not in missing_indices:
                                colors.append(
                                    tuple(cmap((thresholds[loop_fiber] - min_thresh) / (max_thresh - min_thresh)))
                                )
                                loop_fiber += 1
                            else:
                                # NOTE: PLOTS MISSING VALUES AS RED
                                offset += 1
                                colors.append(missing_color)

                    elif plot_mode == 'on_off':
                        for i in range(n_inners):
                            actual_i = i - offset
                            if i not in missing_indices:
                                if thresholds[actual_i] > cutoff_thresh:
                                    colors.append(suprathresh_color)
                                else:
                                    colors.append(subthresh_color)
                            else:
                                # NOTE: PLOTS MISSING VALUES AS RED
                                offset += 1
                                colors.append(missing_color)

                    # figure title -- make arbitrary, hard-coded subplot title modifications here (add elif's)
                    title = ''
                    for fib_key_name, fib_key_value in zip(
                        sim_object.fiberset_key,
                        sim_object.fiberset_product[fiberset_index],
                    ):
                        if alltitle:

                            if fib_key_name == 'fibers->z_parameters->diameter':
                                title = f'{title} Fiber Diameter: {fib_key_value} μm'
                            else:
                                # default title
                                title = f'{title} {fib_key_name}:{fib_key_value}'
                            title += '\n'
                        elif waveform_index == 0:
                            ax.set_ylabel(
                                f'{fib_key_value}',
                                fontsize=35,
                                rotation=0,
                                labelpad=20,
                            )

                    for wave_key_name, wave_key_value in zip(
                        sim_object.wave_key, sim_object.wave_product[waveform_index]
                    ):
                        if alltitle:
                            if wave_key_name == 'waveform->BIPHASIC_PULSE_TRAIN->pulse_width':
                                title = f'{title} Pulse Width: {wave_key_value} ms'
                            else:
                                title = f'{title} {wave_key_name}:{wave_key_value}'
                        elif potentials_product_index == max([x[0] for x in sim_object.master_product_indices]):
                            ax.set_xlabel(f'{wave_key_value}', fontsize=35, rotation=0)
                    ax.spines['left'].set_visible(False)
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['bottom'].set_visible(False)
                    ax.set_xticks([])
                    ax.set_yticks([])

                    # set title
                    if subplot_title_toggle and alltitle:
                        ax.set_title(title, fontsize=25)

                    # plot orientation point if applicable
                    if orientation_point is not None and show_orientation_point is True:
                        ax.plot(*orientation_point, 'o', markersize=30, color='red')

                    if add_colorbar:
                        if not microamps:
                            cb_label = r'mA'
                        else:
                            cb_label = u'\u03bcA'
                        cb: cbar.Colorbar = plt.colorbar(
                            mappable=plt.cm.ScalarMappable(
                                cmap=cmap,
                                norm=mplcolors.Normalize(vmin=min_thresh, vmax=max_thresh),
                            ),
                            ticks=tick.MaxNLocator(nbins=tick_count) if not min_max_ticks else [min_thresh, max_thresh],
                            ax=ax,
                            orientation='vertical',
                            aspect=colorbar_aspect if colorbar_aspect is not None else 20,
                            format='%0.2f',
                        )
                        if cbar_label_func == 'title':
                            cb.ax.set_title(
                                cb_label,
                                fontsize=colorbar_text_size_override
                                if (colorbar_text_size_override is not None)
                                else 25,
                                rotation=0,
                            )
                        else:
                            cb.set_label(
                                cb_label,
                                fontsize=colorbar_text_size_override
                                if (colorbar_text_size_override is not None)
                                else 25,
                                rotation=90,
                            )
                        # colorbar font size
                        if colorbar_text_size_override is not None:
                            cb.ax.tick_params(
                                labelsize=colorbar_text_size_override
                                if (colorbar_text_size_override is not None)
                                else 25
                            )

                    if plot_mode == 'fiber0' or plot_mode == 'on_off':
                        # plot slide (nerve and fascicles, defaulting to no outers)
                        sample_object.slides[0].plot(
                            final=False,
                            fix_aspect_ratio=True,
                            fascicle_colors=colors,
                            ax=ax,
                            outers_flag=plot_outers,
                            inner_format='k-',
                        )
                    elif plot_mode == 'fibers':
                        sample_object.slides[0].plot(
                            final=False,
                            fix_aspect_ratio=True,
                            ax=ax,
                            outers_flag=plot_outers,
                            inner_format='k-',
                        )
                        sim_object.fibersets[0].plot(ax=ax, fiber_colors=colors, size=dotsize)

                plt.gcf().tight_layout(rect=[0, 0.03, 1, 0.95])

                # set super title
                if title_toggle:
                    if suptitle_override is None:
                        plt.suptitle(
                            'Activation thresholds: {} (model {}, sim {})'.format(
                                sample_config.get('sample'), model_index, sim_index
                            ),
                            size=40,
                        )
                    else:
                        plt.suptitle(suptitle_override, size=40)
                if not alltitle:
                    plt.gcf().text(
                        0.5,
                        0.01,
                        "Pulse Width (ms)",
                        ha="center",
                        va="center",
                        fontsize=35,
                    )
                    plt.gcf().text(
                        -0.02,
                        0.5,
                        u"Fiber Diameter (\u03bcm)",
                        ha="center",
                        va="center",
                        rotation=90,
                        fontsize=35,
                    )

                # save figure as png
                if save_path is not None:
                    if not os.path.exists(save_path):
                        os.makedirs(save_path)
                    dest = f'{save_path}{os.sep}{sample_index}_{model_index}_{sim_index}.png'
                    figure.savefig(dest, dpi=300)

                # plot figure
                if plot:
                    plt.show()

        if track_colormap_bounds:
            print('BOUNDS:\n[')
            for bounds in colormap_bounds_tracking:
                print(f'\t{bounds},')
            print(']')

    return figure, axes, colormap_bounds_tracking


def ap_loctime(
    query_object: Query,
    delta_V: float = 60,
    rounding_precision: int = 5,
    n_sim_filter: List[int] = None,
    plot: bool = False,
    plot_nodes_on_find: bool = False,
    plot_compiled: bool = False,
    absolute_voltage: bool = True,
    n_sim_label_override: str = None,
    model_labels: List[str] = None,
    save: bool = False,
    subplots=False,
    nodes_only=False,
    amp=0,
):
    print(
        f'Finding time and location of action potentials,'
        f' which are defined as any voltage deflection of {delta_V} mV.'
    )

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

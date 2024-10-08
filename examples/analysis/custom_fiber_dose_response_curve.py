#!/usr/bin/env python3.7

"""Interpolate fiber locations and types from an existing ASCENT run.

See the "Dose-response curves reflecting fiber
diameters, types, and locations" section in the Running Ascent Usage documentation for more details.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent.

RUN THIS FROM REPOSITORY ROOT
"""

import os
import sys
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import lines
from scipy.interpolate import interp1d

sys.path.append(os.path.sep.join([os.getcwd(), '']))
from src.core import Fascicle, FiberSet, Sample, Simulation, Trace  # noqa E402
from src.core.query import Query  # noqa E402
from src.utils import Config, MaskInputMode, Object, PerineuriumThicknessMode, ScaleInputMode, SetupMode  # noqa E402

# USER INPUTS
# Only one of each index is supported at one time
SAMPLE = 300
MODEL = 300
SIM = 300

# Define the path to the input fiber data CSV file. Only include path after /input/{sample name}/
CSV_FILE = 'fiber_data/fiber_data.csv'  # Replace with your path

# Output directory for figures
OUT_DIR = f'output/{SAMPLE}_{MODEL}_{SIM}'

# Start code


def main():
    """Execute the post-hoc fiber script."""
    # Global settings/variables
    sns.set_style(style="whitegrid")
    os.makedirs(OUT_DIR, exist_ok=True)

    # Load thresholds from base model
    q = Query(
        {
            'partial_matches': False,
            'include_downstream': True,
            'indices': {'sample': [SAMPLE], 'model': [MODEL], 'sim': [SIM]},
        }
    ).run()
    # Get threshold data from ASCENT fibers
    base_thresh_data = q.threshold_data()
    palette = sns.color_palette(palette='deep', n_colors=np.max(base_thresh_data['inner']) + 1)

    # Load sim and sample objects
    sim_object = q.get_object(Object.SIMULATION, [SAMPLE, MODEL, SIM])
    sample_object = q.get_object(Object.SAMPLE, [SAMPLE, MODEL, SIM])

    # Load custom fiber coordinates
    input_name = sample_object.configs['sample']['sample']
    input_path = f'input/{input_name}'
    fiber_data = pd.read_csv(os.path.join(input_path, CSV_FILE))

    # Transform coordinates to sample (accounting for shrinkage, deformation, etc)
    xy_coords = np.array([fiber_data['x'], fiber_data['y']]).T

    # Map fibers to sample fascicles
    if hasattr(sample_object, 'init_slides'):
        out_to_fib, out_to_in = sample_object.init_slides[0].map_points(xy_coords)
    else:
        out_to_fib, out_to_in = sample_object.slides[0].map_points(xy_coords)
    tfm_coords = sample_object.point_transform(xy_coords)[0]
    fiber_data['x'] = tfm_coords[:, 0]
    fiber_data['y'] = tfm_coords[:, 1]
    for of, oi in zip(out_to_fib, out_to_in):
        for fibers, inner in zip(of, oi):
            fiber_data.loc[fibers, 'inner'] = inner
    fiber_data.loc[fiber_data['inner'].isna(), 'inner'] = -1
    fiber_data['inner'] = fiber_data.loc[:, 'inner'].astype('int')
    plot_sample_fibers(sample_object, fiber_data)
    fiber_data.loc[fiber_data['inner'] == -1, 'inner'] = np.nan

    # Warn about fibers not corresponding to fascicles
    any_na = fiber_data['inner'].isna().sum()
    if any_na:
        print(
            f'WARNING: {any_na} fiber found outside of fascicle boundaries, no thresholds will be computed for '
            f'these fibers.'
        )

    # Assign ASCENT fiberset coordinates
    base_x, base_y = sim_object.fibersets[0].xy_points(split_xy=True)
    assert len(base_x) == base_thresh_data['index'].max() + 1
    for idx in base_thresh_data['index'].unique():
        base_thresh_data.loc[base_thresh_data['index'] == idx, 'x'] = base_x[idx]
        base_thresh_data.loc[base_thresh_data['index'] == idx, 'y'] = base_y[idx]

    # Assign ASCENT fiberset diameters, etc
    for nsim, f_prod in enumerate(sim_object.fiberset_product):
        for k, v in zip(sim_object.fiberset_key, f_prod):
            if k.split('->')[-1] in fiber_data.columns:
                base_thresh_data.loc[base_thresh_data['nsim'] == nsim, k.split('->')[-1]] = v

    # Create one fiber for each diameter if only x and y coordinates are input
    if 'diameter' not in fiber_data.columns:
        fiber_data_diams = []
        for diam in base_thresh_data['diameter'].unique():
            fiber_data['diameter'] = diam
            fiber_data_diams.append(fiber_data.copy())
        fiber_data = pd.concat(fiber_data_diams, ignore_index=True)

    # Do fiber interpolation
    nonnan_interp = fiber_data.dropna(axis=0, inplace=False)
    nonnan_interp = interp_fibers(base_thresh_data, nonnan_interp)
    fiber_data.loc[nonnan_interp.index, 'threshold'] = nonnan_interp['threshold']

    # Output computed fiber thresholds and cleanup for plotting
    fiber_data.to_csv(os.path.join(OUT_DIR, 'interp_fiber_thresholds.csv'), index=False)
    fiber_data.dropna(axis=0, inplace=True)
    fiber_data['inner'] = fiber_data['inner'].astype(int)
    fiber_data['fascicle'] = fiber_data['inner']
    base_thresh_data['fascicle'] = base_thresh_data['inner']

    # Plot interpolated diameter data
    plot_fiber_hist(fiber_data)
    plot_diameter_thresholds(base_thresh_data, fiber_data, palette)

    # Plot interpolated data for each fascicle
    plot_fascicle_drc(fiber_data, palette)

    # Iterate over other fiber labels (var) found in input csv and plot dose-response of fiber types
    for var in fiber_data.columns:
        if var in ['x', 'y', 'z', 'fascicle', 'inner', 'diameter', 'threshold']:
            # Only iterate over fiber labels not covered by other functions
            continue

        # Plot dose response by label
        plot_var_drc(fiber_data, var)
        plot_var_fascicle_drc(fiber_data, var)


def plot_sample_fibers(sample_obj: Sample, interp_data: pd.DataFrame):
    """plot_sample_fibers creates plots of interpolated fibers over the sample cross-section.

    :param sample_obj: Sample object of the ASCENT-run cross-section
    :param interp_data: Dataframe of the interpolated fiber points
    """
    # Overlay post-hoc fiber coordinates with fascicles
    slide = sample_obj.slides[0]
    sns.scatterplot(interp_data, x='x', y='y', hue='inner', palette='deep')
    slide.plot(
        fix_aspect_ratio=True,
        final=False,
        inner_index_labels=True,
        scalebar=True,
        scalebar_length=100,
        scalebar_units='μm',
        title='Detected fascicle borders and custom query points.',
        axlabel="\u03bcm",
    )
    plt.legend()
    plt.gcf().savefig(OUT_DIR + '/sample_morph.png')
    plt.close('all')


def interp_fibers(base_df, interp_df):
    """interp_fibers interpolates fiber diameters from a set of ASCENT-run fibers.

    :param base_df: dataframe of ASCENT-run fibers with "inner", "diameter", and "threshold" columns.
    :param interp_df: dataframe of fibers to interpolate with "inner" and "diameter" columns.
    :return: interp_df same as interp_df parameter with new "threshold" column.
    """

    def interp_diameter(base_data: pd.DataFrame, interp_data: pd.DataFrame):
        # Do quadratic interpolation of thresholds over fiber diameters
        fasc_avg = base_data.groupby('diameter', as_index=False)['threshold'].mean()
        base_x = fasc_avg['diameter'].to_numpy()
        base_y = fasc_avg['threshold'].to_numpy()
        interp_x = interp_data['diameter'].to_numpy()
        interp = interp1d(base_x, base_y, kind='quadratic')
        return interp(interp_x)

    def interp_diameter_loc(base_data: pd.DataFrame, interp_data: pd.DataFrame):
        raise NotImplementedError("XY location interpolation is not yet supported")

    # Get data for each inner and interpolate
    for inner in interp_df['inner'].unique():
        base_data = base_df.loc[base_df['inner'] == inner]
        if len(base_data) == 0:
            continue
        interp_data = interp_df.loc[interp_df['inner'] == inner]

        interp_df.loc[interp_data.index, 'threshold'] = interp_diameter(base_data, interp_data)

    return interp_df


def plot_fiber_hist(interp_data):
    """plot_fiber_hist creates a histogram of the interpolated fiber diameter distribution.

    :param interp_data: Dataframe of interpolated fibers.
    """
    # Visualize fiber diameter distribution
    g = sns.histplot(
        interp_data,
        x='diameter',
        hue='fascicle',
        palette='deep',
        multiple='stack',
        element='bars',
        common_bins=True,
        legend=True,
    )
    g.legend(list(range(len(np.unique(interp_data['fascicle'])))))
    g.legend_.set_title('Inner')
    plt.title(f'Fiber Diameter Distribution for Sample {SAMPLE}')
    plt.xlabel('Fiber diameter (um)')
    plt.ylabel('Fiber Count')
    plt.gcf().savefig(OUT_DIR + '/fiber_cnt.png')
    plt.close('all')


def plot_diameter_thresholds(base_data, interp_data, palette):
    """Create a lineplot of the interpolated fiber diameter thresholds and ASCENT-run fiber diameter thresholds.

    :param base_data: Dataframe of ASCENT-run fibers.
    :param interp_data: Dataframe of interpolated fibers.
    :param palette: Color palette for the fascicles.
    """
    # Plot base thresholds on top of interpolated fit at base diameters for fit validation.
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.subplots_adjust(right=0.8)
    sns.scatterplot(base_data, x='diameter', y='threshold', hue='fascicle', palette=palette, ax=ax)
    g = sns.lineplot(data=interp_data, x='diameter', y='threshold', hue='fascicle', palette=palette, legend=True)
    g.legend(np.arange(len(interp_data['fascicle'].unique())))
    sns.move_legend(g, "upper left", bbox_to_anchor=(1, 1))
    g.legend_.set_title('Fascicle')
    leg = plt.legend(
        np.arange(len(interp_data['fascicle'].unique())),
        loc="upper left",
        bbox_to_anchor=(1, 0.5),
        title='Fascicle',
    )
    g.add_artist(leg)
    h = [plt.plot([], [], color="gray", ls=i, ms=1)[0] for i in [':', '-']]
    plt.legend(handles=h, labels=['Computed', 'Interpolated'], loc="upper left", bbox_to_anchor=(1, 1))
    plt.title('Thresholds vs. Plausible Fiber Diameters')
    plt.xlabel('Fiber diameter (um)')
    plt.ylabel('Threshold (mA)')
    plt.gcf().savefig(OUT_DIR + '/fiber_diam_thresholds.png')
    plt.close('all')


def plot_diameter_drc(interp_data):
    """plot_diameter_drc creates a cumulative dose-response curve of the interpolated fiber thresholds.

    :param interp_data: Dataframe of interpolated fibers.
    """
    # Dose response curves for each diameter
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.ecdfplot(data=interp_data, x='threshold', hue='diameter', stat='proportion', palette='flare')
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    plt.ylabel('Percent of fibers activated (%)')
    plt.xlabel('Thresholds (mA)')
    plt.title('Diameter - Dose-Response Curve')
    plt.gcf().savefig(OUT_DIR + '/fiber_diam_drc.png')
    plt.close('all')


def plot_fascicle_drc(interp_data, palette):
    """plot_fascicle_drc creates a lineplot of the interpolated fiber thresholds per fascicle.

    :param interp_data: Dataframe of interpolated fibers.
    :param palette: Color palette for the fascicles.
    """
    # Dose response curves for each fascicle
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.ecdfplot(data=interp_data, x='threshold', hue='fascicle', stat='proportion', palette=palette)
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    plt.ylabel('Percent of fibers activated (%)')
    plt.xlabel('Thresholds (mA)')
    plt.title('Fascicle Dose-Response Curve')
    plt.gcf().savefig(OUT_DIR + '/fascicle_drc.png')


def plot_var_drc(interp_data, var):
    """plot_fascicle_drc creates a lineplot of the interpolated fiber thresholds per value of a label variable (var).

    :param interp_data: Dataframe of interpolated fibers.
    :param var: Label variable found in the csv file for interpolated fibers.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.ecdfplot(data=interp_data, x='threshold', hue=var, stat='proportion', palette='deep')
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    plt.ylabel('Percent of fibers activated (%)')
    plt.xlabel('Thresholds (mA)')
    plt.title(f'{var.capitalize()} Dose-Response Curve')
    plt.gcf().savefig(OUT_DIR + f'/{var}_drc.png')


def plot_var_fascicle_drc(interp_data, var):
    """Create a lineplot of the interpolated fiber thresholds per value of a label variable (var) and fascicle.

    :param interp_data: Dataframe of interpolated fibers.
    :param var: Label variable found in the csv file for interpolated fibers.
    """
    # Plot var in linestyles, fascicle in hue
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.subplots_adjust(right=0.85)
    markers_list = list(lines.lineStyles.keys())  # ["solid", "dashed", "dotted", "dashdot"]
    if len(np.unique(interp_data[var])) > len(markers_list):
        warnings.warn(
            'Only four line styles available for plotting, hence currently limited to four different fiber_types.',
            stacklevel=2,
        )
    fiber_var_list = np.unique(interp_data[var])
    # Create a plot for each value in the label variables
    for i, fib_type in enumerate(fiber_var_list):
        g = sns.ecdfplot(
            data=interp_data.loc[interp_data[var] == fib_type],
            x='threshold',
            hue='fascicle',
            stat="proportion",
            palette='deep',
            log_scale=False,
            legend=True,
            linestyle=markers_list[i],
            label=fib_type,
        )
    g.legend(np.arange(len(interp_data['fascicle'].unique())))
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    g.legend_.set_title('Fascicle')
    plt.ylabel('Percent of fibers activated (%)')
    plt.xlabel('Thresholds (mA)')
    plt.title(f'Myelinated Dose-Response Curve per Fascicle and {var.capitalize()}')

    leg = plt.legend(
        np.arange(len(interp_data['fascicle'].unique())),
        loc="upper left",
        bbox_to_anchor=(1, 0.5),
        title='Fascicle',
    )
    ax.add_artist(leg)
    h = [plt.plot([], [], color="gray", ls=i, ms=1)[0] for i in markers_list[: len(fiber_var_list)]]
    plt.legend(
        handles=h, labels=list(fiber_var_list), loc="upper left", bbox_to_anchor=(1, 1), title=f"{var.capitalize()}"
    )
    plt.gcf().savefig(OUT_DIR + f'/fasc_{var}_drc_breakout.png')
    plt.close('all')


if __name__ == '__main__':
    main()

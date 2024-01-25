"""Fiber template generation from transmembrane current matrix.

This script will likely later become part of the query class later on,
and only serves as a starting point for template generation.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent.
"""
import os
import sys

import numpy as np
from import_Imembrane import import_tm_current_matrix
from scipy.interpolate import interp1d
from scipy.io import savemat
from scipy.signal import resample
from scipy.stats import mode

sys.path.append(os.path.sep.join([os.getcwd(), '']))
from src.core.query import Query  # noqa E402
from src.utils import Config  # noqa E402

sample = 202303232
model = 0
sim = 20230323093
fiber = 0  # fiber index in each nsim. Used to specify membrane current matrix file path on line 75
amp_num = 0

q = Query(
    {
        'partial_matches': False,
        'include_downstream': True,
        'indices': {'sample': [sample], 'model': [model], 'sim': [sim]},
    }
).run()
sim_obj = q.get_config(Config.SIM, [sim])
template_fiber_diameters = sim_obj['fibers']['z_parameters']['diameter']

# Input variables
fiber_type = sim_obj['fibers']['mode']  # Set common time bounds based fiber type
stim_pulse_start_time_ms = sim_obj['waveform']['global']['on']  # [ms]

# Note: tpeakl is relative to start of stim pulse.
if fiber_type in [
    'MRG_DISCRETE',
    'MRG_INTERPOLATION',
    'SMALL_MRG_INTERPOLATION_V1',
]:  # Myelinated types that ascent allows
    fiber_type = 'myelinated'
    stim_pulse_duration_ms = 0.1  # includes total duration of biphasic stim pulse
    common_time_bounds_ms = [-2.4, 36]
    n_compartments_per_repeatable_uit = 11
else:  # Assuming ascent ran successfully, if not myelinated fiber, then input is unmyelinated fiber
    fiber_type = 'unmyelinated'
    stim_pulse_duration_ms = 0.4
    common_time_bounds_ms = [-2, 60]
    n_compartments_per_repeatable_uit = 1


output_data = []
fiber_data_list = []
for fiber_ind in range(len(template_fiber_diameters)):  # Looping through simulated fiber diameters...
    # Assuming nsims indexing correlates with fiber index (e.g., nsim = 0 is the first diameter, ...)
    print(f"Constructing templates for fiber {fiber_ind}")
    coordinates_filename = os.path.join(
        os.getcwd(), f"samples/{sample}/models/{model}/sims/{sim}/fibersets/{fiber_ind}/0.dat"
    )
    compartment_coordinates = np.loadtxt(coordinates_filename, skiprows=1)
    # Get rid of the zeros column and store the coordinates for the current fiber
    z_locations_mm = compartment_coordinates[:, 2] * 1e-3  # [mm]

    # Read in membrane current matrix
    membrane_current_filename = os.path.join(
        os.getcwd(),
        f"samples\\{sample}\\models\\{model}\\sims\\{sim}\\n_sims\\{fiber_ind}\\data\\outputs\\"
        f"Imembrane_axon{fiber}_fiber{fiber}_amp{amp_num}.dat",
    )
    tstop, time_vector, transmembrane_curent_matrix = import_tm_current_matrix(membrane_current_filename)

    # Preprocessing
    # Extract templates from matrix - N (time) x Number of templates ( x 11 for myelinated fiber compartments)
    # Blank out stim artifact - cut off from stim_pulse start time + stim pulse duration,
    # but ensure t value is the same at that point
    blanking_buffer_ms = 0.129  # [ms]
    valid_time_indices = np.where(time_vector > (stim_pulse_start_time_ms + stim_pulse_duration_ms))[0][:-1]
    # 0 index returns list of indices from the tuple returned from .where().
    # [:-1] removes the last index to avoid indexing conflicts

    transmembrane_curent_matrix = transmembrane_curent_matrix[valid_time_indices, :]
    time_vector = time_vector[valid_time_indices]
    time_vector = time_vector - time_vector[0]
    blanking_buffer_first_idx = np.argwhere(time_vector > blanking_buffer_ms)[0][0]
    transmembrane_curent_matrix = transmembrane_curent_matrix[blanking_buffer_first_idx:, :]
    time_vector = time_vector[time_vector > blanking_buffer_ms]

    # Calculate CV - focus on myelinated fibers
    node_indices = range(0, len(z_locations_mm), n_compartments_per_repeatable_uit)
    node_z_locations = z_locations_mm[node_indices]
    index_to_extract = round((len(node_z_locations) - 1) * 0.7)  #
    value_at_70_percent = node_z_locations[index_to_extract]
    dz_mm, _ = mode(np.diff(z_locations_mm[node_indices]), keepdims=False)
    target_compartment_index = np.where(z_locations_mm == value_at_70_percent)[0][0]

    # Resample around target compartment index at a high factor for peaks to align properly
    resample_factor = 64
    indices_for_upsample = target_compartment_index + np.arange(-6, 7) * n_compartments_per_repeatable_uit
    indices_for_upsample = indices_for_upsample.tolist()

    # Subset columns from the matrix
    transmembrane_currents_all_compartments_subset = transmembrane_curent_matrix[:, indices_for_upsample]
    upsampled_transmembrane_currents_all_compartments_subset, upsampled_time_vector = resample(
        transmembrane_currents_all_compartments_subset,
        resample_factor * (len(transmembrane_currents_all_compartments_subset) - 1),
        t=time_vector,
    )
    # Find the index of the maximum value in each column
    max_idx = np.argmax(upsampled_transmembrane_currents_all_compartments_subset, axis=0)

    # Calculate the time between maxima
    measured_time_between_compartments_or_nodes = np.diff(upsampled_time_vector[max_idx])

    # Refine the time between maxima by taking the median
    refined_time_between_compartments_or_nodes = np.median(measured_time_between_compartments_or_nodes)

    # Set the time_between_compartments_or_nodes to the refined value
    time_between_compartments_or_nodes = refined_time_between_compartments_or_nodes

    # Calculate conduction velocity
    conduction_velocity_m_per_s = dz_mm / time_between_compartments_or_nodes

    # Calculate dipole variable
    dipolar_currents = -np.cumsum(transmembrane_curent_matrix, 1)

    # Pull out templates for both mono and dipole methods - myelinated has 11 surrounding compartments
    if fiber_type == 'myelinated':
        myel_compartments_around_target_idx = range(
            target_compartment_index, target_compartment_index + n_compartments_per_repeatable_uit
        )
        monopolar_temporal_template = transmembrane_curent_matrix[:, myel_compartments_around_target_idx]
        dipole_temporal_template = dipolar_currents[:, myel_compartments_around_target_idx]
    else:
        monopolar_temporal_template = transmembrane_curent_matrix[:, target_compartment_index]
        dipole_temporal_template = dipolar_currents[:, target_compartment_index]

    # Upsample each template by factor of 15 - to get a more exact tpeak suitable for template alignment for
    # interpolation over fiber diameter.
    template_upsample_factor = 15
    monopolar_signal, monopolar_time = resample(
        monopolar_temporal_template, template_upsample_factor * (len(monopolar_temporal_template) - 1), t=time_vector
    )
    dipole_signal, dipole_time = resample(
        dipole_temporal_template, template_upsample_factor * (len(dipole_temporal_template) - 1), t=time_vector
    )

    # Shifting time vectors so tpeak happens at time 0
    peak_idx_monopolar = np.argmax(monopolar_signal[:, 0])
    peak_idx_dipole = np.argmax(dipole_signal[:, 0])
    time_at_peak_monopolar = monopolar_time[peak_idx_monopolar]
    time_at_peak_dipole = dipole_time[peak_idx_dipole]
    monopolar_time -= time_at_peak_monopolar
    dipole_time -= time_at_peak_dipole

    # At this point, though peaks all happen at t=0, the previous x-points won't be aligned. Need a new standard
    # time vector and use interp to resample the points.
    dt_pre_resample, _ = mode(np.diff(time_vector), keepdims=False)  # [ms]
    common_time_vector = np.concatenate(
        (
            np.flipud(np.arange(0, min(common_time_bounds_ms), -dt_pre_resample)),
            np.arange(dt_pre_resample, max(common_time_bounds_ms) + dt_pre_resample, dt_pre_resample),
        )
    )
    mono_interp = interp1d(monopolar_time, monopolar_signal, kind='cubic', axis=0, bounds_error=False, fill_value=0)
    temporal_templates = mono_interp(common_time_vector)

    # Template construction - interpolate to form mono and dipole temporal templates using spline.
    dipole_interp = interp1d(dipole_time, dipole_signal, kind='cubic', axis=0, bounds_error=False, fill_value=0)
    dipole_temporal_templates = dipole_interp(common_time_vector)

    target_compartment_index_z_loc = z_locations_mm[target_compartment_index]
    # Outputs - store variables for this single node template.
    fiber_data = (
        fiber_ind,
        template_fiber_diameters[fiber_ind],
        temporal_templates,
        dipole_temporal_templates,
        conduction_velocity_m_per_s,
        common_time_vector,
        time_at_peak_monopolar,
        time_at_peak_dipole,
        target_compartment_index,
        target_compartment_index_z_loc,
        z_locations_mm,
    )
    # Append single node template to list of node templates per fiber.
    fiber_data_list.append(fiber_data)

# Constructing structured array to allow for matlab export of 'output_data' to be in the form of a struct, not a cell.
# A struct is necessary for follow-up CAPulator matlab script.
output_data = np.array(
    fiber_data_list,
    dtype=[
        ('fiber_index', type(fiber_ind)),
        ('fiber_diameter', type(template_fiber_diameters[fiber_ind])),
        ('temporal_templates', type(temporal_templates)),
        ('dipole_temporal_templates', type(dipole_temporal_templates)),
        ('conduction_velocity_m_per_s', type(conduction_velocity_m_per_s)),
        ('common_time_vector_ms', type(common_time_vector)),
        ('reference_peak_time_i_ms', type(time_at_peak_monopolar)),
        ('reference_peak_time_i_dipole_ms', type(time_at_peak_dipole)),
        ('target_compartment_index', type(target_compartment_index)),
        ('z_loc_of_target_compartment_index', type(target_compartment_index_z_loc)),
        ('z_locations_mm_all', type(z_locations_mm)),
    ],
)

# Save as .mat file to be compatible with edgar's foloowing CAPulator matlab script.
output_file_name = os.path.join('output', 'analysis', 'templates')
os.makedirs(output_file_name, exist_ok=True)
output_file_name = os.path.join(output_file_name, f'template_data_{sample}_{model}_{sim}.mat')
savemat(output_file_name, {'fiber_type': fiber_type, 'output_data_structure': output_data})

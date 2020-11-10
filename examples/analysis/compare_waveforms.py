#!/usr/bin/env python3.7
# RUN THIS FROM REPOSITORY ROOT

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import statistics

from core import Simulation, Sample
from core.query import Query
from utils import Config, Object
from typing import List
from scipy import stats

sys.path.append(os.path.sep.join([os.getcwd(), '']))


def flatten(list_in: List):
    # https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
    flattened_list_in = [item for sublist in list_in for item in sublist]
    return flattened_list_in


def get_sim_thresholds(sim_obj: Simulation):

    master_thresholds: List[List[float]] = []
    for t, (potentials_ind, waveform_ind) in enumerate(sim_obj.master_product_indices):

        nsim_outputs_directory = os.path.join(sim_dir, str(sim_num), 'n_sims', str(t), 'data', 'outputs')

        active_src_ind, fiberset_ind = sim_obj.potentials_product[potentials_ind]

        # fetch thresholds, then find min and max
        out_in_fib, out_in = sim_obj.fiberset_map_pairs[fiberset_ind]

        n_inners = max(flatten(out_in))

        nsim_thresholds: List[float] = []
        for inner in range(1 if n_inners is 0 else 1):

            inner_thresholds: List[float] = []

            outer = [index for index, inners in enumerate(out_in) if inner in inners][0]
            for local_fiber_index, _ in enumerate(out_in_fib[outer][out_in[outer].index(inner)]):
                thresh_path = os.path.join(
                    nsim_outputs_directory,
                    'thresh_inner{}_fiber{}.dat'.format(inner, local_fiber_index)
                )
                if os.path.exists(thresh_path):
                    threshold = np.loadtxt(thresh_path)
                    if threshold.size == 3:
                        threshold = threshold[-1]
                else:
                    print("MISSING: ".format(thresh_path))
                    threshold = 0

                inner_thresholds.append(abs(threshold))
            nsim_thresholds.append(inner_thresholds)
        master_thresholds.append(nsim_thresholds)

    return master_thresholds


def response_calculator(sim_obj: Object.SIMULATION, thresholds, response: float, a_s_i: int, f_i: int, w_i: int):
    p_i = sim_obj.potentials_product.index((a_s_i, f_i))
    m_p_i = sim_obj.master_product_indices.index((p_i, w_i))
    data = thresholds[m_p_i]

    sorted_flat_data = sorted(flatten(data))

    # https://stackoverflow.com/questions/12414043/map-each-list-value-to-its-corresponding-percentile
    percentiles = [stats.percentileofscore(sorted_flat_data, a, 'rank') for a in sorted_flat_data]

    # https://stackoverflow.com/questions/9706041/finding-index-of-an-item-closest-to-the-value-in-a-list-thats-not-entirely-sort
    data_index = min(range(len(percentiles)), key=lambda i: abs(percentiles[i]-response))

    return sorted_flat_data[data_index]


def var_within_calculator(sim_obj: Object.SIMULATION, thresholds, a_s_i: int, f_i: int, w_i: int):
    p_i = sim_obj.potentials_product.index((a_s_i, f_i))
    m_p_i = sim_obj.master_product_indices.index((p_i, w_i))
    data = thresholds[m_p_i]
    fasc_means = [np.mean(x) for x in data]
    vw = np.std(fasc_means)
    return vw


query_inds = [2, 3, 4, 5, 6, 7, 8, 9, 10]  # removed 3 (1 fasc??)

query_dim = len(query_inds)

master_i20 = [None] * query_dim
master_i50 = [None] * query_dim
master_i80 = [None] * query_dim
master_i100 = [None] * query_dim
master_var_within = [None] * query_dim

for query_ind, _ in enumerate(query_inds):

    criteria: str = os.path.join('config', 'user', 'query_criteria', '{}.json'.format(query_inds[query_ind]))
    q = Query(criteria)
    q.run()
    results = q.summary()

    sample_num = results['samples'][0]['index']
    model_num = results['samples'][0]['models'][0]['index']
    sim_num = results['samples'][0]['models'][0]['sims'][0]

    sim_dir = os.path.join(os.getcwd(), 'samples', str(sample_num), 'models', str(model_num), 'sims')
    sim: Simulation = q.get_object(Object.SIMULATION, [sample_num, model_num, sim_num])

    active_src_dim = len(sim.src_product)
    fiberset_dim = len(sim.fibersets)
    waveform_dim = len(sim.waveforms)
    i_20 = [[[[0] for k in range(waveform_dim)] for j in range(fiberset_dim)] for i in range(active_src_dim)]
    i_50 = [[[[0] for k in range(waveform_dim)] for j in range(fiberset_dim)] for i in range(active_src_dim)]
    i_80 = [[[[0] for k in range(waveform_dim)] for j in range(fiberset_dim)] for i in range(active_src_dim)]
    i_100 = [[[[0] for k in range(waveform_dim)] for j in range(fiberset_dim)] for i in range(active_src_dim)]
    var_within = [[[[0] for k in range(waveform_dim)] for j in range(fiberset_dim)] for i in range(active_src_dim)]

    # sample_object: Sample = q.get_object(Object.SAMPLE, [sample_num])

    m_thresholds = get_sim_thresholds(sim)

    master_i20[query_ind] = [None] * active_src_dim

    for t, (potentials_ind, waveform_ind) in enumerate(sim.master_product_indices):
        active_src_ind, fiberset_ind = sim.potentials_product[potentials_ind]
        i_20[active_src_ind][fiberset_ind][waveform_ind] = response_calculator(sim, m_thresholds, 20, active_src_ind, fiberset_ind, waveform_ind)
        i_50[active_src_ind][fiberset_ind][waveform_ind] = response_calculator(sim, m_thresholds, 50, active_src_ind, fiberset_ind, waveform_ind)
        i_80[active_src_ind][fiberset_ind][waveform_ind] = response_calculator(sim, m_thresholds, 80, active_src_ind, fiberset_ind, waveform_ind)
        i_100[active_src_ind][fiberset_ind][waveform_ind] = response_calculator(sim, m_thresholds, 100, active_src_ind, fiberset_ind, waveform_ind)

        var_within[active_src_ind][fiberset_ind][waveform_ind] = var_within_calculator(sim, m_thresholds, active_src_ind, fiberset_ind, waveform_ind)

    master_i20[query_ind] = i_20
    master_i50[query_ind] = i_50
    master_i80[query_ind] = i_80
    master_i100[query_ind] = i_100
    master_var_within[query_ind] = var_within

active_src_ind = 0

fig, axs = plt.subplots(fiberset_dim)
for fiberset_ind in range(fiberset_dim):
    for waveform_ind, _ in enumerate(sim.waveforms):
        axs[fiberset_ind].plot(waveform_ind,
                               statistics.stdev([master_i20[x][active_src_ind][fiberset_ind][waveform_ind] for x in range(query_dim)]) /
                               statistics.mean([master_i20[x][active_src_ind][fiberset_ind][waveform_ind] for x in range(query_dim)])
                               , 'ko')
        axs[fiberset_ind].plot(waveform_ind,
                               statistics.stdev([master_i50[x][active_src_ind][fiberset_ind][waveform_ind] for x in range(query_dim)]) /
                               statistics.mean([master_i50[x][active_src_ind][fiberset_ind][waveform_ind] for x in range(query_dim)])
                               , 'ro')
        axs[fiberset_ind].plot(waveform_ind,
                               statistics.stdev([master_i80[x][active_src_ind][fiberset_ind][waveform_ind] for x in range(query_dim)]) /
                               statistics.mean([master_i80[x][active_src_ind][fiberset_ind][waveform_ind] for x in range(query_dim)])
                               , 'bo')
        axs[fiberset_ind].plot(waveform_ind,
                               statistics.stdev([master_i100[x][active_src_ind][fiberset_ind][waveform_ind] for x in range(query_dim)]) /
                               statistics.mean([master_i100[x][active_src_ind][fiberset_ind][waveform_ind] for x in range(query_dim)])
                               , 'co')

fig2, axs2 = plt.subplots(fiberset_dim)
for fiberset_ind in range(fiberset_dim):
    for waveform_ind, _ in enumerate(sim.waveforms):
        axs2[fiberset_ind].plot(waveform_ind,
                               statistics.stdev([master_var_within[x][active_src_ind][fiberset_ind][waveform_ind] for x in range(query_dim)]) /
                               statistics.mean([master_var_within[x][active_src_ind][fiberset_ind][waveform_ind] for x in range(query_dim)]), 'ko')
plt.show()

print('done')

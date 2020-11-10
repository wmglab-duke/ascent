import numpy as np
import matplotlib.pyplot as plt

N = 5

exp_thresholds = (0.37, 1.6, 3.8, 17)
errs = (0.18, 0.35, 0.84, 7.6)
types = ["A\n(7.8 \u03bcm MRG)", "Fast B\n(3.6 \u03bcm MRG)", "Slow B\n(2.1 \u03bcm MRG)", "C-Fiber\n(1 \u03bcm Tigerholm)"]
ind = np.arange(len(types))

# 10 um MRG
# 5.7 um MRG
# 2 um MRG
# 0.8 um Tigerholm

# model_thresholds = (0.339258, 0.854133, 3.222187, 23.140625)

# 7.8 um MRG
# 3.6 um MRG
# 2.1 um MRG
# 1 um Tigerholm
# TODO change last 2 values in the row below (1)
model_thresholds = (0.469141, 1.820371, 3.108423, 20.683594)

width = 0.35

fig, ax = plt.subplots(figsize=(14, 10))
plt.bar(ind, exp_thresholds, width, yerr=errs, color='dodgerblue', alpha=0.6, error_kw=dict(ecolor='black'),
             label='Yoo et al. 2013 (Dog Cervical Vagus)')
plt.plot(ind, model_thresholds, marker='.', color='crimson', markersize=20, linestyle='None', label='ASCENT')

plt.ylabel('Activation Threshold (mA)', fontsize=25)
plt.title(u"Replication of Experimental Results with ASCENT, PW = 300 \u03bcs", fontsize=30) #
plt.xticks(ind, [my_type for my_type in types], fontsize=25)
plt.yticks(fontsize=25)

handles, labels = ax.get_legend_handles_labels()
order = [1, 0]
ax.legend([handles[idx] for idx in order], [labels[idx] for idx in order], loc=2, fontsize=25)

# plt.legend(loc=2, fontsize=25)

plt.show()

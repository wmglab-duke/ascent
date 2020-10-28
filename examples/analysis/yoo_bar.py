import numpy as np
import matplotlib.pyplot as plt

N = 5

exp_thresholds = (0.37, 1.6, 3.8, 17)
errs = (0.18, 0.35, 0.84, 7.6)
types = ["A\n7.8 \u03bcm MRG", "Fast B\n3.6 \u03bcm MRG", "Slow B\n2.1 \u03bcm MRG", "C-Fiber\n1 \u03bcm Tigerholm"]
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

fig = plt.subplots(figsize=(12, 10))
p1 = plt.bar(ind, exp_thresholds, width, yerr=errs, color='lightsalmon', alpha=0.6, error_kw=dict(ecolor='black'),
             label='Yoo et al. 2013 (Dog Cervical Vagus)')
p2 = plt.plot(ind, model_thresholds, marker='.', color='blueviolet', markersize=20, linestyle='None', label='ASCENT')

plt.ylabel('Activation Threshold (mA)', fontsize=20)
plt.title(u"Replication of Experimental Results with ASCENT, PW = 300 \u03bcs", fontsize=20) #
plt.xticks(ind, [my_type for my_type in types], fontsize=20)
plt.yticks(fontsize=20)
plt.legend(loc=2, fontsize=20)

plt.show()

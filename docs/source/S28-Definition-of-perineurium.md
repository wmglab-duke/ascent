# S28: Definition of perineurium
## 1.1 Definition of perineurium

The perineurium is a thin highly resistive layer of connective tissue
and has a profound impact on thresholds of activation and block. Our
previous modeling work demonstrates that representing the perineurium
with a thin layer approximation (Rm = rho\*peri\_thk), rather than as a
thinly meshed domain, reduces mesh complexity and is a reasonable
approximation \[1\]. Therefore, perineurium can be modeled with a thin
layer approximation (except with “peanut” fascicles; see an example in
Fig 2), termed “contact impedance” in COMSOL (if ***Model’s***
`“use_ci”` parameter is true ([S8 Text](S8-JSON-file-parameter-guide))), which relates the normal component of
the current density through the surface
![f5] to the drop in electric
potentials ![f3] and the sheet resistance ![f4]:

![f1]

The sheet resistance ![f4] is defined as the sheet thickness
![f6] divided by the material bulk conductivity ![f7] :

![f2]

Our previously published work quantified the relationship between fascicle diameter and perineurium thickness \[2\] (Table A).

Table A. Previously published relationships between fascicle diameter and
perineurium thickness.

| **Species** | **peri\_thk:** ***f*(species, d<sub>fasc</sub>)** | **References** |
| ----------- | ------------------------------------------------------------ | -------------- |
| Rat         | peri\_thk = 0.01292\*d<sub>fasc</sub> + 1.367 \[um\]         | \[2\]         |
| Pig         | peri\_thk = 0.02547\*d<sub>fasc</sub> + 3.440 \[um\]         | \[2\]         |
| Human       | peri\_thk = 0.03702\*d<sub>fasc</sub> + 10.50 \[um\]         | \[2\]         |


The “rho\_perineurium” parameter in ***Model*** can take either of two
modes:

  - “RHO\_WEERASURIYA”: The perineurium conductivity value changes with the frequency of electrical stimulation (for
    a single value, not a spectrum, defined in ***Model*** as
    “frequency”) and temperature (using a Q10 adjustment, defined in
    ***Model*** as “temperature”) based on measurements of frog sciatic
    perineurium \[1,3\]. The equation is defined in
    `src/core/Waveform.py` in the `rho_weerasuriya()` method.

  - “MANUAL”: Conductivity value assigned to the perineurium is as
    explicitly defined in either `materials.json` or ***Model*** without
    any corrections for temperature or frequency.

## 1.2 References
1. Pelot NA, Behrend CE, Grill WM. On the parameters used in finite element modeling of compound peripheral nerves. J Neural Eng [Internet]. 2019;16(1):16007. Available from: [http://dx.doi.org/10.1088/1741-2552/aaeb0c](http://dx.doi.org/10.1088/1741-2552/aaeb0c)
2. 	Pelot NA, Goldhagen GB, Cariello JE, Musselman ED, Clissold KA, Ezzell JA, et al. Quantified Morphology of the Cervical and Subdiaphragmatic Vagus Nerves of Human, Pig, and Rat. Front Neurosci [Internet]. 2020;14:1148. Available from: [https://doi.org/10.3389/fnins.2020.601479](https://doi.org/10.3389/fnins.2020.601479)
3. 	Weerasuriya A, Spangler RA, Rapoport SI, Taylor RE. AC impedance of the perineurium of the frog sciatic nerve. Biophys J. 1984 Aug;46(2):167–74. Available from: [https://dx.doi.org/10.1016%2FS0006-3495(84)84009-6](https://dx.doi.org/10.1016%2FS0006-3495(84)84009-6)

[f1]: https://chart.apis.google.com/chart?cht=tx&chl=\vec{n}\cdot\vec{J_{1}}=\frac{1}{\rho_{s}}(V_{1}-V_{2})
[f2]: https://chart.apis.google.com/chart?cht=tx&chl=\rho_{s}=\frac{d_{s}}{\sigma_{s}}
[f3]: https://chart.apis.google.com/chart?cht=tx&chl=(V_{1}-V_{2})
[f4]: https://chart.apis.google.com/chart?cht=tx&chl=(\rho_{s})
[f5]: https://chart.apis.google.com/chart?cht=tx&chl=(\vec{n}\cdot\vec{J_{1}})
[f6]: https://chart.apis.google.com/chart?cht=tx&chl=(\d_{s})
[f7]: https://chart.apis.google.com/chart?cht=tx&chl=(\sigma_{s})

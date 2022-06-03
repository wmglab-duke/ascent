# Defining and assigning materials in COMSOL

Materials are defined in the COMSOL “Materials” node for each material
“function” indicated in the “preset” cuff configuration file (i.e.,
cuff “insulator”, contact “conductor”, contact “recess”, and cuff
“fill”) and nerve domain (i.e., endoneurium, perineurium,
epineurium). Material properties for each function are assigned in
***Model*’s** “conductivities” JSON Object by either referencing
materials in the default materials library
(`config/system/materials.json`) by name, or with explicit definitions
of a materials name and conductivity as a JSON Object ([S8 Text](S8-JSON-file-parameter-guide)).
See [link](link to ModelWrapper.addMaterialDefinitions()) for code one how this happens.

## Adding and assigning default material properties

Default material properties defined in `config/system/materials.json`
are listed in Table A. To accommodate automation of
frequency-dependent material properties (for a single frequency, i.e.,
sinusoid), parameters for material conductivity that are dependent on
the stimulation frequency are calculated in Runner’s
`compute_electrical_parameters()` method and saved to ***Model*** before
the handoff() method is called. Our pipeline supports calculation of the
frequency-dependent conductivity of the perineurium based on
measurements from the frog sciatic nerve \[1\] using the
`rho_weerasuriya()` method in the Python Waveform class. See [Fig. 2](https://doi.org/10.1371/journal.pcbi.1009285.g002) for
identification of tissue types in a compound nerve cross section (i.e.,
epineurium, perineurium, endoneurium).

Table A. Default material conductivities.

| **Material**  | **Conductivity**             | **References**         |
| ------------- | ---------------------------- | ---------------------- |
| silicone      | 10^-12 \[S/m\]               | \[2\]                 |
| platinum      | 9.43 ⨉ 10^6 \[S/m\]          | \[3\]                 |
| endoneurium   | {1/6, 1/6, 1/1.75} \[S/m\]   | \[4,5\]       |
| epineurium    | 1/6.3 \[S/m\]                | \[6-8\] |
| muscle        | {0.086, 0.086, 0.35} \[S/m\] | \[9\]             |
| fat           | 1/30 \[S/m\]                 | \[10\]             |
| encapsulation | 1/6.3 \[S/m\]                | \[7\]                 |
| saline        | 1.76 \[S/m\]                 | \[11\]                |
| perineurium   | 1/1149 \[S/m\]               | \[1,5\]           |

## References
1. Weerasuriya A, Spangler RA, Rapoport SI, Taylor RE. AC impedance of the perineurium of the frog sciatic nerve. Biophys J. 1984 Aug;46(2):167–74. [https://dx.doi.org/10.1016%2FS0006-3495(84)84009-6](https://dx.doi.org/10.1016%2FS0006-3495(84)84009-6)
1. Callister WD, Rethwisch DG. Fundamentals of Material Science and Engineering An Integrated Approach. In: Fundamentals Of Material Science and Engineering An Integrated Approach. 2012.
1. de Podesta M, Laboratory NP, UK. Understanding the Properties of Matter. Understanding the Properties of Matter. 1996.
1. Ranck JB, BeMent SL. The specific impedance of the dorsal columns of cat: An anisotropic medium. Exp Neurol [Internet]. 1965 Apr 1 [cited 2020 Apr 20];11(4):451–63. Available from: [https://doi.org/10.1016/0014-4886(65)90059-2](https://doi.org/10.1016/0014-4886(65)90059-2)
1. Pelot NA, Behrend CE, Grill WM. On the parameters used in finite element modeling of compound peripheral nerves. J Neural Eng [Internet]. 2019;16(1):16007. Available from: [http://dx.doi.org/10.1088/1741-2552/aaeb0c](http://dx.doi.org/10.1088/1741-2552/aaeb0c)
1. Stolinski C. Structure and composition of the outer connective tissue sheaths of peripheral nerve. J Anat [Internet]. 1995 Feb;186 ( Pt 1(Pt 1):123–30. Available from: [https://pubmed.ncbi.nlm.nih.gov/7649808](https://pubmed.ncbi.nlm.nih.gov/7649808)
1. Grill WM, Mortimer TJ. Electrical properties of implant encapsulation tissue. Ann Biomed Eng [Internet]. 1994;22(1):23–33. Available from: [https://doi.org/10.1007/BF02368219](https://doi.org/10.1007/BF02368219)
1. Pelot NA, Behrend CE, Grill WM. Modeling the response of small myelinated axons in a compound nerve to kilohertz  frequency signals. J Neural Eng. 2017 Aug;14(4):46022. Available from: [https://doi.org/10.1088/1741-2552/aa6a5f](https://doi.org/10.1088/1741-2552/aa6a5f)
1. Gielen FLH, Wallinga-de Jonge W, Boon KL. Electrical conductivity of skeletal muscle tissue: Experimental results from different musclesin vivo. Med Biol Eng Comput [Internet]. 1984;22(6):569–77. Available from: [https://doi.org/10.1007/BF02443872](https://doi.org/10.1007/BF02443872)
1. Geddes LA, Baker LE. The specific resistance of biological material—A compendium of data for the biomedical engineer and physiologist. Med Biol Eng [Internet]. 1967;5(3):271–93. Available from: [https://doi.org/10.1007/BF02474537](https://doi.org/10.1007/BF02474537)
1. Horch K. Neuroprosthetics: Theory and practice: Second edition. Neuroprosthetics: Theory and Practice: Second Edition. 2017. 1–925 p.


## Definition of perineurium

The perineurium is a thin highly resistive layer of connective tissue
and has a profound impact on thresholds of activation and block. Our
previous modeling work demonstrates that representing the perineurium
with a thin layer approximation (Rm = rho\*peri\_thk), rather than as a
thinly meshed domain, reduces mesh complexity and is a reasonable
approximation \[1\]. Therefore, perineurium can be modeled with a thin
layer approximation (except with “peanut” fascicles; see an example in
[Fig 2](https://doi.org/10.1371/journal.pcbi.1009285.g002)), termed “contact impedance” in COMSOL (if ***Model’s***
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

## References
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

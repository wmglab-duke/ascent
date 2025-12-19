.. |doi| image:: https://zenodo.org/badge/379064819.svg
   :target: https://zenodo.org/badge/latestdoi/379064819

Welcome to ASCENT's documentation!
==================================

This documentation is an adaptation and update of the supplements associated with the original ASCENT publication.

**Please check out the associated** `publication <https://doi.org/10.1371/journal.pcbi.1009285>`_ **in PLOS Computational Biology!**

**Cite the ASCENT paper, PyFibers paper, and the DOI for the release of the repository used for your work. If you use the neural recording feature or SMALL_MRG_INTERPOLATION model, also cite the neural recording paper. We encourage you to clone the most recent commit of the repository.**

* **Cite the ASCENT paper:**

  .. tab:: APA

    **Musselman, E. D.**, **Cariello, J. E.**, Grill, W. M., & Pelot, N. A. (2021). ASCENT (Automated Simulations to Characterize Electrical Nerve Thresholds): A pipeline for sample-specific computational modeling of electrical stimulation of peripheral nerves. PLOS Computational Biology, 17(9), e1009285. https://doi.org/10.1371/journal.pcbi.1009285.

  .. tab:: BibTeX

    .. code-block:: BibTeX

         @article{Musselman2021,
          doi = {10.1371/journal.pcbi.1009285},
          url = {https://doi.org/10.1371/journal.pcbi.1009285},
          year = {2021},
          month = sep,
          publisher = {Public Library of Science ({PLoS})},
          volume = {17},
          number = {9},
          pages = {e1009285},
          author = {Eric D. Musselman and Jake E. Cariello and Warren M. Grill and Nicole A. Pelot},
          editor = {Dina Schneidman-Duhovny},
          title = {{ASCENT} (Automated Simulations to Characterize Electrical Nerve Thresholds): A pipeline for sample-specific computational modeling of electrical stimulation of peripheral nerves},
          journal = {{PLOS} Computational Biology}
        }

* **Cite the PyFibers paper:**

  .. tab:: APA

    Marshall, D. P., Farah, E. S., Musselman, E. D., Pelot, N. A., & Grill, W. M. (2025). PyFibers: An open-source NEURON-Python package to simulate responses of model nerve fibers to electrical stimulation. PLOS Computational Biology, 21(12), e1013764. https://doi.org/10.1371/journal.pcbi.1013764

  .. tab:: BibTeX

    .. code-block:: BibTeX

        @article{Marshall2025,
          title = {PyFibers: An open-source NEURON-Python package to simulate responses of model nerve fibers to electrical stimulation},
          volume = {21},
          ISSN = {1553-7358},
          url = {http://dx.doi.org/10.1371/journal.pcbi.1013764},
          DOI = {10.1371/journal.pcbi.1013764},
          number = {12},
          journal = {PLOS Computational Biology},
          publisher = {Public Library of Science (PLoS)},
          author = {Marshall,  Daniel P. and Farah,  Elie S. and Musselman,  Eric D. and Pelot,  Nicole A. and Grill,  Warren M.},
          editor = {Nogaret,  Alain},
          year = {2025},
          month = dec,
          pages = {e1013764}
        }

* **Cite the neural recording paper:**

  .. tab:: APA

     Peña, E., Pelot, N. A., & Grill, W. M. (2024). Computational models of compound nerve action potentials: Efficient filter-based methods to quantify effects of tissue conductivities, conduction distance, and nerve fiber parameters. PLoS computational biology, 20(3), e1011833. https://doi.org/10.1371/journal.pcbi.1011833.

  .. tab:: BibTeX

    .. code-block:: BibTeX

        @article{Peña2024,
          doi = {10.1371/journal.pcbi.1011833},
          url = {https://doi.org/10.1371/journal.pcbi.1011833},
          year = {2024},
          month = mar,
          publisher = {Public Library of Science ({PLoS})},
          volume = {20},
          number = {3},
          pages = {e1011833},
          author = {Edgar Peña and Nicole A. Pelot, and Warren M. Grill},
          editor = {Kim T. Blackwell},
          title = {Computational models of compound nerve action potentials: Efficient filter-based methods to quantify effects of tissue conductivities, conduction distance, and nerve fiber parameters},
          journal = {{PLOS} Computational Biology}
        }

* **Cite the code (use the DOI for the version of code used):** |doi|

  .. tab:: APA

     **Musselman, E. D.**, **Cariello, J. E.**, Grill, W. M., & Pelot, N. A. (2025). wmglab-duke/ascent: ASCENT v1.5.0 (v1.5.0) [Computer software]. Zenodo. https://doi.org/10.5281/ZENODO.10608262.

  .. tab:: BibTeX

    .. code-block:: BibTeX

        @misc{https://doi.org/10.5281/zenodo.10608262,
          doi = {10.5281/ZENODO.10608262},
          url = {https://zenodo.org/record/10608262},
          author = {Musselman,  Eric D and Cariello,  Jake E and Grill,  Warren M and Pelot,  Nicole A},
          title = {wmglab-duke/ascent: ASCENT v1.5.0},
          publisher = {Zenodo},
          year = {2025},
          copyright = {MIT License}
        }

**ASCENT** is an open source platform for simulating peripheral nerve stimulation. To download the software, visit the `ASCENT GitHub repository <https://github.com/wmglab-duke/ascent>`_.

..  youtube:: rG-KU7wWcXY

.. toctree::
   :maxdepth: 2
   :caption: Basic ASCENT Usage

   Getting_Started
   Running_ASCENT/index
   JSON/index
   Publishing_with_ASCENT/index

.. toctree::
   :maxdepth: 2
   :caption: Advanced ASCENT Usage

   MockSample
   Primitives_and_Cuffs/index
   Modeling_Neural_Recording
   Convergence_Example
   Troubleshooting-Guide

.. toctree::
   :maxdepth: 2
   :caption: ASCENT Hierarchies

   Code_Hierarchy/index
   Data_Hierarchy

.. toctree::
   :maxdepth: 2
   :caption: Reference

   Publications_Using_ASCENT
   references
   Validation
   Changelog

.. toctree::
   :maxdepth: 2
   :caption: External Links

   ASCENT Publication <https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1009285>
   ASCENT on GitHub <https://github.com/wmglab-duke/ascent>
   The Grill Lab <https://grill-lab.pratt.duke.edu>
   NIH SPARC <https://commonfund.nih.gov/sparc>

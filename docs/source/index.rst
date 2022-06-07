.. ASCENT documentation master file, created by
   sphinx-quickstart on Fri Sep 17 12:12:45 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. |doi| image:: https://zenodo.org/badge/379064819.svg
   :target: https://zenodo.org/badge/latestdoi/379064819

Welcome to ASCENT's documentation!
==================================
**Please check out the associated** `publication <https://doi.org/10.1371/journal.pcbi.1009285>`_ **in PLOS Computational Biology!**

**Cite both the paper and the DOI for the release of the repository used for your work. We encourage you to clone the most recent commit of the repository.**

Note: Here add copy button, and other citation types including bibtex. Might want to add whole citation page.
Note also add copy button to json configs
Note I also think these citations should be changed to APA?
Also need to rewrite tutorial text
Also need to get toctree maxdepth working on subpages

* **Cite the paper:**
    **Musselman ED**, **Cariello JE**, Grill WM, Pelot NA. ASCENT (Automated Simulations to Characterize Electrical Nerve Thresholds): A
    Pipeline for Sample-Specific Computational Modeling of Electrical Stimulation of Peripheral Nerves. PLoS Comput Biol [Internet]. 2021;
    Available from: https://doi.org/10.1371/journal.pcbi.1009285


* **Cite the code (use the DOI for the version of code used):** |doi|
    **Musselman ED**, **Cariello JE**, Grill WM, Pelot NA. ASCENT (Automated Simulations to Characterize Electrical Nerve Thresholds): A
    Pipeline for Sample-Specific Computational Modeling of Electrical Stimulation of Peripheral Nerves. PLoS Comput Biol [Internet]. 2021,
    DOI: 10.5281/zenodo.5500260

**ASCENT** is an open source platform for simulating peripheral nerve stimulation. To download the software, visit the `ASCENT GitHub repository <https://github.com/wmglab-duke/ascent>`_.

.. image:: uploads/ascent_media_release_v2.png



.. toctree::
   :maxdepth: 2
   :caption: Basic ASCENT Usage

   Getting_Started
   Running_ASCENT/index
   JSON/index
   Methods_Template

.. toctree::
   :maxdepth: 2
   :caption: Advanced ASCENT Usage

   MockSample
   Primitives_and_Cuffs/index
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

.. toctree::
   :maxdepth: 2
   :caption: External Links

   ASCENT Publication <https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1009285>
   ASCENT on GitHub <https://github.com/wmglab-duke/ascent>
   The Grill Lab <https://www.neuro.duke.edu/research/faculty-labs/grill-lab>

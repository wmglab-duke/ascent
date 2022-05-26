Command-Line Arguments
***********************
Note: In cases where a behavior can be controlled by both a command line argument, and a configuration file (.json file), the command line argument will ALWAYS take precedence.
run
---

.. argparse::
   :filename: ../../config/system/run_utils/parse_args.py
   :func: parser
   :prog: run

submit.py
---------

.. argparse::
   :filename: ../../src/neuron/submit.py
   :func: parser
   :prog: submit.py

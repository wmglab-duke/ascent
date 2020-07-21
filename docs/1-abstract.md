# 1 ABSTRACT

## 1.1 Background
The design and development of technologies for electrical stimulation of peripheral nerves will benefit from anatomically realistic biophysical models. The relationship between applied electrical signals and the complement of nerve fibers that are activated or blocked, how this relationship varies across individuals and species, and how this relationship can be controlled present important challenges to the field of neuromodulation. The exceedingly large stimulation parameter space and nonlinear input-output relationships between applied stimulation and neural response make optimizing the system for therapeutic outcomes in vivo unrealistic. To complement in vivo studies, biophysical modeling enables use of numerical methods to solve complex nonlinear problems efficiently, allowing exploration of this parameter space and rigorous optimization to define application-specific parameters. Our pipeline will help interpret and communicate more precisely the mechanisms of therapeutic effects of autonomic nerve stimulation.

## 1.2 Objective
Herein we describe our ASCENT modeling pipeline of autonomic nerve stimulation that serves as a standardized, modular, and scalable framework for the research community to make informed decisions of stimulation parameters and cuff designs to modulate selectively distinct fibers in novel applications.

## 1.3 Methods
Integration of multiple software tools (Python, Java, COMSOL, and NEURON) simulates the response of fibers within individual-specific nerve samples to electrical stimulation with standard or custom electrode designs. The nerve morphology is specified by segmented histology or by user-defined nerve and fascicles sizes and locations. The pipeline includes a suite of built-in capabilities for programmatic user control over the entire workflow, and its expandable design enables the user to develop additional tools to pursue their own research questions. For example, the pipeline includes libraries for: COMSOL parts to assemble stimulation electrodes, electrical properties of biological materials, previously published fiber models implemented in NEURON, and commonly-used stimulation waveforms.

## 1.4 Conclusion
Computational modeling of sample-specific peripheral nerve stimulation is a complex, multi-step process that requires highly detailed parameterization to enable reproducibility, performance of sensitivity analyses, and model-based design. We present tools that empower researchers to model the responses of their own nerve samples to electrical stimulation with an automated process.
 

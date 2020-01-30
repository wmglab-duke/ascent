: Author: David Catherall
: Created: November 2016
: Extracellular potassium ion accumulation
: Adapted from Hines and Carnevale 2000: Guide to NMODL
: Upon further inspection, this doesn't appear in Schild 1994. Saving for furture use if needed.
NEURON {
  SUFFIX kext
  USEION k READ ik WRITE ko
  GLOBAL kbath
  RANGE fhspace, txfer
}
UNITS {
  (mV)    = (millivolt)
  (mA)    = (milliamp)
  FARADAY = (faraday) (coulombs)
  (molar) = (1/liter)
  (mM)    = (millimolar)
}
PARAMETER {
  kbath   =  5.4 (mM)        : seawater (squid axon!)
  fhspace = 1e-4 (cm)  :Thickness of Shell
  txfer   =  50 (ms)  : tau for F-H space <-> bath exchange = 30-100
}
ASSIGNED { ik  (mA/cm2) }
STATE { ko  (mM) }
BREAKPOINT { SOLVE state METHOD cnexp }
DERIVATIVE state {
  ko' = ik/(fhspace*FARADAY) + (kbath - ko)/txfer
}
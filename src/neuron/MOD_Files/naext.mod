: Author: David Catherall
: Created: November 2016
: Extracellular potassium ion accumulation
: Upon further inspection, this doesn't appear in Schild 1994. Saving for furture use if needed.
NEURON {
  SUFFIX naext
  USEION na READ ina WRITE nao
  GLOBAL nabath
  RANGE fhspace, txfer
}
UNITS {
  (mV)    = (millivolt)
  (mA)    = (milliamp)
  FARADAY = 96500 (coulombs)
  (molar) = (1/liter)
  (mM)    = (millimolar)
}
PARAMETER {
  nabath   =  154 (mM)        : Given in Schild 1994
  fhspace = 1e-4 (cm)  : Thickness of Shell
  txfer   =  50 (ms)  : tau for F-H space <-> bath exchange = 30-100
}
ASSIGNED { ina  (mA/cm2) }
STATE { nao  (mM) }
BREAKPOINT { SOLVE state METHOD cnexp }
DERIVATIVE state {
  nao' = ina/(fhspace*FARADAY) + (nabath - nao)/txfer
}
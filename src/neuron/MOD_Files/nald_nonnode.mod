NEURON {
  SUFFIX nald_nonnode
  USEION na READ nao, ina WRITE nao
  GLOBAL nabath
  RANGE fhspace, txfer, Vol_peri, L, nseg, SA, Volratio, lseg, A_peri		:Allows variables to be modified in hoc and collected in vectors
}
UNITS {
  (mV)    = (millivolt)
  (mA)    = (milliamp)
  FARADAY = 96485 (coulombs)
  :FARADAY = (faraday) (10000 coulomb)
  (molar) = (1/liter)
  (mM)    = (millimolar)
  PI      = (pi) (1)
  (um)    = (micrometer)
}
PARAMETER {
  txfer   =  50 (ms)  : tau for F-H space <-> bath exchange = 30-100
  :D = 1.85 (um2/ms) : m2s-1
  D = 1.15 (um2/ms)
  nabath = 154 (mM)
  fhspace = 2 (um)
}
ASSIGNED {
  ina (mA/cm2)
  Vol_peri (cm3)
  A_peri (um2)
  SA 			(cm2)
  diam		(um)
  nseg		(1)
  L			  (um)
  lseg		(cm)
  Vol			(cm3)
}
STATE { nao  (mM) }
BREAKPOINT { SOLVE state METHOD sparse }
INITIAL {
		lseg=(1e-4)*L/nseg
		SA = PI*(1e-4)*diam*lseg
		Vol = (PI*((1e-4)*(diam/2))^2*lseg)
		Vol_peri = (PI*((1e-4)*((diam+fhspace)/2))^2*lseg)-Vol
    :A_peri = 2*diam*fhspace*PI - fhspace*fhspace*PI
    A_peri = 2*diam*fhspace/4*PI + fhspace*fhspace/4*PI
		:Vol_peri = Vol * Volratio
	}

:Defines Governing Equations for State Variables
KINETIC state{
  COMPARTMENT i, A_peri {nao}
  LONGITUDINAL_DIFFUSION i, D * A_peri {nao}
  ~ nao << ((10000)*ina*PI*diam/(FARADAY))
}

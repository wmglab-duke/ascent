TITLE na ion dynamics

COMMENT
#-*-#
### na_ion_dynamics - naoi
------------------------------
Mechanism for controlling Na ion concentrations. This mechanism reads Ina and writes to the nao and nai ion pools.
#-*-#
ENDCOMMENT


NEURON {
    SUFFIX naoi
    USEION na READ ina WRITE nai, nao
    RANGE naiinf, naoinf
}

UNITS {
    (molar)	= (1/liter)			: moles do not appear in units
    (mM)	= (millimolar)
    (um)	= (micron)
    (mA)	= (milliamp)
    FARADAY	= (faraday) (coulombs)
}

PARAMETER {
    naiinf	= 11.4		(mM)		: 63.4
    naoinf	= 154.0		(mM)
    theta	= 14.5e-3	(um)
    D		= 0.1e-6 	(m/s)			: Scriven1981
}

ASSIGNED {
    ina				(mA/cm2)
    diam			(um)
}

STATE {
    nai				(mM)
    nao				(mM)
}

INITIAL {
    nai		= naiinf
    nao		= naoinf
}

BREAKPOINT {
    SOLVE state METHOD cnexp
}

DERIVATIVE state {
    nai'	= -ina*4/FARADAY/diam*(1e4)
    nao'	= (ina/FARADAY - D*(0.1)*(nao - naoinf))/theta*(1e4)
}
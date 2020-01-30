TITLE K ion dynamics with pointer

COMMENT
#-*-#
### k_ion_dynamics - koi
------------------------
Mechanism for controlling K ion concentrations. This mechanism reads Ik and writes to the ki and ko ion pools.
#-*-#
ENDCOMMENT

NEURON {
    SUFFIX koi
    USEION k READ ik WRITE ki, ko
    RANGE kiinf, koinf
}

UNITS {
    (molar)	= (1/liter)			: moles do not appear in units
    (mM)	= (millimolar)
    (um)	= (micron)
    (mA)	= (milliamp)
    FARADAY	= (faraday) (coulombs)
}

PARAMETER {
    kiinf	= 121.7		(mM) : 144.9
    koinf	= 5.6   	(mM)
    theta	= 14.5e-3	(um)
    D		= 0.1e-6 	(m/s)			: Scriven1981
}

ASSIGNED {
    ik				(mA/cm2)
    diam			(um)
}

STATE {
    ki				(mM)
    ko				(mM)
}

INITIAL {
    ki		= kiinf
    ko		= koinf
}

BREAKPOINT {
    SOLVE state METHOD cnexp
}

DERIVATIVE state {
    ki'		= -ik*4/FARADAY/diam*(1e4)
    ko'		= (ik/FARADAY - D*(0.1)*(ko - koinf))/theta*(1e4)
}
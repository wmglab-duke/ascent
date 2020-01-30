: Sodium-dependent potassium current
: Paramaters according to Wang et al. 2003 (based on Bischoff et al. 1998)

NEURON {
	SUFFIX kna
	USEION na READ nai
	USEION k READ ek WRITE ik
	RANGE gbar, ik
}

UNITS {
        (molar)	= (1/liter)                     : moles do not appear in units
        (mM)	= (millimolar)             	
	(mA)	= (milliamp)
	(mV)	= (millivolt)
	(S) 	= (siemens)

}

PARAMETER {
:	nain = 11.4 	(mM)
:	kout = 5.6 	(mM)

:	gbar = 0  	(S/cm2)
	EC50 = 38.7  	(mM)
	pmax = 0.37
	nH = 3.5

}

ASSIGNED {
	v (mV)
	ek (mV)
	ik (mA/cm2)
	nai (mM)
	gbar (S/cm2)
}

STATE {	w }


INITIAL {
	w = pmax/(1+(EC50/nai)^nH)
	ik = gbar*w*(v-ek)
}

BREAKPOINT {
	w = pmax/(1+(EC50/nai)^nH)
	ik = gbar*w*(v-ek)
}




TITLE leak

NEURON {
	SUFFIX leak
	USEION k READ ek WRITE ik
	USEION na READ ena WRITE ina
	RANGE gkleak, gnaleak, gk, qna, ik, ina
}

UNITS { 
	(mV) = (millivolt)  (mA) = (milliamp)
	(um) = (micron)
	PI		= (pi) (1)
	FARADAY		= 96485.309 (coul)
}

PARAMETER {
:	gkleak	= 1e-5 (mho/cm2)
:	gnaleak	= 1e-5 (mho/cm2)
	gkleak	= 0 (mho/cm2)
	gnaleak	= 0 (mho/cm2)
	:gcl	= 1e-4 (mho/cm2)
	:ga	= 0 (mho/cm2)
}

ASSIGNED {
	v (mV)
	ik (mA/cm2)
	ek (mV)
	ina (mA/cm2)
	ena (mV)

}

BREAKPOINT {

	ik = gkleak*(v-ek)
	ina = gnaleak*(v-ena)

}


INITIAL {
	ik = gkleak*(v-ek)
	ina = gnaleak*(v-ena)
}


: Chapman JB, Johnson EA, Kootsey JM. (1983)
: Electrical and Biochemical Properties of an Enzyme Model of the Sodium Pump
: J. Membrane Biol. 74, 139-153

: note default step 5 voltage dependence

: extended by Michael Hines as a component of larger models.
: I.e. modifies nai, ki, contributes to ina, ik, and consumes atp
: for investigation of isolated pump, allow clamping of
: nai, ki, atp (note p and adp are constant here)
: initialize to steady state pump with nai, ki, atp clamped.

NEURON {
	SUFFIX nakpump
	USEION na READ nai WRITE ina
	USEION k READ ko WRITE ik
	RANGE ik, ina
	RANGE nain, naout, kin, kout, smalla, b1, b2, celsiusT, kvotqt
}

UNITS {
        (molar) = (1/liter)                     : moles do not appear in units
        (mM)    = (millimolar)             	
	
	(uA) = (microamp)
	(mA) = (milliamp)
	(mV) = (millivolt)
	(um) = (micron)

}

PARAMETER {
:	nain = 63.4 (mmol/l)
:	kout = 5.6 (mmol/l)
	nain = 11.4 	(mM)
	kout = 5.6 	(mM)

	smalla = 0  	(mA/cm2)
	b1 = 1  	(mM)
:	b1 = 0.5  	(mM) :testing for disp
	:b2 = 30  	(mM)
	
	kvotqt

}

ASSIGNED {

	ina (mA/cm2)
	ik (mA/cm2)

	nai (mM)
	ko (mM)

	celsiusT
}

STATE {
	inapump  (mA/cm2)
	ikpump (mA/cm2)	

}


INITIAL {

	inapump = 0
	ikpump = 0

}

BREAKPOINT {

:	kvotqt = 2.1^((celsiusT-22)/10)
	kvotqt = 1^((celsiusT-22)/10)

	ikpump = smalla/((1+b1/ko)^2) * (1.62/(1+(6.7(mM)/(nai+8(mM)))^3) + 1.0/(1+(67.6(mM)/(nai+8(mM)))^3))
	ikpump = ikpump*kvotqt
	inapump = -1.5*ikpump

	ina = inapump		
	ik = ikpump		

}



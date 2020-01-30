TITLE l-calcium channel
: l-type calcium channel - Milgiore et al. 1995


UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)

	F = (faraday) (coulomb)
	R = (k-mole) (joule/degC)
	TEMP = 25 (degC)
}

PARAMETER {
	v (mV)
	celsius 	(degC)
	gcalbar=.003 (mho/cm2)
	ki=.001 (mM)
	ca0 = .00007	(mM)		: initial calcium concentration inside
	cao = 2		(mM)		: calcium concentration outside
        tfa=1
}


NEURON {
	SUFFIX cal
	USEION ca WRITE ica
        RANGE gcalbar, gcal, m
        GLOBAL minf,tau
}

STATE {
	m ca_i (mM)
}

ASSIGNED {
	ica (mA/cm2)
        gcal (mho/cm2)
        minf
        tau   (ms)
	e_ca  (mV)
}

INITIAL {
	ca_i = ca0
	rate(v)
	m = minf
}

BREAKPOINT {
	SOLVE state METHOD cnexp
	e_ca = (1000)*(TEMP+273.15)*R/(2*F)*log(cao/ca_i)
	gcal = gcalbar*m*m
	ica = gcal*(v-e_ca)

}


FUNCTION efun(z) {
	if (fabs(z) < 1e-4) {
		efun = 1 - z/2
	}else{
		efun = z/(exp(z) - 1)
	}
}

FUNCTION alp(v(mV)) (1/ms) {
	TABLE FROM -150 TO 150 WITH 200
	alp = 15.69*(-1.0*v+81.5)/(exp((-1.0*v+81.5)/10.0)-1.0)
}

FUNCTION bet(v(mV)) (1/ms) {
	TABLE FROM -150 TO 150 WITH 200
	bet = 0.29*exp(-v/10.86)
}

DERIVATIVE state {  
        rate(v)
        m' = (minf - m)/tau
}

PROCEDURE rate(v (mV)) { :callable from hoc
        LOCAL a
        a = alp(v)
        tau = 1/(tfa*(a + bet(v)))
        minf = tfa*a*tau
}
 
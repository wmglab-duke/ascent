TITLE slowly activating potassium current (M-current)

COMMENT
        *********************************************
        reference:   	Yamada, Koch & Adams (1989) 
			Methods in Neuronal Modeling, MIT press
        found in:       bullfrog sympathetic ganglion cells
        *********************************************
	Assembled for MyFirstNEURON by Arthur Houweling
ENDCOMMENT

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
	SUFFIX iM
	USEION k READ ek WRITE ik 
        RANGE gkbar, ikim, m_inf, tau_m, m, vshift
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

PARAMETER {
	v		(mV)
	celsius		(degC)
        dt              (ms)
	ek		(mV)
	gkbar= 0.00031	(mho/cm2)
	vshift = 0 	(mV)
}

STATE {
	m
}

ASSIGNED {
	ik		(mA/cm2)
	m_inf
	tau_m		(ms)
	tau_h		(ms)
	tadj
	ikim		(mA/cm2)
}

BREAKPOINT { 
	SOLVE states :METHOD euler
	ik = gkbar * m * (v-ek)
	ikim = ik
}

:DERIVATIVE states {
:       evaluate_fct(v)
:
:       m'= (m_inf-m) / tau_m 
:}
  
PROCEDURE states() {
        evaluate_fct(v+vshift)

        m= m + (1-exp(-dt/tau_m))*(m_inf-m)
}

UNITSOFF
INITIAL {
	tadj = 3^((celsius-23.5)/10)
	evaluate_fct(v+vshift)
	m = m_inf
}

PROCEDURE evaluate_fct(v(mV)) {  LOCAL a,b
	tau_m = 1000.0/(3.3*(exp((v+35)/20)+exp(-(v+35)/20))) / tadj
	m_inf = 1.0 / (1+exp(-(v+35)/10))
}
UNITSON

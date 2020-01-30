TITLE Gaines Motor Axon Internode channels

: 2/02
: Cameron C. McIntyre
:
: Fast Na+, Persistant Na+, Slow K+, and Leakage currents 
: responsible for nodal action potential
: Iterative equations H-H notation rest = -80 mV
:
: This model is described in detail in:
:
: McIntyre CC, Richardson AG, and Grill WM. Modeling the excitability of
: mammalian nerve fibers: influence of afterpotentials on the recovery
: cycle. Journal of Neurophysiology 87:995-1006, 2002.

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
	SUFFIX gaines_internode_mysa
	NONSPECIFIC_CURRENT ikf
	NONSPECIFIC_CURRENT ik : Slow potassium
	NONSPECIFIC_CURRENT ihcn : HCN channel
	NONSPECIFIC_CURRENT il
	RANGE gkbar, gl, gkfbar, ghcnbar, ena, ek, el, eq
	RANGE s_inf, n_inf, q_inf	: gating variables, s -> slow potassium, n -> fast potassium, q -> HCN
	RANGE tau_s, tau_n, tau_q
}


UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

PARAMETER {

	gkbar   = 0.002581 	(mho/cm2)
	gkfbar = 0.15074	(mho/cm2)	: Different between flut and mysa/stin
	gl	= 0.002 (mho/cm2)	: Different between flut and mysa/stin
	ghcnbar = 0.002232
	ek  = -90.0 (mV)
	el	= -80 (mV):-90.0 (mV)
	eq = -54.9	(mV)
	celsius		(degC)
	dt              (ms)
	v               (mV)
	vtraub=-80

	anA = 0.0462
	anB = -83.2
	anC = 1.1
	bnA = 0.0824
	bnB = -66
	bnC = 10.5
	asA = 0.3
	asB = -27
	asC = -5
	bsA = 0.03
	bsB = 10
	bsC = -1
	aqA = 0.00522
	aqB = -107.3
	aqC = -12.2
	bqA = 0.00522
	bqB = -107.3
	bqC = -12.2
}

STATE {
	s n q
}

ASSIGNED {
	ik      (mA/cm2)
	ikf		(mA/cm2)
	ihcn	(mA/cm2)
	il      (mA/cm2)
	n_inf
	s_inf
	q_inf
	tau_n
	tau_s
	tau_q
	q10
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	ik   = gkbar * s * (v - ek)
	ikf = gkfbar * n*n*n*n * (v-ek)
	ihcn = ghcnbar * q * (v-eq)
	il   = gl * (v - el)
}

DERIVATIVE states {   : exact Hodgkin-Huxley equations
    evaluate_fct(v)
	s' = (s_inf - s) / tau_s
	n' = (n_inf - n) / tau_n
	q' = (q_inf - q) / tau_q
}

UNITSOFF

INITIAL {	LOCAL t_howells
:
:	Q10 adjustment
:	According to Howells 2012, s n q have Q10 of 3
:
	t_howells = 34 :Temperature for Howells measurements, for Q10 conversion

	q10 = 3.0 ^ ((celsius-t_howells)/ 10 )

	evaluate_fct(v)
	s = s_inf
	n = n_inf
	q = q_inf
}

PROCEDURE evaluate_fct(v(mV)) { LOCAL a,b,v2

	a = q10*vtrap1(v)
	b = q10*vtrap2(v)
	tau_s = 1 / (a + b)
	s_inf = a / (a + b)

	a = q10*vtrap3(v)
	b = q10*vtrap4(v)
	tau_n = 1 / (a + b)
	n_inf = a / (a + b)

	a = q10*vtrap5(v)
	b = q10*vtrap6(v)
	tau_q = 1 / (a + b)
	q_inf = a / (a + b)

	v2 = v - vtraub : convert to traub convention
}

:FUNCTION vtrap(x) {
:	if (x < -50) {
:		vtrap = 0
:	}else{
:		vtrap = bsA / (Exp((x+bsB)/bsC) + 1)
:	}
:}

FUNCTION vtrap1(x) {
	:Alpha s gating
	vtrap1 = asA/(Exp((x+asB)/asC) + 1)
}

FUNCTION vtrap2(x) {
	:Beta s gating
	vtrap2 = bsA/(Exp((x+bsB)/bsC) + 1)
}

FUNCTION vtrap3(x) {
	:Alpha n gating
	vtrap3 = anA * (x-anB) / (1 - Exp((anB-x)/anC))
}

FUNCTION vtrap4(x) { 
	:Beta n gating
	vtrap4 = bnA * (bnB-x) / (1 - Exp((x-bnB)/bnC))
}

FUNCTION vtrap5(x) { 
	:Alpha hcn (q) gating
	vtrap5 = aqA * Exp((x-aqB)/aqC)
}

FUNCTION vtrap6(x) {
	:Beta hcn (q) gating
	vtrap6 = bqA / Exp((x-bqB)/bqC)
}

FUNCTION Exp(x) {
	if (x < -100) {
		Exp = 0
	}else{
		Exp = exp(x)
	}
}

UNITSON
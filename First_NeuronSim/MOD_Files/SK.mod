
:  SK model based on Aradi and Holmes 1999
:
:

NEURON {
	SUFFIX SK
	USEION ca READ ica
	USEION k READ ek WRITE ik
	RANGE gskbar, cal, gsk, sstau, cascale
	GLOBAL ca0, stau
}

UNITS {
	(molar) = (1/liter)
	(mM) = (millimolar)
	(mV) = (millivolt)
	(mA) = (milliamp)
	(S) = (siemens)
}

PARAMETER {
	gskbar = .01	(S/cm2)	: maximum permeability
	ca0 = .00007	(mM)
	sstau = 20		(ms)
	alphar = 7.5	(/ms)
	stau = 10		(ms)
	cal = 0 (mM)
	cascale = .1     ()
	B = .26 (mM-cm2/mA-ms)
}

ASSIGNED {
	v		(mV)
	ek		(mV)
	ik		(mA/cm2)
	ica		(mA/cm2)
	area		(microm2)
      gsk		(S/cm2)
}

STATE { ca_i (mM) q }

BREAKPOINT {
	SOLVE state METHOD cnexp
	gsk = gskbar*q*q
	ik = gsk*(v - ek)
	cal = ca_i*1e3
}

DERIVATIVE state {	: exact when v held constant; integrates over dt step
	ca_i' = -B*cascale*ica-(ca_i-ca0)/sstau
	q' = alphaq(ca_i*1e3)*(1-q)-betaq(ca_i*1e3)*q
}

INITIAL {
	ca_i = ca0
	q = alphaq(ca_i*1e3)/(alphaq(ca_i*1e3)+betaq(ca_i*1e3))
}

FUNCTION exp1(A (/ms), d, k, x (mM)) (/ms) {
	UNITSOFF
	exp1 = A/exp((12*log10(x)+d)/k)
	UNITSON
}

FUNCTION alphaq(x (mM)) (/ms) {
	alphaq = exp1(0.00246,28.48,-4.5,x^3)
}

FUNCTION betaq(x (mM)) (/ms) {
	betaq = exp1(0.006,60.4,35,x^3)
}


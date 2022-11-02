: This channels is implemented by Jenny Tigerholm.
:The steady state curves are collected from Winkelman 2005
:The time constat is from Gold 1996 and Safron 1996
: To plot this model run KA_Winkelman.m
: Adopted and altered by Nathan Titus

NEURON {
	SUFFIX ka34
	USEION k READ ek WRITE ik
	RANGE gbar, ek, ik
	RANGE tau_m, minf, hinf,tau_h,m,h
	RANGE minfshift, hinfshift, mtaushift, htaushift, ik
}

UNITS {
	(S) = (siemens)
	(mV) = (millivolts)
	(mA) = (milliamp)
}

PARAMETER {
	gbar 	(S/cm2)

    minfshift = 0 (mV)
	hinfshift = 0 (mV)
	mtaushift = 0 (ms)
	htaushift = 0 (ms)
}

ASSIGNED {
	v	(mV) : NEURON provides this
	ik	(mA/cm2)
	g	(S/cm2)
	tau_m	(ms)
    tau_h   (ms)
    minf
    hinf
    ek	(mV)
	celsius (degC)
}

STATE { h m }

BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar*m*h
	ik = g * (v-ek)
}

INITIAL {
	: assume that equilibrium has been reached
    rates(v)
	m=minf
    h=hinf

}

DERIVATIVE states {
	rates(v)
	m' = (minf - m)/tau_m
    h' = (hinf - h)/tau_h

}

FUNCTION rates(Vm (mV)) (/ms) {
		LOCAL q10
		q10 = 3^((celsius-22)/10)
        :minf=1/(1+exp(-1*(v+16.8-minfshift)/20.7))
		minf=1/(1+exp(-1*(v-28-minfshift)/25.3))
        :hinf=1/(1+exp((v+74-hinfshift)/14))
		hinf=1/(1+exp((v+29-hinfshift)/8))
        :tau_m=6.09/(exp((v+33.64)/6.7)+exp(-1*(v+46.6)/14.71)) + 2.5/(1+exp((v-26.2)/21.55))
        tau_m=0.66 + 1/(0.13*exp((v-mtaushift)/13.0) + 0.04*exp(-1*(v-mtaushift)/39.3))
		:tau_h= 1*(4 + 82.59/(exp((v+83.39)/9.046)^2 + exp(-1*(v+101.6)/30)) + 15/(1+exp((v+42.58)/20.79)))
		tau_h=15+22.7*exp(-1*(v-htaushift)/24.8)

        tau_m=tau_m/q10
        tau_h=tau_h/q10

}

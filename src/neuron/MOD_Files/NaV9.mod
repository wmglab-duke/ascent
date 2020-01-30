: This channels is implemented by Jenny Tigerholm. 
:The steady state curves are collected from Winkelman 2005 
:The time constat is from Gold 1996 and Safron 1996
: To plot this model run KA_Winkelman.m
: Adopted and altered by Nathan Titus

NEURON {
	SUFFIX NaV9
	USEION na READ ena WRITE ina
	RANGE gbar, ena, ina
	RANGE tau_m, minf, hinf,tau_h, sinf, tau_s, m,h,s
	RANGE minfshift, hinfshift, mtaushift, htaushift, ina
	RANGE sinfshift, staushift
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
	sinfshift = 0 (mV)
	mtaushift = 0 (ms)
	htaushift = 0 (ms)
	staushift = 0 (ms)
}

ASSIGNED {
	v	(mV) : NEURON provides this
	ina	(mA/cm2)
	g	(S/cm2)
	tau_m	(ms)
    tau_h   (ms)
	tau_s
    minf
    hinf
	sinf
    ena	(mV)
	celsius (degC)
}

STATE { h m s}

BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar*m*h*s
	ina = g * (v-ena)
}

INITIAL {
	: assume that equilibrium has been reached
    rates(v)    
	m=minf
    h=hinf
	s=sinf

}

DERIVATIVE states {
	rates(v)
	m' = (minf - m)/tau_m
    h' = (hinf - h)/tau_h
	s' = (sinf - s)/tau_s
          
}

FUNCTION rates(Vm (mV)) (/ms) {    
		LOCAL q10
		q10 = 3^((celsius-22)/10)
        minf = 1/(1+exp(-1*(v+63)/7.4))
		hinf = 1/(1+exp((v+61)/9))
		sinf = 1/(1+exp((v+88)/7.2))
		tau_m = .11+33/(exp((v+77)/13.9)+exp(-1*(v+48)/14.8))+1.18/(1+exp(-1*(v+73)/7.8))
		tau_h = 3.67+27.6/(exp((v+23)/17.4)+exp(-1*(v+100)/17.7))+7.8/(1+exp((v+48)/11.5))
		tau_s = 2042/(exp((v+57)/16.1)+exp(-1*(v+112)/12.7))+2657/(1+exp(-1*(v+95)/7))
		
        tau_m=tau_m/q10
        tau_h=tau_h/q10
        tau_s=tau_s/q10

}
: This channels is implemented by Jenny Tigerholm. 
:The steady state curves are collected from Winkelman 2005 
:The time constat is from Gold 1996 and Safron 1996
: To plot this model run KA_Winkelman.m
: Adopted and altered by Nathan Titus

NEURON {
	SUFFIX ka14
	USEION k READ ek WRITE ik
	RANGE gbar, ek, ik
	RANGE tau_m,minf,hinf1,tau_h1,hinf2,tau_h2,m,h1,h2
	RANGE minfshift, hinf1shift, hinf2shift, ik
}

UNITS {
	(S) = (siemens)
	(mV) = (millivolts)
	(mA) = (milliamp)
}

PARAMETER {
	gbar 	(S/cm2) 
        
    minfshift = 0 (mV)
	hinf1shift = 0 (mV)
	hinf2shift = 0 (mV)
}

ASSIGNED {
	v	(mV) : NEURON provides this
	ik	(mA/cm2)
	g	(S/cm2)
	tau_m	(ms)
    tau_h1  (ms)
	tau_h2  (ms)
    minf
    hinf1
	hinf2
    ek	(mV)
	celsius (degC)
}

STATE { h1 h2 m }

BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar*m*h1*h2
	ik = g * (v-ek)
}

INITIAL {
	: assume that equilibrium has been reached
    rates(v)    
	m=minf
    h1=hinf1
	h2=hinf2

}

DERIVATIVE states {
	rates(v)
	m' = (minf - m)/tau_m
    h1' = (hinf1 - h1)/tau_h1
	h2' = (hinf2 - h2)/tau_h2
          
}

FUNCTION rates(Vm (mV)) (/ms) {    
		LOCAL q10
		q10 = 3^((celsius-22)/10)
        minf=1/(1+exp(-1*(v+25)/12))
        hinf1=.073 + 0.924/(1+exp((v+47)/4.75))
        hinf2 = .415 + .576/(1+exp((v+44.5)/5.93)) + .103/(1+exp(-1*(v)/18.37))
        tau_m = 2*(.6 + 2748/(exp((v+138)/14.5)+exp(-1*(v+20)/8))+1.7/(1+exp((v+18.5)/10.65)))
        :tau_h1 = 87 + 11.22/(exp((v+21.4)/9.48)+exp(-1*(v+153.3)/16.4))
		:tau_h1 = 64 + 92.3/(exp((v+44.3)/8.74)+exp(-1*(v+107)/17))
		tau_h1 = 56 + 218.5/(exp((v+51.9)/9.48)+exp(-1*(v+153.3)/17.7))
		tau_h2 = 1000*(.278 + 3.97/(exp((v+25.1)/9.97)+exp(-1*(v+35.3)/47.16))+2.25/(1+exp(-1*(v+17.3)/7.11)))

        tau_m=tau_m/q10
        tau_h1=tau_h1/q10
        tau_h2=tau_h2/q10

}

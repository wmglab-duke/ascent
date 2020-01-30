: This channels is implemented by Jenny Tigerholm. 
:The steady state curves are collected from Winkelman 2005 
:The time constat is from Gold 1996 and Safron 1996
: To plot this model run KA_Winkelman.m

NEURON {
	SUFFIX kf
	USEION k READ ek WRITE ik
	RANGE gbar, ek, ik
	RANGE tau_m, minf, hinf,tau_h,m,h, celsiusT
}

UNITS {
	(S) = (siemens)
	(mV) = (millivolts)
	(mA) = (milliamp)
}

PARAMETER {
	gbar 	(S/cm2) 
        
        lj=0 	(mV):not known 
        vhm=-5.4	(mV)
        vhh=-49.9 	(mV)
        km=16.4	(mV)
        kh=4.6	(mV)        

        celsiusT
        kvot_qt

	shift=-15 (mV)
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
}

STATE { h m }

BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar*m*h
	ik = g * (v-ek)
}

INITIAL {
	: assume that equilibrium has been reached
         
	 m=(1/(1+exp(-(1/km)*(v-vhm+lj+shift))))^4
         h=1/(1+exp((1/kh)*(v-vhh+lj+shift)))


}

DERIVATIVE states {
	rates(v)
	m' = (minf - m)/tau_m
        h' = (hinf - h)/tau_h
          
}

FUNCTION rates(Vm (mV)) (/ms) {        
        minf=(1/(1+exp(-(1/km)*(v-vhm+lj+shift))))^4
        hinf=1/(1+exp((1/kh)*(v-vhh+lj+shift)))
        tau_m=(0.25+10.04*exp(-((v+24.67)^2)/(2*34.8^2)))
        tau_h= (20+50*exp(-((v+40)^2)/(2*40^2)))    
        if (tau_h<5) {
        tau_h=5
        }
        kvot_qt=1/((3.3^((celsiusT-23)/10)))
        tau_m=tau_m*kvot_qt
        tau_h=tau_h*kvot_qt

}

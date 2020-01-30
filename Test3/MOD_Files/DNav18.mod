: The m and h are form sheets  2007
:s and u are form Delmas
: run NaV18_delmas.m to plot the model

NEURON {
	SUFFIX nav1p8
	USEION na READ ena WRITE ina
 	RANGE gbar, ena, ina
}

UNITS {
	(S) = (siemens)
	(mV) = (millivolts)
	(mA) = (milliamp)
}

PARAMETER {
	gbar = 0 (S/cm2) : =220e-9/(100e-12*1e8) (S/cm2) : 220(nS)/100(um)^2       
	kvot_qt
        celsiusT	
	shift_act = 0 (mV)
	shift_inact =0 (mV)
}

ASSIGNED {
	v	(mV) : NEURON provides this
	ina	(mA/cm2)
	g	(S/cm2)
	tau_h	(ms)
   	tau_m	(ms)
	tau_s	(ms)
	tau_u	(ms)
	minf
	hinf
	sinf
	uinf
        ena    	(mV)
        am
        bm
}

STATE { m h s u }

BREAKPOINT {
	SOLVE states METHOD cnexp	
	g = gbar * m^3* h * s * u
	ina = g * (v-ena)
}

INITIAL {
	: assume that equilibrium has been reached
        rates(v)
        m=minf
        h=hinf
        s=sinf
        u=uinf
    	

}

DERIVATIVE states {
	rates(v)
	m' = (minf - m)/tau_m
	h' = (hinf - h)/tau_h
	s' = (sinf - s)/tau_s
	u' = (uinf - u)/tau_u
}

FUNCTION rates(Vm (mV)) {
        
        am= 2.85-(2.839)/(1+exp((Vm-1.159)/13.95))
        bm= (7.6205)/(1+exp((Vm+46.463)/8.8289))
	tau_m = 1/(am+bm)
	minf = am/(am+bm)
        
        hinf= 1/(1+exp((Vm+32.2)/4))  
        tau_h=(1.218+42.043*exp(-((Vm+38.1)^2)/(2*15.19^2)))
	
	tau_s = 1/(alphas(Vm) + betas(Vm))			
        sinf = 1/(1 + exp((Vm + 45)/8(mV)))	 	
 	tau_u = 1/(alphau(Vm) + betau(Vm))	
	uinf = 1/(1 + exp((Vm + 51)/8(mV)))


	kvot_qt=1/((2.5^((celsiusT-22)/10)))
        tau_m=tau_m*kvot_qt
        tau_h=tau_h*kvot_qt
        tau_s=tau_s*kvot_qt
        tau_u=tau_u*kvot_qt
}


FUNCTION alphas(Vm (mV)) (/ms) {
	alphas=	0.001(/ms)*5.4203/(1 + exp((Vm + 79.816)/16.269(mV)))	
}

FUNCTION alphau(Vm (mV)) (/ms) {
	alphau=	0.0002(/ms)*2.0434/(1 + exp((Vm + 67.499)/19.51(mV)))
}

FUNCTION betas(Vm (mV)) (/ms) {
	betas= 0.001(/ms)*5.0757/(1 + exp(-(Vm + 15.968)/11.542(mV)))
}

FUNCTION betau(Vm (mV)) (/ms) {
	betau= 0.0002(/ms)*1.9952/(1 + exp(-(Vm + 30.963)/14.792(mV)))
}




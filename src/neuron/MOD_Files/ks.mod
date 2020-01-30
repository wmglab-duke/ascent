: This is mainly the 7.3 channel.
: It is an inactivation potassium current
: The inactivation long time constant is based on the article Passmore 2003. 
: The steady state inactivation and short time constant is from Maingret 2008 (which is based on Passmore 2003)
: To plot the model run kv73_passmore_delmas.m

NEURON {
	SUFFIX ks
	USEION k READ ek WRITE ik
	RANGE gbar, ena, ik,ek, celsiusT
}

UNITS {
	(S) = (siemens)
	(mV) = (millivolts)
	(mA) = (milliamp)
}

PARAMETER {
	gbar 	(S/cm2):= 0.2e-6 : =2e-9/(100e-12*1e8) (S/cm2) : 2(nS)/100(um)^2
        celsiusT
        kvot_qt
        lj=0
        a
        b
}

ASSIGNED {
	v	(mV) : NEURON provides this
	ik	(mA/cm2)
	g	(S/cm2)
	tau_ns	(ms)
	tau_nf  (ms)
        ninfs
        ninff
        ek	(mV)
}

STATE { ns nf }

BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar * (1/4*ns+nf*3/4) 
	ik = g * (v-ek)
}

INITIAL {
	: assume that equilibrium has been reached
	ns=1/(1+exp(-(v+30)/6(mV)))
        nf=1/(1+exp(-(v+30)/6(mV)))

}

DERIVATIVE states {
	rates(v)
	ns' = (ninfs - ns)/tau_ns
        nf' = (ninff - nf)/tau_nf

}


FUNCTION rates(Vm (mV)) (/ms) {
        ninfs=1/(1+exp(-(Vm+30)/6(mV)))
        ninff=1/(1+exp(-(Vm+30)/6(mV)))
        tau_ns=1(ms)*(13*(Vm*1(/mV)+lj)+1000)
        if (Vm<-60) {tau_ns=219}
        a=0.00395*exp((Vm+30)/40(mV))
        b=0.00395*exp(-(Vm+30)/20(mV))
        tau_nf=1(ms)/(a+b)

        kvot_qt=1/((3.3^((celsiusT-21)/10)))
        tau_ns=tau_ns*kvot_qt
        tau_nf=tau_nf*kvot_qt


}

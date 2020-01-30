: h.mod is the h channel 
: from Tom Andersson Sensitivity studies of voltage-dpendent conductance in neurons
: Tom has build his model on Kouranova 2008 Hyoerpolarization -activated cyclic nuleotide-gated channel mRNA and protein expression in large versus mall diameter dorsal root ganglion neurons: correlation with hyperpolarization-activated current

NEURON {
	SUFFIX h
	USEION k READ ek, ko, ki WRITE ik
        USEION na READ ena, nao, nai WRITE ina
	RANGE gbar, ena, ik, ina, ek, ekna, celsiusT
}

UNITS {
	(molar) = (1/liter)			: moles do not appear in units
	(mM)	= (millimolar)
	(S) = (siemens)
	(mV) = (millivolts)
	(mA) = (milliamp)
}

PARAMETER {
	gbar	(S/cm2): = 30e-6
	ekna    (mV): the combined rev pot from Na and k
        kvot_qt
        celsiusT
}

ASSIGNED {
	v	(mV) : NEURON provides this
	ik	(mA/cm2)
        ina     (mA/cm2)
	g	(S/cm2)
	tau_n_s	(ms)
        tau_n_f (ms)
	ninfs
        ninff
        kh
        ek	(mV)
        ena	(mV)
        ki	(mM)
        ko	(mM)
        nai	(mM)
        nao	(mM)
}

STATE { ns nf }

BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar * (0.5*ns+0.5*nf)
        ina=0.5*g*(v-ena)
        ik=0.5*g*(v-ek)
        :ekna=58*log10((1.0*ko + 0.4*nao)/(1.0*ki + 0.4*nai))          
        :kh=g*(v-ekna)/0.6
        :if (kh>0) {
	:ik = kh
        :ina = -kh*0.4
        :}else{
        :ik = -kh
        :ina = kh*0.4
        :}
}

INITIAL {
	: assume that equilibrium has been reached
	ns = 1./(1+exp((v+87.2)/9.7(mV)))
        nf = 1./(1+exp((v+87.2)/9.7(mV)))

}
 
DERIVATIVE states {
	rates(v)
	ns' = (ninfs - ns)/tau_n_s
        nf' = (ninff - nf)/tau_n_f

}


FUNCTION rates(Vm (mV)) (/ms) {

	ninfs = 1./(1+exp((Vm+87.2)/9.7(mV)))
        ninff = 1./(1+exp((Vm+87.2)/9.7(mV)))

        tau_n_s = 1(ms)*(300+542*exp((Vm+25)/-20(mV)))
        if (Vm<-70) {tau_n_s=1(ms)*(2500+100*exp((Vm+240)/50(mV)))}
      
        tau_n_f=1(ms)*(140+50*exp((Vm+25)/-20(mV)))
        if (Vm<-70) {tau_n_f=1(ms)*(250+12*exp((Vm+240)/50(mV)))}
        kvot_qt=1/((3^((celsiusT-22)/10)))
        tau_n_s=tau_n_s*kvot_qt
        tau_n_f=tau_n_f*kvot_qt

  
}

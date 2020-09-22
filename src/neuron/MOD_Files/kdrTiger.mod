:sheets 2007


NEURON {
	SUFFIX kdrTiger
	USEION k READ ek WRITE ik
	RANGE gbar, ena, ik,ek, celsiusT
}

UNITS {
	(S) = (siemens)
	(mV) = (millivolts)
	(mA) = (milliamp)
}

PARAMETER {
	gbar 	(S/cm2)
        celsiusT
        kvot_qt
        k1=15.4	(mV)
        Vh=35	(mV)

}

ASSIGNED {
	v	(mV) : NEURON provides this
	ik	(mA/cm2)
	g	(S/cm2)
	tau	(ms)
        ninf
        ek	(mV)
   
}

STATE { n }

BREAKPOINT {
	SOLVE states METHOD cnexp
	g = gbar*n^4 
	ik = g*(v-ek)
}

INITIAL {
	: assume that equilibrium has been reached
	n=1/(1+exp((v+Vh-10)/-k1))

}

DERIVATIVE states {
	rates(v)
	n' = (ninf - n)/tau

}


FUNCTION rates(Vm (mV)) (/ms) {        
        ninf=1/(1+exp((v+Vh-10)/-k1))
        tau=0.16+0.8*exp(-0.0267*(v+11)) 
        
        if (v<-31){
        tau=1000*(0.000688 +1/(exp((v+75.2)/6.5) + exp((v-131.5)/-34.8))) 
        } 
      
        kvot_qt=1/((3.3^((celsiusT-22)/10)))
        tau=tau*kvot_qt

}

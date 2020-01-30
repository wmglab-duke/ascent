: This is a leak channel for potassium 

NEURON {
	SUFFIX extrapump
	USEION k WRITE ik
	RANGE pumpik, pumpina
        USEION na WRITE ina

}

UNITS {
	(S) = (siemens)
	(mV) = (millivolts)
	(mA) = (milliamp)
}

PARAMETER {
	pumpik =0	(mA/cm2)
        pumpina =0	(mA/cm2)

     
}

ASSIGNED {
	ik	(mA/cm2)
        ina     (mA/cm2)
}


BREAKPOINT {
	 
	ik = pumpik 
        ina =pumpina
}

TITLE nahh
: From Traub & Miles "Neuronal networks of the hippocampus" (1991)
: Cummins et al. (2007), Sheets et al. (2007)

NEURON {
	SUFFIX nahh
	USEION na READ ena WRITE ina
	RANGE gnabar, m, h, ishift, mshift, hshift
	GLOBAL inf,tau
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

PARAMETER {
	v (mV)
	celsius		(degC)
	gnabar=.30 	(mho/cm2)
	ena 		(mV)
	ishift		(mV)
	mshift		(mV)
	hshift		(mV)
}
STATE {
	m h
}
ASSIGNED {
	ina (mA/cm2)
	inf[2]
        tau[2]
}

INITIAL {
         mhn(v)
         m=inf[0]
         h=inf[1]
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	ina = gnabar*m*m*m*h*(v - ena)
}

DERIVATIVE states {
	mhn(v*1(/mV))
	m' = (inf[0] - m)/tau[0]
	h' = (inf[1] - h)/tau[1]
}


FUNCTION alp(v(mV),i) { LOCAL q10 :  order m,h
        v=v+65
	q10 = 3^((celsius - 30)/10)
	if (i==0) {
	        v = v + mshift
		alp = q10*.32*expM1(13.1-v, 4)
	}else if (i==1){
	        v = v + hshift
		alp = q10*.128*exp((17-v+ishift)/18)
	}
}

FUNCTION bet(v,i) { LOCAL q10 : order m,h
        v=v+65
	q10 = 3^((celsius - 30)/10)
	if (i==0) {
	  	v = v + mshift
		bet = q10*.28*expM1(v-40.1,5)
	}else if (i==1){
	        v = v + hshift
		bet = q10*4/(exp((40.0-v)/5) + 1)
	}
}

FUNCTION expM1(x,y) {
	if (fabs(x/y) < 1e-6) {
		expM1 = y*(1 - x/y/2)
	}else{
		expM1 = x/(exp(x/y) - 1)
	}
}

PROCEDURE mhn(v) {LOCAL a, b
	FROM i=0 TO 1 {
		a = alp(v,i)
		b=bet(v,i)
		tau[i] = 1/(a + b)
		inf[i] = a/(a + b)
	}
}

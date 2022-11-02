TITLE hh.mod   squid sodium, potassium, and leak channels

COMMENT

ENDCOMMENT

UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
	(S) = (siemens)
}

? interface
NEURON {
        SUFFIX NaV7
        USEION na READ ena WRITE ina
        RANGE gnabar, gna, ina
        RANGE minf, hinf, htau, mtau
	THREADSAFE : assigned GLOBALs will be per thread
}

PARAMETER {
        gnabar = .12 (S/cm2)	<0,1e9>
}

STATE {
        m h
}

ASSIGNED {
        v (mV)
        celsius (degC)
        ena (mV)

	gna (S/cm2)
        ina (mA/cm2)
        minf hinf
		mtau (ms)
		htau (ms)
}

? currents
BREAKPOINT {
        SOLVE states METHOD cnexp
        gna = gnabar*m*m*m*h
	ina = gna*(v - ena)
}


INITIAL {
	rates(v)
	m = minf
	h = hinf
}

? states
DERIVATIVE states {
        rates(v)
        m' =  (minf-m)/mtau
        h' = (hinf-h)/htau
}

:LOCAL q10


? rates
PROCEDURE rates(v(mV)) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
        LOCAL  q10
        TABLE minf, mtau, hinf, htau DEPEND celsius FROM -100 TO 100 WITH 200

UNITSOFF
        q10 = 3^((celsius - 21)/10)
    :"m" sodium activation system
			:mtau = 0.0178 + 100/(exp(-1*(v+18)/9) + exp((v-13)/15))/q10
			mtau = 1/(exp((v+23.7)/12.35) + exp(-1*(v+13.6)/17))/q10
			minf = 1/(1+exp(-1*(v+31.2)/12))
    :"h" sodium inactivation system
			htau = 1/(exp(-1*(v+131)/9.5) + exp((v+5.7)/12.4))/q10
			hinf = 1/(1+exp((v+68)/7))
}

UNITSON

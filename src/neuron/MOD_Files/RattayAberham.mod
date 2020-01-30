TITLE hh.mod   squid sodium, potassium, and leak channels
 
COMMENT
HH model using RattayAberham k=12 for 37degC

 Remember to set celsius=37 in your HOC file.
 Eric Musselman  December 5, 2017
ENDCOMMENT
 
UNITS {
        (mA) = (milliamp)
        (mV) = (millivolt)
        (S)  = (siemens)
}
 
? interface
NEURON {
        SUFFIX RattayAberham
        USEION na READ ena WRITE ina
        USEION k READ ek WRITE ik
        NONSPECIFIC_CURRENT il
        RANGE gnabar, gkbar, gl, el, gna, gk
        GLOBAL minf, hinf, ninf, mtau, htau, ntau
        THREADSAFE : assigned GLOBALs will be per thread
}
 
PARAMETER {
        gnabar = .12 (S/cm2)    <0,1e9> : units verified
        gkbar = .036 (S/cm2)    <0,1e9> : units verified
        gl = .0003 (S/cm2)  <0,1e9>     : units verified
        el = -59.4 (mV)                  : changed this to match RattayAberham, units verified
}
 
STATE {
        m h n
}
 
ASSIGNED {
        v (mV)
        celsius (degC)
		ek (mV)
		ena (mV)

    gna (S/cm2)
    gk (S/cm2)
        ina (mA/cm2)
        ik (mA/cm2)
        il (mA/cm2)
        minf hinf ninf
    mtau (ms) htau (ms) ntau (ms)
}
 
? currents
BREAKPOINT {
        SOLVE states METHOD cnexp
        gna = gnabar*m*m*m*h
    ina = gna*(v - ena)
        gk = gkbar*n*n*n*n
    ik = gk*(v - ek)      
        il = gl*(v - el)
}
 
 
INITIAL {
    rates(v)
    m = minf
    h = hinf
    n = ninf
}

? states
DERIVATIVE states {  
        rates(v)
        m' =  (minf-m)/mtau
        h' = (hinf-h)/htau
        n' = (ninf-n)/ntau
}
 
:LOCAL q10


? rates
PROCEDURE rates(v(mV)) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
        LOCAL  alpha, beta, sum, q10
        TABLE minf, mtau, hinf, htau, ninf, ntau DEPEND celsius FROM -100 TO 100 WITH 200

UNITSOFF
        q10 = 2.24659524757^((celsius - 6.3)/10) : for k=12 as used in RattayAberham
                :"m" sodium activation system
        alpha = vtrap(2.5-0.1*(v+70),1)
        beta =  4 * exp(-(v+70)/18)
        sum = alpha + beta
    mtau = 1/(q10*sum)
        minf = alpha/sum
                :"h" sodium inactivation system
        alpha = 0.07 * exp(-(v+70)/20)
        beta = 1 / (exp(3-0.1*(v+70)) + 1)
        sum = alpha + beta
    htau = 1/(q10*sum)
        hinf = alpha/sum
                :"n" potassium activation system
        alpha = 0.1*vtrap(1-0.1*(v+70),1) 
        beta = 0.125*exp(-(v+70)/80)
    sum = alpha + beta
        ntau = 1/(q10*sum)
        ninf = alpha/sum
}
 
FUNCTION vtrap(x,y) {  :Traps for 0 in denominator of rate eqns.
        if (fabs(x/y) < 1e-6) {
                vtrap = y*(1 - x/y/2)
        }else{
                vtrap = x/(exp(x/y) - 1)
        }
}
 
UNITSON

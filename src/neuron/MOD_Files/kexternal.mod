

COMMENT
	Kexternal - Based on Frankenhauser and Hodgkin, 1956; Kushmerick and Podolsky, 1969
ENDCOMMENT

NEURON {
   SUFFIX kextern
   RANGE wid, txfer, kinitial
   USEION k READ ik WRITE ko
   USEION na READ ina WRITE nao
}

UNITS {
   (mM) = (milli/liter)
   (um) = (micron)
   FARADAY = (faraday) (coulomb)
   (molar) = (1/liter)
   PI = (pi) (1)
   (mA) = (milliamp)
}

PARAMETER {
	kinitial = 3.5 (mM)
	nainitial = 135 (mM)
	wid = 300 (angstrom)	: 30x10-3 width
	txfer = 150 (ms)		: tau
}

ASSIGNED {
   ik (mA/cm2)
   ina (mA/cm2)
}


INITIAL {
     ko = 3.5
     nao = 135
}

STATE {
   ko (mM)
   nao (mM)
}

BREAKPOINT {
   SOLVE state METHOD cnexp
}

DERIVATIVE state {
	   ko' = (1e8)*ik/(wid*FARADAY)+(kinitial-ko)/txfer
	   nao' = (1e8)*ina/(wid*FARADAY)+(nainitial-nao)/txfer

}


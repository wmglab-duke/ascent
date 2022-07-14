: Author: David Catherall
: Created: November 2016
: Intracellular calcium ion accumulation

: Neuron Block creates mechanism
	NEURON {
	  SUFFIX caintscale					:Sets suffix of mechanism for insertion into models
	  USEION ca READ ica WRITE cai		:Lays out which NEURON variables will be used/modified by file
	  GLOBAL nb							:Allows nb to be modified in hoc
	  RANGE a, ku, kr, Bi, diffOc, SA, Vol, L, nseg	:Allows variables to be modified in hoc and collected in vectors
	}

: Defines Units different from NEURON base units
	UNITS {
	  (mV)   	= (millivolt)
	  (um)		= (micrometer)
	  (mA)   	= (milliamp)
	  FARADAY 	= 96500 (coulombs)
	  (molar)	= (1/liter)
	  (mM)    	= (millimolar)
	  PI 		= (pi) (1)
	}

: Defines variables which will have a constant value throughout any given simulation
	PARAMETER {
	  a = 15e-4 (cm)  			: radius of cell
	  ku = 100 (/mM/ms) 		: rate constant for calcium buffer binding
	  kr = 0.238 (/ms)		 	: rate constant for calcium buffer release
	  nb = 4 					: number of binding sites on Calmodulin
	  Bi = 0.001 (mM) 			: Concentration of Calmodulin
	  :SA = 2.82743E-05 (cm2) 	: Surface area of cell
	  :Vol = 1.27e-8 (cm3) 		: vol of cell
	  :SA = 2.67617E-06 (cm2) 	: Surface area of cell w/ d=2.3 and nseg = 27
	  :Vol = 1.5388E-10 (cm3) 	: vol of cell w/ d=2.3 and nseg = 27
	}

: Defines variables which will be used or calculated throughout the simulation which may not be constant. Also included NEURON provided variables, like v, celsius, and ica
	ASSIGNED {

		:NEURON provided Variables
		ica  	(mA/cm2)
		L 		(um)
		nseg	(1)
		lseg	(cm)
		SA		(cm2)
		Vol		(cm3)
		diam	(um)
		:Model Specific Variables
		diffOc (/ms)


	}

: Defines state variables which will be calculated by numerical integration
	STATE { cai  (mM) Oc } :Oc is the fraction of Calmodulin binding sites that are occupied

: This block iterates the state variable calculations and uses those calculations to calculate currents
	BREAKPOINT { SOLVE state METHOD derivimplicit }

: Intializes State Variables
	INITIAL {

	Oc=.05
	lseg=(1e-4)*L/nseg
	SA = PI*(1e-4)*diam*lseg
	Vol = (PI*((1e-4)*(diam/2))^2*lseg)

	}

:Defines Governing Equations for State Variables
	DERIVATIVE state {
	  LOCAL diffOc											:Variable created to avoid ' notation on right hand side
	  diffOc=ku*cai*(1-Oc)-kr*Oc 							:Differential equation governing Calmodulin binding
	  Oc'=diffOc											:See diffOc above
	  cai' = -ica*(SA)/Vol/(2*FARADAY) - (nb*Bi*diffOc)		:Cai differential Equation
	}

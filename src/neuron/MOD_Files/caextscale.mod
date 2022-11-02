: Author: David Catherall
: Created: November 2016
: Extracellular calcium ion accumulation

: Neuron Block creates mechanism
	NEURON {
	  SUFFIX caextscale						:Sets suffix of mechanism for insertion into models
	  USEION ca READ ica WRITE cao		:Lays out which NEURON variables will be used/modified by file
	  GLOBAL cabath						:Allows cabath to be modified in hoc
	  RANGE fhspace, txfer, Vol_peri, L, nseg, SA, Volratio, lseg		:Allows variables to be modified in hoc and collected in vectors
	}

: Defines Units different from NEURON base units
	UNITS {
	  (mV)    = (millivolt)
	  (mA)    = (milliamp)
	  FARADAY = 96500 (coulombs)
	  (molar) = (1/liter)
	  (mM)    = (millimolar)
	  (um)	  = (micrometer)
	  PI      = (pi) (1)
	}

: Defines variables which will have a constant value throughout any given simulation run
	PARAMETER {
	  cabath   =  2 (mM)        	: Given in Schild 1994
	  fhspace = 1 (um)  			: Thickness of shell
	  txfer   =  4511.0 (ms)  		: tau for perineural space <-> bath exchange - Given in Schild 1994
	  :SA = 2.82743E-05 (cm2)		: Surface area of cell
	  VolSchild = 1.41372E-08 (cm3)
	  Vol_periSchild = 1.46136E-09 (cm3)	: Volume of perineural space

	}

: Defines variables which will be used or calculated throughout the simulation and are not necessarily constant
	ASSIGNED {

		ica  		(mA/cm2)
		SA 			(cm2)
		Vol_peri	(cm3)
		diam		(um)
		nseg		(1)
		L			(um)
		lseg		(cm)
		Vol			(cm3)
		Volratio	(1)

	}

: Defines state variables which will be calculated by numerical integration
	STATE { cao  (mM) }

: This block iterates the state variable calculations
	BREAKPOINT { SOLVE state METHOD derivimplicit }

: Variables are initialized
	INITIAL {
		lseg=(1e-4)*L/nseg
		SA = PI*(1e-4)*diam*lseg
		Vol = (PI*((1e-4)*(diam/2))^2*lseg)
		Volratio = Vol_periSchild/VolSchild
		Vol_peri = (PI*((1e-4)*((diam+fhspace)/2))^2*lseg)-Vol
		:Vol_peri = Vol * Volratio
	}

:Defines Governing Equations for State Variables
	DERIVATIVE state {
	  cao' = ica*SA/(2*Vol_peri*FARADAY) + (cabath - cao)/txfer
	}
	COMMENT
	  This equation has been changed from the original Schild 1994 equation. The second term of the cao
	  equation was given in Schild 1994 as:

	  (cao - cabath)/txfer

	  In this form, any difference between cao and cabath tends to drive cao away from cabath, which
	  doesn't make physiological sense, and creates an unstable system. Eventually, cao blows up,
	  changing the equilibrium of the system and skewing results.
	ENDCOMMENT

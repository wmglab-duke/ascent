: Author: David Catherall
: Created: November 2016
: Extracellular calcium ion accumulation

: Neuron Block creates mechanism
	NEURON {
	  SUFFIX caexttest						:Sets suffix of mechanism for insertion into models
	  USEION ca READ ica WRITE cao		:Lays out which NEURON variables will be used/modified by file
	  GLOBAL cabath						:Allows cabath to be modified in hoc
	  RANGE fhspace, txfer				:Allows variables to be modified in hoc and collected in vectors
	}

: Defines Units different from NEURON base units
	UNITS {
	  (mV)    = (millivolt)
	  (mA)    = (milliamp)
	  FARADAY = 96500 (coulombs)
	  (molar) = (1/liter)
	  (mM)    = (millimolar)
	}

: Defines variables which will have a constant value throughout any given simulation run
	PARAMETER {
	  cabath   =  2 (mM)        	: Given in Schild 1994
	  fhspace = 1e-4 (cm)  			: Thickness of shell
	  txfer   =  4511.0 (ms)  		: tau for perineural space <-> bath exchange - Given in Schild 1994
	  SA = 7.66242E-07 (cm2)		: Surface area of cell
	  Vol_peri = 1.98017E-12 (cm3)	: Volume of perineural space
	}

: Defines variables which will be used or calculated throughout the simulation and are not necessarily constant
	ASSIGNED { ica  (mA/cm2) }

: Defines state variables which will be calculated by numerical integration
	STATE { cao  (mM) }

: This block iterates the state variable calculations
	BREAKPOINT { SOLVE state METHOD derivimplicit }

:Nothing to be initialized

:Defines Governing Equations for State Variables
	DERIVATIVE state {
	  cao' = ica*SA/(2*Vol_peri*FARADAY) + (cao - cabath)/txfer
	}
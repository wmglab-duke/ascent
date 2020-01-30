: Author: David Catherall
: Created: November 2016
: leak is the background Na and Ca current in Schild 1994

: Neuron Block creates mechanism
	NEURON {
		SUFFIX leakSchild		:Sets suffix of mechanism for insertion into models
		USEION na READ ena WRITE ina		:Lays out which NEURON variables will be used/modified by file
		USEION ca READ cai, cao WRITE ica	:Since the mechanism uses two ions, two USEION statements are necessary
		RANGE i, ina, ica, gbna, gbca		:Allows variables to be modified in hoc and collected in vectors
	}

: Defines Units different from NEURON base units
	UNITS {
		(S)=(siemens)
		(mV)=(millivolt)
		(mA)=(milliamp)
		F = 96500 (coulombs)
		(molar) = (1/liter)
		(mM)    = (millimolar)
	}

: Defines variables which will have a constant value throughout any given simulation run
	PARAMETER {
		gbna=1.85681E-05 (S/cm2) <0, 1e9>
		gbca=3.00626E-06 (S/cm2) <0, 1e9>
		
		R=8.314 (joule/degC): Gas Constant
		z=2 : Charge of Ca ion
		ecaoffset=78.7 (mV)
	}

: Defines variables which will be used or calculated throughout the simulation which may not be constant. Also included NEURON provided variables, like v, celsius, and ina
	ASSIGNED {

		:NEURON provided Variables
		v (mV)
		ena (mV)
		ica (mA/cm2)
		ina (mA/cm2)
		celsius (degC)
		cai(mM)
		cao (mM)
		
		:Model Specific Variables
		ecaleak	(mV)
	}

: This block iterates the variable calculations and uses those calculations to calculate currents
	BREAKPOINT { 
		
		: Equation for eca given in Schild 1994
		ecaleak=(1000)*(R*(celsius+273.15)/z/F*log(cao/cai))-ecaoffset 
		
		ina = gbna*(v - ena) 
		ica = gbca*(v - ecaleak) 
	}
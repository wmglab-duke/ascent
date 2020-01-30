: Author: David Catherall
: Created: November 2016
: NaKpump is the Sodium-Potassium Pump in Schild 1994 
: Adapted from Leo Medina's implementation from Lindblad et al Am J Physiol 1996 275:H1666

: Original model has been modified to assume constant nai

: Neuron Block creates mechanism
	NEURON {
		SUFFIX NaKpumpSchild								:Sets suffix of mechanism for insertion into models
		USEION k READ ko WRITE ik					:Lays out which NEURON variables will be used/modified by file
		USEION na READ nai WRITE ina				:Since the mechanism uses two ions, two USEION statements are necessary
		RANGE INaKmax, ina, ink, Kmko, Kmnai, ik	:Allows variables to be modified in hoc and collected in vectors
	}

: Defines Units different from NEURON base units
	UNITS {
		(mA) = (milliamp)
		(mV) = (millivolt)
		(molar) = (1/liter)
		(mM) = (millimolar)
		
	}

: Defines variables which will have a constant value throughout any given simulation run
	PARAMETER {
		INaKmax22 = 0.009726135 (mA/cm2) <0,1e6> :INaKmax at 22 degC
		Kmnai = 5.46 (mM)    <0,1e6>
		Kmko = 0.621 (mM)    <0,1e6>
		Q10NaK = 1.16
		Q10TempA = 22.85	(degC)		: Used to shift INakmax value based on temperature with equation : tau(T1)=tau(Q10TempA)*Q10^((Q10TempA-T1)/Q10TempB)
		Q10TempB = 10	(degC)
	}

: Defines variables which will be used or calculated throughout the simulation which may not be constant. Also included NEURON provided variables, like v, celsius, and ina
	ASSIGNED {
		
		:NEURON provided Variables
		celsius (degC)
		v (mV)
		ko (mM)
		nai (mM)
		ik (mA/cm2)
		ina (mA/cm2)
		
		:Model Specific Variables
		ink (mA/cm2)
		INaKmax (mA/cm2)
	}

: This block iterates the variable calculations and uses those calculations to calculate currents
	BREAKPOINT { LOCAL fnk
		
		fnk = (v + 150)/(v + 200)
					
		ink = INaKmax*fnk*((nai/(nai+Kmnai))^3)*((ko/(ko+Kmko))^2) : Changed this line to reflect the exponents given in Schild 1994, instead of the orginal exponents in Leo's model.
		
		ina = 3*ink
		ik = -2*ink
	}

:Initialize INakmax, as it is temperature dependent
	INITIAL { 
		INaKmax = INaKmax22*Q10NaK^((Q10TempA-celsius)/Q10TempB)
	}
:Note that there are no state variables, and as such, no differential equations
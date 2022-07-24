: Author: David Catherall
: Created: November 2016
:CaPump is the Calcium Pump in Schild 1994
:  Adapted from Leo Medina's implementation from Lindblad et al Am J Physiol 1996 275:H1666

: Neuron Block creates mechanism
	NEURON {
		SUFFIX CaPump						:Sets suffix of mechanism for insertion into models
		USEION ca READ cai WRITE ica		:Lays out which NEURON variables will be used/modified by file
		RANGE ICaPmax, KmCa, ica, icap		:Allows variables to be modified in hoc and collected in vectors
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
		ICaPmax22 = 0.000859437(mA/cm2) <0,1e6>
		KmCa = .0005 (mM)    <0,1e6>
		Q10CaP = 2.30
		Q10TempA = 22	(degC)		: Used to shift ICaPmax value based on temperature with equation : tau(T1)=tau(Q10TempA)*Q10^((Q10TempA-T1)/Q10TempB)
		Q10TempB = 10	(degC)
	}

: Defines variables which will be used or calculated throughout the simulation which may not be constant. Also included NEURON provided variables, like v, celsius, and ina
	ASSIGNED {

		:NEURON provided Variables
		celsius (degC)
		v (mV)
		cai (mM)
		ica (mA/cm2)

		:Model Specific Variables
		icap (mA/cm2)
		ICaPmax (mA/cm2)
	}

: This block iterates the variable calculations and uses those calculations to calculate currents
	BREAKPOINT {

		icap = ICaPmax*(cai/(cai+KmCa))

		ica=icap
	}

:Initialize KNaCa, as it is temperature dependent
	INITIAL {
		ICaPmax = ICaPmax22*Q10CaP^((Q10TempA-celsius)/Q10TempB)
	}
:Note that there are no state variables, and as such, no differential equations

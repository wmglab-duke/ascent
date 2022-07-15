: Author: David Catherall
: Created: November 2016
: NaCaPump is the Sodium-Calcium Exchanger in Schild 1994
:  Adapted from Leo Medina's implementation from Lindblad et al Am J Physiol 1996 275:H1666

: Original model has been modified to assume constant nai

: Neuron Block creates mechanism
	NEURON {
		SUFFIX NaCaPump									:Sets suffix of mechanism for insertion into models
		USEION ca READ cao, cai WRITE ica				:Lays out which NEURON variables will be used/modified by file
		USEION na READ nao, nai WRITE ina				:Since the mechanism uses two ions, two USEION statements are necessary
		RANGE  inca, DFout, DFin, S, KNaCa, DNaCa		:Allows variables to be modified in hoc and collected in vectors
	}

: Defines Units different from NEURON base units
	UNITS {
		(mA) = (milliamp)
		(mV) = (millivolt)
		(molar) = (1/liter)
		(mM) = (millimolar)
		F = 96500 (coulombs)
		R = 8.314 (joule/degC)
	}

: Defines variables which will have a constant value throughout any given simulation run
	PARAMETER {
		KNaCa22 = 1.27324E-06 (mA/cm2/mM4)    <0,1e6> :KNaCa at 22 degC
		Q10NaCa = 2.20				:KNaCa Scale Factor
		Q10TempA = 22.85	(degC)		: Used to shift KNaCa value based on temperature with equation : tau(T1)=tau(Q10TempA)*Q10^((Q10TempA-T1)/Q10TempB)
		Q10TempB = 10	(degC)
		r=3
		gamma=0.5
		DNaCa=0.0036 (/mM4)
	}

: Defines variables which will be used or calculated throughout the simulation which may not be constant. Also included NEURON provided variables, like v, celsius, and ina
	ASSIGNED {

		:NEURON provided Variables
		celsius (degC)
		v (mV)
		cai (mM)
		cao (mM)
		ica (mA/cm2)
		ina (mA/cm2)
		nao (mM)
		nai (mM)

		:Model Specific Variabl
		inca (mA/cm2)
		S
		DFin (mM4)
		DFout (mM4)
		temp (degC)
		KNaCa (mA/cm2/mM4)
	}

: This block iterates the variable calculations and uses those calculations to calculate currents
	BREAKPOINT {

		temp = celsius +273.15

		S=1.0+DNaCa*(cai*nao*nao*nao+cao*nai*nai*nai)

		DFin=nai*nai*nai*cao*exp(((r-2)*gamma*v*F)/((1000)*R*temp))

		DFout=nao*nao*nao*cai*exp(((r-2)*(gamma-1)*v*F)/((1000)*R*temp))

		inca=KNaCa*((DFin-DFout)/S)


		ina = 3*inca
		ica = -2*inca
	}

:Initialize KNaCa, as it is temperature dependent
	INITIAL {
		KNaCa = KNaCa22*Q10NaCa^((Q10TempA-celsius)/Q10TempB)
	}
:Note that there are no state variables, and as such, no differential equations

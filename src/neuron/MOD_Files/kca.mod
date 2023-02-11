: Author: David Catherall
: Created: November 2016
: KCa is the calcium-activated potassium current in Schild 1994

: Neuron Block creates mechanism
	NEURON {
		   SUFFIX kca					:Sets suffix of mechanism for insertion into models
		   USEION k READ ek WRITE ik	:Lays out which NEURON variables will be used/modified by file
		   USEION ca READ cai			:As kca is reliant on two ions, two separate USEION statements are required
		   RANGE gbar, ek, ik			:Allows variables to be modified in hoc and collected in vectors

	}

: Defines Units different from NEURON base units
	UNITS {
		  (S) = (siemens)
		  (mV) = (millivolts)
		  (mA) = (milliamp)
		  (molar) = (/liter)
		  (mM) = (millimolar)
	}

: Defines variables which will have a constant value throughout any given simulation run
	PARAMETER {
		gbar =0.000141471 (S/cm2) 	: (S/cm2) Channel Conductance
		Q10kcac=2.30				: kca Q10 Scale Factor
		Q10TempA = 22.85	(degC)		: Used to shift tau values based on temperature with equation : tau(T1)=tau(Q10TempA)*Q10^((Q10TempA-T1)/Q10TempB)
		Q10TempB = 10	(degC)

		:kca_c Variables

			:Alpha Variables
				A_alphac=750.0 (/ms-mM) :From Schild 1994, alphac=A_alphac*cai*((Vm+B_alphan)/C_alphan)
				B_alphac=-10.0 (mV)
				C_alphac=12.0	(mV)

			:Beta Variables
				A_betac=0.05 (/ms)	:From Schild 1994, betac=A_betan*exp((Vm+B_betan)/C_betan)
				B_betac=-10.0 (mV)
				C_betac=-60.0 (mV)
	}

: Defines variables which will be used or calculated throughout the simulation which may not be constant. Also included NEURON provided variables, like v, celsius, and ina
	ASSIGNED {

		:NEURON provided Variables
		 v	(mV) : NEURON provides this
		 ik	(mA/cm2)
		 cai (mM)
		 celsius (degC)
		 ek	(mV)

		 :Model Specific Variables
		 g	(S/cm2)
		 tau_c	(ms)
		 cinf
		 alphac (/ms)
		 betac (/ms)


	}

: Defines state variables which will be calculated by numerical integration
	STATE { c }

: This block iterates the state variable calculations and uses those calculations to calculate currents
	BREAKPOINT {
		   SOLVE states METHOD cnexp
		   g = gbar * c
		   ik = g * (v-ek)
	}

: Intializes State Variables
	INITIAL {
		rates(v) : set tau_c, cinf
		: assume that equilibrium has been reached

		c = cinf
	}

:Defines Governing Equations for State Variables
	DERIVATIVE states {
		   rates(v)
		   c' = (cinf - c)/tau_c
	}

: Any other functions go here

	:Alpha Equation
		FUNCTION alpha(Vm (mV)) (/ms) {
			alphac=A_alphac*cai*exp((Vm+B_alphac)/C_alphac)
		}

	:Beta Equation
		FUNCTION beta(Vm (mV)) (/ms) {
			betac=A_betac*exp((Vm+B_betac)/C_betac)
		}

	:rates is a function which calculates the current values for tau and steady state equations based on voltage.
		FUNCTION rates(Vm (mV)) (/ms) {
			alpha(Vm)
			beta(Vm)

			tau_c = 4.5/(alphac+betac)
			cinf = alphac/(alphac+betac)

			:This scales the tau values based on temperature

			tau_c=tau_c*Q10kcac^((Q10TempA-celsius)/Q10TempB)
		}

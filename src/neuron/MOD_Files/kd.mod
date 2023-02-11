: Author: David Catherall
: Created: November 2016
: Kd is the delayed rectifier current in Schild 1994

: Neuron Block creates mechanism
	NEURON {
		   SUFFIX kd								:Sets suffix of mechanism for insertion into models
		   USEION k READ ek WRITE ik				:Lays out which NEURON variables will be used/modified by file
		   RANGE gbar, ek, ik, A_betan, shiftkd		:Allows variables to be modified in hoc and collected in vectors

	}

: Defines Units different from NEURON base units
	UNITS {
		  (S) = (siemens)
		  (mV) = (millivolts)
		  (mA) = (milliamp)
	}

: Defines variables which will have a constant value throughout any given simulation run
	PARAMETER {
		gbar =0.000180376 (S/cm2) 	: (S/cm2) Channel Conductance
		Q10kdn=1.40					: Q10 Scale Factor
		Q10TempA = 22.85	(degC)		: Used to shift tau values based on temperature with equation : tau(T1)=tau(Q10TempA)*Q10^((Q10TempA-T1)/Q10TempB)
		Q10TempB = 10	(degC)


		shiftkd=3.0 (mV) 			: Shift factor present in C-fiber

		: kd_n Variables

			: Steady State Variables
				V0p5n=14.62 (mV):As defined by Schild 1994, zinf=1.0/(1.0+exp((V0p5z-V)/S0p5z)
				S0p5n=-18.38 (mV)

			: Alpha Variables
				A_alphan=.001265 (/ms-mV) :From Schild 1994, alphan=A_alphan*(Vm+B_alphan)/(1.0-exp((Vm+B_alphan)/C_alphan)
				B_alphan=14.273 (mV)
				C_alphan=-10.0	(mV)

			:Beta Variables
				A_betan=0.125 (/ms)	:From Schild 1994, betan=A_betan*exp((Vm+B_betan)/C_betan)
				B_betan=55.0 (mV)
				C_betan=-2.5 (mV)
	}

: Defines variables which will be used or calculated throughout the simulation which may not be constant. Also included NEURON provided variables, like v, celsius, and ina
	ASSIGNED {
		:NEURON provided Variables
		v	(mV) : NEURON provides this
		ik	(mA/cm2)
		celsius (degC)
		ek	(mV)

		:Model Specific Variables
		g	(S/cm2)
		tau_n	(ms)
		ninf
		alphan (/ms)
		betan (/ms)

	}

: Defines state variables which will be calculated by numerical integration
	STATE { n }

: This block iterates the state variable calculations and uses those calculations to calculate currents
	BREAKPOINT {
		   SOLVE states METHOD cnexp
		   g = gbar * n
		   ik = g * (v-ek)
	}

: Intializes State Variables
	INITIAL {
		rates(v) : set tau_m, tau_h, hinf, minf
		: assume that equilibrium has been reached

		n = ninf
	}

:Defines Governing Equations for State Variables
	DERIVATIVE states {
		   rates(v)
		   n' = (ninf - n)/tau_n
	}

: Any other functions go here

	:Calculates Alpha value based on voltage
		FUNCTION alpha(Vm (mV)) (/ms) {
			alphan=(A_alphan*(Vm+B_alphan))/(1.0-exp((Vm+B_alphan)/C_alphan))
		}

	:Calculates Beta value based on voltage
		FUNCTION beta(Vm (mV)) (/ms) {
			betan=A_betan*exp((Vm+B_betan)/C_betan)
		}
	:rates is a function which calculates the current values for tau and steady state equations based on voltage.
		FUNCTION rates(Vm (mV)) (/ms) {
			alpha(Vm)
			beta(Vm)

			tau_n = 1/(alphan+betan)+1.0
			ninf = 1.0/(1.0+exp((Vm+V0p5n+shiftkd)/S0p5n))

			:This scales the tau values based on temperature
			tau_n=tau_n*Q10kdn^((Q10TempA-celsius)/Q10TempB)
		}

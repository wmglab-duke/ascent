: Author: David Catherall
: Created: November 2016
: Cat is the Low threshold, transient Ca current in Schild 1994

: Neuron Block creates mechanism
	NEURON {
		   SUFFIX cat							:Sets suffix of mechanism for insertion into models
		   USEION ca READ cai, cao WRITE ica	:Lays out which NEURON variables will be used/modified by file
		   RANGE gbar, ecat, ica, shiftcat		:Allows variables to be modified in hoc and collected in vectors

	}

: Defines Units different from NEURON base units
	UNITS {
		  (S) = (siemens)
		  (mV) = (millivolts)
		  (mA) = (milliamp)
		  F = 96500 (coulombs)
		  (molar) = (1/liter)
		  (mM)    = (millimolar)
	}

: Defines variables which will have a constant value throughout any given simulation run
	PARAMETER {
		gbar =1.23787E-05 (S/cm2)	: (S/cm2) Channel Conductance
		Q10catd=1.90				: d Q10 Scale Factor
		Q10catf=2.20				: f Q10 Scale Factor
		Q10TempA = 22.85	(degC)			: Used to shift tau values based on temperature with equation : tau(T1)=tau(Q10TempA)*Q10^((Q10TempA-T1)/Q10TempB)
		Q10TempB = 10	(degC)

		shiftcat=-7.0 (mV) 			: Shift factor present in C-fiber

		: cat_d Variables

			: Steady State Variables
				V0p5d=54.00 (mV):As defined by Schild 1994, zinf=1.0/(1.0+exp((V0p5z-V)/S0p5z)
				S0p5d=-5.75 (mV)

			: Tau Variables
				A_taud=22.0	(ms)	:As defined by Schild 1994, tauz=A_tauz*exp(-B^2(V-Vpz)^2)+C
				B_taud=0.052	(/mV)
				C_taud=2.5	(ms)
				Vpd=-68.0		(mV)

		: cat_f Variables

			: Steady State Variables
				V0p5f=68.00 (mV)
				S0p5f=6 (mV)

			: Tau Variables
				A_tauf=103.0	(ms)
				B_tauf=0.050	(/mV)
				C_tauf=12.5	(ms)
				Vpf=-58.0	(mV)

		:Calcium Related Variables
			R=8.314 (joule/degC): Gas Constant
			z=2 : Charge of Ca ion
			ecaoffset=78.7 (mV)


	}

: Defines variables which will be used or calculated throughout the simulation which may not be constant. Also included NEURON provided variables, like v, celsius, and ina
	ASSIGNED {
		:NEURON provided Variables
		 v	(mV)
		 ica	(mA/cm2)
		 celsius (degC)
		 cai (mM)
		 cao (mM)

		 :Model Specific Variables
		 g	(S/cm2)
		 tau_f	(ms)
		 tau_d	(ms)
		 dinf
		 finf
		 ecat	(mV)


	}

: Defines state variables which will be calculated by numerical integration
	STATE { d f }

: This block iterates the state variable calculations and uses those calculations to calculate currents
	BREAKPOINT {
		   SOLVE states METHOD cnexp
		   g = gbar * d * f
		   ica = g * (v-ecat)
	}

: Intializes State Variables
	INITIAL {
		rates(v) : set tau_m, tau_h, hinf, minf
		: assume that equilibrium has been reached


		d = dinf
		f = finf
	}

:Defines Governing Equations for State Variables
	DERIVATIVE states {
		   rates(v)
		   d' = (dinf - d)/tau_d
		   f' = (finf - f)/tau_f
	}

: Any other functions go here

	:rates is a function which calculates the current values for tau and steady state equations based on voltage.
		FUNCTION rates(Vm (mV)) (/ms) {
			 tau_d = A_taud*exp(-(B_taud)^2*(Vm-Vpd)^2)+C_taud
				 dinf = 1.0/(1.0+exp((Vm+V0p5d+shiftcat)/S0p5d))

			 tau_f = A_tauf*exp(-(B_tauf)^2*(Vm-Vpf)^2)+C_tauf
				 finf = 1.0/(1.0+exp((Vm+V0p5f+shiftcat)/S0p5f))

			: Equation for eca given in Schild 1994
			ecat=(1000)*(R*(celsius+273.15)/z/F*log(cao/cai))-ecaoffset

			:This scales the tau values based on temperature
				tau_d=tau_d*Q10catd^((Q10TempA-celsius)/Q10TempB)
				tau_f=tau_f*Q10catf^((Q10TempA-celsius)/Q10TempB)
		}

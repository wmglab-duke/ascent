: Author: David Catherall
: Created: November 2016
: Naf is the fast, TTX-sensitive current in Schild 1994

: Neuron Block creates mechanism
	NEURON {
		   SUFFIX naf						:Sets suffix of mechanism for insertion into models
		   USEION na READ ena WRITE ina		:Lays out which NEURON variables will be used/modified by file
		   RANGE gbar, ena, ina, shiftnaf	:Allows variables to be modified in hoc and collected in vectors

	}

: Defines Units different from NEURON base units
	UNITS {
		  (S) = (siemens)
		  (mV) = (millivolts)
		  (mA) = (milliamp)
	}

: Defines variables which will have a constant value throughout any given simulation run
	PARAMETER {
		gbar =0.068967142	(S/cm2)	: (S/cm2) Channel Conductance
		Q10nafm=2.30				: m Q10 Scale Factor
		Q10nafh=1.50				: h Q10 Scale Factor
		Q10TempA = 22.85	(degC)		: Used to shift tau values based on temperature with equation : tau(T1)=tau(Q10TempA)*Q10^((Q10TempA-T1)/Q10TempB)
		Q10TempB = 10	(degC)		: Note that a Q10 value for j is not defined in Schild 1994.


		shiftnaf=-17.5 (mV) 		: Shift factor present in C-fiber (Note that this shift is not applied to the j gating variable, as per Schild 1994)


		: naf_m Variables

			: Steady State Variables
			V0p5m=41.35 (mV)	:As defined by Schild 1994, zinf=1.0/(1.0+exp((V0p5z-V)/S0p5z)
			S0p5m=-4.75 (mV)

			: Tau Variables
			A_taum=0.75	(ms)	:As defined by Schild 1994, tauz=A_tauz*exp(-B^2(V-Vpz)^2)+C
			B_taum=0.0635	(/mV)
			C_taum=0.12	(ms)
			Vpm=-40.35		(mV)


		: naf_h Variables

			: Steady State Variables
				V0p5h=62.00 (mV)
				S0p5h=4.50 (mV)

			: Tau Variables
				A_tauh=6.5	(ms)
				B_tauh=0.0295	(/mV)
				C_tauh=0.55	(ms)
				Vph=-75.00	(mV)

		: naf_j Variables

			: Steady State Variables
				V0p5j=40.00 (mV)
				S0p5j=1.50 (mV)

			: Tau Variables
				A_tauj=25	(ms)
				B_tauj=4.50	(mV)
				C_tauj=0.01	(ms)
				Vpj=-20.00		(mV)
	}

: Defines variables which will be used or calculated throughout the simulation which may not be constant. Also included NEURON provided variables, like v, celsius, and ina
	ASSIGNED {

		:NEURON provided Variables
		 v	(mV)
		 celsius (degC)
		 ina	(mA/cm2)
		 ena	(mV)

		 :Model Specific Variables
		 g	(S/cm2)
		 tau_h	(ms)
		 tau_m	(ms)
		 tau_j	(ms)
		 minf
		 hinf
		 jinf


	}

: Defines state variables which will be calculated by numerical integration
	STATE { m h l }

COMMENT
	:#####NOTE##### The variable j is a reserved name in NMODL, so the
	gating variable j in the naf mechanism was renamed to l. This prevents
	any compiling errors. tauj and jinf retain their j naming convention
ENDCOMMENT

: This block iterates the state variable calculations and uses those calculations to calculate currents
	BREAKPOINT {
		   SOLVE states METHOD cnexp
		   g = gbar * m^3 * h *l
		   ina = g * (v-ena)
	}

: Intializes State Variables
	INITIAL {
		rates(v) : set tau_m, tau_h, hinf, minf
		: assume that equilibrium has been reached


		m = minf
		h = hinf
		l = jinf
	}

:Defines Governing Equations for State Variables
	DERIVATIVE states {
		   rates(v)
		   m' = (minf - m)/tau_m
		   h' = (hinf - h)/tau_h
		   l' = (jinf - l)/tau_j
	}


: Any other functions go here

	:rates is a function which calculates the current values for tau and steady state equations based on voltage.
		FUNCTION rates(Vm (mV)) (/ms) {
			 tau_m = A_taum*exp(-(B_taum)^2*(Vm-Vpm)^2)+C_taum
				 minf = 1.0/(1.0+exp((Vm+V0p5m+shiftnaf)/S0p5m))

			 tau_h = A_tauh*exp(-(B_tauh)^2*(Vm-Vph)^2)+C_tauh
				 hinf = 1.0/(1.0+exp((Vm+V0p5h+shiftnaf)/S0p5h))

			 tau_j = (A_tauj/(1.0+exp((Vm+Vpj)/B_tauj)))+C_tauj
				 jinf = 1.0/(1.0+exp((Vm+V0p5j)/S0p5j))

				tau_m=tau_m*Q10nafm^((Q10TempA-celsius)/Q10TempB)
				tau_h=tau_h*Q10nafh^((Q10TempA-celsius)/Q10TempB)
		}

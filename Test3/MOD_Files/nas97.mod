: Author: David Catherall
: Created: January 2018
: Nas is the slower, TTX-insensitive current in Schild 1994 

: Neuron Block creates mechanism
	NEURON {
		   SUFFIX nas97						:Sets suffix of mechanism for insertion into models
		   USEION na READ ena WRITE ina		:Lays out which NEURON variables will be used/modified by file
		   RANGE gbar, ena, ina, shiftnas	:Allows variables to be modified in hoc and collected in vectors

	}

: Defines Units different from NEURON base units
	UNITS {
		  (S) = (siemens)
		  (mV) = (millivolts)
		  (mA) = (milliamp)
	}

: Defines variables which will have a constant value throughout any given simulation
	PARAMETER {
		gbar =8.8420e-04 (S/cm2)	: (S/cm2) Channel Conductance
		Q10nasm=2.30				: m Q10 Scale Factor
		Q10nash=1.50				: h Q10 Scale Factor
		Q10TempA = 22	(degC)		: Used to shift tau values based on temperature with equation : tau(T1)=tau(Q10TempA)*Q10^((Q10TempA-T1)/Q10TempB)
		Q10TempB = 10	(degC)

		
		: nas_m Variables
		
			: Steady State Variables
				V0p5m=-15.29 (mV):As defined by Schild 1994, zinf=1.0/(1.0+exp((V0p5z-V)/S0p5z)
				S0p5m=6.54 (mV)
				
			: Tau Variables
				A_taum=1.35	(ms)	:As defined by Schild 1994, tauz=A_tauz*exp(-B^2(V-Vpz)^2)+C
				B_taum=0.075	(/mV)
				C_taum=0.395	(ms)
				Vpm=-13.5		(mV)
			
		: nas_h Variables
			
			: Steady State Variables
				V0p5h=-28.39 (mV)
				S0p5h=-5.20 (mV)

			: Tau Variables
				A_tauh=14.75	(ms)
				B_tauh=0.05	(/mV)
				C_tauh=2.25	(ms)
				Vph=-18.5	(mV)

	}

: Defines variables which will be used or calculated throughout the simulation which may not be constant. Also included NEURON provided variables, like v, celsius, and ina
	ASSIGNED {
		
		:NEURON provided Variables
		 v	(mV) : NEURON provides this
		 ina	(mA/cm2)
		 celsius (degC)
		 ena	(mV)
		 
		 :Model Specific Variables
		 g	(S/cm2)
		 tau_h	(ms)
		 tau_m	(ms)
		 minf
		 hinf

			 
	}

: Defines state variables which will be calculated by numerical integration
	STATE { m h } 

: This block iterates the state variable calculations and uses those calculations to calculate currents
	BREAKPOINT {
		   SOLVE states METHOD cnexp
		   g = gbar * m^3 * h
		   ina = g * (v-ena)
	}
: Intializes State Variables
	INITIAL {
		rates(v) : set tau_m, tau_h, hinf, minf
		: assume that equilibrium has been reached
		

		m = minf
		h = hinf
	}

:Defines Governing Equations for State Variables
	DERIVATIVE states {
		   rates(v)
		   m' = (minf - m)/tau_m
		   h' = (hinf - h)/tau_h
	}

: Any other functions go here

	:rates is a function which calculates the current values for tau and steady state equations based on voltage.
		FUNCTION rates(Vm (mV)) (/ms) {
			 tau_m = A_taum*exp(-(B_taum)^2*(Vm-Vpm)^2)+C_taum
				 minf = 1.0/(1.0+exp((V0p5m-Vm)/S0p5m))

			 tau_h = A_tauh*exp(-(B_tauh)^2*(Vm-Vph)^2)+C_tauh
				 hinf = 1.0/(1.0+exp((V0p5h-Vm)/S0p5h))
			:This scales the tau values based on temperature	 
			tau_m=tau_m*Q10nasm^((Q10TempA-celsius)/Q10TempB)
			tau_h=tau_h*Q10nash^((Q10TempA-celsius)/Q10TempB)
		}
: Author: David Catherall
: Created: January 2018
: Naf is the fast, TTX-sensitive current in Schild 1994 

: Neuron Block creates mechanism
	NEURON {
		   SUFFIX naf97						:Sets suffix of mechanism for insertion into models
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
		gbar =0.0012	(S/cm2)	: (S/cm2) Channel Conductance
		Q10nafm=2.30				: m Q10 Scale Factor
		Q10nafh=1.50				: h Q10 Scale Factor
		Q10TempA = 22	(degC)		: Used to shift tau values based on temperature with equation : tau(T1)=tau(Q10TempA)*Q10^((Q10TempA-T1)/Q10TempB)
		Q10TempB = 10	(degC)
		
		
		: naf_m Variables
		
			: Steady State Variables
			V0p5m=-37.75 (mV)	:As defined by Schild 1994, zinf=1.0/(1.0+exp((V0p5z-V)/S0p5z)
			S0p5m=6.98 (mV)
			
			: Tau Variables
			A_taum=1.2575	(ms)	:As defined by Schild 1994, tauz=A_tauz*exp(-B^2(V-Vpz)^2)+C
			B_taum=0.0625	(/mV)
			C_taum=0.175	(ms)
			Vpm=-39.0		(mV)
		
		
		: naf_h Variables
		
			: Steady State Variables
				V0p5h=-65.99 (mV)
				S0p5h=-5.97 (mV)
			
			: Tau Variables
				A_tauh=25.5	(ms)
				B_tauh=0.035	(/mV)
				C_tauh=1.05	(ms)
				Vph=-72.5	(mV)
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

			
				tau_m=tau_m*Q10nafm^((Q10TempA-celsius)/Q10TempB)
				tau_h=tau_h*Q10nafh^((Q10TempA-celsius)/Q10TempB)
		}

		
: Author: David Catherall
: Created: November 2016
: Kds is the slowly inactivating delay current in Schild 1994 

: Neuron Block creates mechanism
	NEURON {
		   SUFFIX kds						:Sets suffix of mechanism for insertion into models
		   USEION k READ ek WRITE ik		:Lays out which NEURON variables will be used/modified by file
		   RANGE gbar, ek, ik, shiftkds		:Allows variables to be modified in hoc and collected in vectors

	}

: Defines Units different from NEURON base units
	UNITS {
		  (S) = (siemens)
		  (mV) = (millivolts)
		  (mA) = (milliamp)
	}

: Defines variables which will have a constant value throughout any given simulation run
PARAMETER {
    gbar =0.000106103  (S/cm2)		: (S/cm2) Channel Conductance
	Q10kds=1.93 					:All gating variables have the same constant
	Q10TempA = 22.85	(degC)		: Used to shift tau values based on temperature with equation : tau(T1)=tau(Q10TempA)*Q10^((Q10TempA-T1)/Q10TempB)
	Q10TempB = 10	(degC)

 
	shiftkds=3.0 (mV) 				: Shift factor present in C-fiber
	
	: kds_x Variables
	
		: Steady State Variables
			V0p5x=39.59 (mV):As defined by Schild 1994, zinf=1.0/(1.0+exp((V0p5z-V)/S0p5z)
			S0p5x=-14.68(mV)
		
		: Tau Variables
			A_taux=5.0	(ms)	:As defined by Schild 1994, tauz=A_tauz*exp(-B^2(V-Vpz)^2)+C
			B_taux=0.022	(/mV)
			C_taux=2.5	(ms)
			Vpx=-65.0		(mV)
	
	: kds_y Variables
	
		: Steady State Variables
			V0p5y=48.0 (mV)
			S0p5y=7.0 (mV)
		
		: Tau Variables
			tau_y22=7500 (ms) :This is tau_y at 22 degC

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
		 tau_x	(ms)
		 tau_y	(ms)
		 xinf
		 yinf
		 
			 
	}

: Defines state variables which will be calculated by numerical integration
	STATE { x y1 } 

: This block iterates the state variable calculations and uses those calculations to calculate currents
	BREAKPOINT {
		   SOLVE states METHOD cnexp
		   g = gbar * x^3 * y1
		   ik = g * (v-ek)
	}

: Intializes State Variables
	INITIAL {
		rates(v) : set tau_x, yinf, xinf
		: assume that equilibrium has been reached
		

		x = xinf
		y1 = yinf
	}

:Defines Governing Equations for State Variables
	DERIVATIVE states {
		   rates(v)
		   x' = (xinf - x)/tau_x
		   y1' = (yinf - y1)/tau_y
	}

: Any other functions go here

	:rates is a function which calculates the current values for tau and steady state equations based on voltage.
		FUNCTION rates(Vm (mV)) (/ms) {
			tau_x = A_taux*exp(-(B_taux)^2*(Vm-Vpx)^2)+C_taux
				xinf = 1.0/(1.0+exp((Vm+V0p5x+shiftkds)/S0p5x))
				 
			tau_y=tau_y22
				yinf = 1.0/(1.0+exp((Vm+V0p5y+shiftkds)/S0p5y))
			
			:This scales the tau values based on temperature
			tau_x=tau_x*Q10kds^((Q10TempA-celsius)/Q10TempB)
			tau_y=tau_y*Q10kds^((Q10TempA-celsius)/Q10TempB)
		}
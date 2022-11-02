: Author: David Catherall
: Created: November 2016
: Ka is the Early Transient Outward K current in Schild 1994

: Neuron Block creates mechanism
NEURON {
       SUFFIX ka						:Sets suffix of mechanism for insertion into models
       USEION k READ ek WRITE ik		:Lays out which NEURON variables will be used/modified by file
       RANGE gbar, ek, ik, shiftka		:Allows variables to be modified in hoc and collected in vectors

}
: Defines Units different from NEURON base units
UNITS {
      (S) = (siemens)
      (mV) = (millivolts)
      (mA) = (milliamp)
}

: Defines variables which will have a constant value throughout any given simulation run
	PARAMETER {
		gbar =0.000141471 (S/cm2)	: (S/cm2) Channel Conductance
		Q10ka=1.93 					:All gating variables have the same constant
		Q10TempA = 22.85	(degC)			: Used to shift tau values based on temperature with equation : tau(T1)=tau(Q10TempA)*Q10^((Q10TempA-T1)/Q10TempB)
		Q10TempB = 10	(degC)


		shiftka=3.0 (mV) 			: Shift factor present in C-fiber

		:ka_p Variables

			: Steady State Variables
				V0p5p=28.0 (mV):As defined by Schild 1994, zinf=1.0/(1.0+exp((V0p5z-V)/S0p5z)
				S0p5p=-28.0 (mV)

			: Tau Variables
				A_taup=5.0	(ms)	:As defined by Schild 1994, tauz=A_tauz*exp(-B^2(V-Vpz)^2)+C
				B_taup=0.022	(/mV)
				C_taup=2.5	(ms)
				Vpp=-65.0		(mV)

		:ka_p Variables

			: Steady State Variables
				V0p5q=58.0 (mV)
				S0p5q=7.0 (mV)

			: Tau Variables
				A_tauq=100.0	(ms)
				B_tauq=0.035	(/mV)
				C_tauq=10.5	(ms)
				Vpq=-30.0	(mV)

	}

: Defines variables which will be used or calculated throughout the simulation which may not be constant. Also included NEURON provided variables, like v, celsius, and ina
	ASSIGNED {

		:NEURON provided Variables
		 v	(mV) : NEURON provides this
		 ik	(mA/cm2)
		 celsius  (degC)
		 ek	(mV)

		 :Model Specific Variables
		 g	(S/cm2)
		 tau_q	(ms)
		 tau_p	(ms)
		 pinf
		 qinf


	}

: Defines state variables which will be calculated by numerical integration
	STATE { p q }

: This block iterates the state variable calculations and uses those calculations to calculate currents
	BREAKPOINT {
		   SOLVE states METHOD cnexp
		   g = gbar * p^3 * q
		   ik = g * (v-ek)
	}

: Intializes State Variables
	INITIAL {
		rates(v) : set tau_m, tau_h, hinf, minf
		: assume that equilibrium has been reached


		p = pinf
		q = qinf
	}

:Defines Governing Equations for State Variables
	DERIVATIVE states {
		   rates(v)
		   p' = (pinf - p)/tau_p
		   q' = (qinf - q)/tau_q
	}

: Any other functions go here

	:rates is a function which calculates the current values for tau and steady state equations based on voltage.
		FUNCTION rates(Vm (mV)) (/ms) {
			 tau_p = A_taup*exp(-(B_taup)^2*(Vm-Vpp)^2)+C_taup
				 pinf = 1.0/(1.0+exp((Vm+V0p5p+shiftka)/S0p5p))

			 tau_q = A_tauq*exp(-(B_tauq)^2*(Vm-Vpq)^2)+C_tauq
				 qinf = 1.0/(1.0+exp((Vm+V0p5q+shiftka)/S0p5q))

			:This scales the tau values based on temperature
			tau_p=tau_p*Q10ka^((Q10TempA-celsius)/Q10TempB)
			tau_q=tau_q*Q10ka^((Q10TempA-celsius)/Q10TempB)
		}

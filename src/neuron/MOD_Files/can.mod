: Author: David Catherall
: Created: November 2016
: Can is the high threshold, long-lasting calcium current in Schild 1994

: Neuron Block creates mechanism
	NEURON {
		   SUFFIX can							:Sets suffix of mechanism for insertion into models
		   USEION ca READ cao, cai WRITE ica	:Lays out which NEURON variables will be used/modified by file
		   RANGE gbar, ecan, ica, shiftcan		:Allows variables to be modified in hoc and collected in vectors

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
		gbar =0.000106103	(S/cm2)		: (S/cm2) Channel Conductance
		Q10can=4.30 					:Each gating variable has the same constant
		Q10TempA = 22.85	(degC)			: Used to shift tau values based on temperature with equation : tau(T1)=tau(Q10TempA)*Q10^((Q10TempA-T1)/Q10TempB)
		Q10TempB = 10	(degC)

		shiftcan=-7.0 (mV) 				: Shift factor present in C-fiber

		: can_d Variables

			: Steady State Variables
				V0p5d=20.0 (mV):As defined by Schild 1994, zinf=1.0/(1.0+exp((V0p5z-V)/S0p5z)
				S0p5d=-4.5 (mV)

			: Tau Variables
				A_taud=3.25	(ms)	:As defined by Schild 1994, tauz=A_tauz*exp(-B^2(V-Vpz)^2)+C
				B_taud=0.042	(/mV)
				C_taud=0.395	(ms)
				Vpd=-31.0		(mV)

		: can_f1 Variables

			: Steady State Variables
				V0p5f1=20.0 (mV)
				S0p5f1=25.0 (mV)

			: Tau Variables
				A_tauf1=33.5	(ms)
				B_tauf1=.0395	(/mV)
				C_tauf1=5.0	(ms)
				Vpf1=-30.0	(mV)

		: can_f2 Variables

			: Steady State Variables
				V0p5f2=40.0 (mV)
				S0p5f2=10.0 (mV)

			: Tau Variables
				A_tauf2=225.0	(ms)
				B_tauf2=0.0275	(/mV)
				C_tauf2=75.00	(ms)
				Vpf2=-40.0		(mV)

		:Rn Variables
			A_rn=5.0 (mV)
			B_rn=-10.0 (mV)

		:Calcium Related Variables
			R=8.314 (joule/degC): Gas Constant
			z=2 : Charge of Ca ion
			ecaoffset=78.7 (mV)

	}

: Defines variables which will be used or calculated throughout the simulation which may not be constant. Also included NEURON provided variables, like v, celsius, and ina
	ASSIGNED {

		:NEURON provided Variables
		 v	(mV) : NEURON provides this
		 ica	(mA/cm2)
		 celsius (degC)
		 cao (mM)
		 cai (mM)

		 :Model Specific Variables
		 g	(S/cm2)
		 tau_f1	(ms)
		 tau_d	(ms)
		 tau_f2	(ms)
		 dinf
		 f1inf
		 f2inf
		 rn
		 ecan	(mV)


	}

: Defines state variables which will be calculated by numerical integration
	STATE { d f1 f2 }

: This block iterates the state variable calculations and uses those calculations to calculate currents
BREAKPOINT {
		   SOLVE states METHOD cnexp
		   g = gbar * d * (0.55*f1+0.45*f2)
		   ica = g * (v-ecan)
	}

: Intializes State Variables
INITIAL {
		rates(v) : set tau_m, tau_h, hinf, minf
		: assume that equilibrium has been reached


		d = dinf
		f1 = f1inf
		f2 = f2inf
}

:Defines Governing Equations for State Variables
	DERIVATIVE states {
		   rates(v)
		   d' = (dinf - d)/tau_d
		   f1' = (f1inf - f1)/tau_f1
		   f2' = (f2inf - f2)/tau_f2
	}

: Any other functions go here

:rates is a function which calculates the current values for tau and steady state equations based on voltage.
	FUNCTION rates(Vm (mV)) (/ms) {

		rn=0.2/(1.0+exp((Vm +A_rn+shiftcan)/B_rn))

		tau_d = A_taud*exp(-(B_taud)^2*(Vm-Vpd)^2)+C_taud
			dinf = 1.0/(1.0+exp((Vm+V0p5d+shiftcan)/S0p5d))

		tau_f1 = A_tauf1*exp(-(B_tauf1)^2*(Vm-Vpf1)^2)+C_tauf1
			f1inf = 1.0/(1.0+exp((Vm+V0p5f1+shiftcan)/S0p5f1))

		tau_f2 = A_tauf2*exp(-(B_tauf2)^2*(Vm-Vpf2)^2)+C_tauf2
			f2inf =rn+(1.0/(1.0+exp((Vm+V0p5f2+shiftcan)/S0p5f2)))

		: Equation for eca given in Schild 1994
		ecan=(1000)*(R*(celsius+273.15)/z/F*log(cao/cai))-ecaoffset

		:This scales the tau values based on temperature
			tau_d=tau_d*Q10can^((Q10TempA-celsius)/Q10TempB)
			tau_f1=tau_f1*Q10can^((Q10TempA-celsius)/Q10TempB)
			tau_f2=tau_f2*Q10can^((Q10TempA-celsius)/Q10TempB)
	}

 :Current Clamp

 NEURON {
 		 POINT_PROCESS trainIClamp
 		 RANGE del, PW, train, amp, freq, i, conv, pulsecount, onoff
 		 ELECTRODE_CURRENT i
 }

 UNITS { (na) = (nanoamp) }

 PARAMETER{
 		del (ms)
 		PW (ms)
 		train (ms)
 		amp (na)
 		freq (1/s)
 		conv = 1000 (ms/s)
 		pulsecount (s/s)
 		onoff (s/s)
 }

 ASSIGNED {
 		i (na)
 }

 INITIAL  { LOCAL j,k
 			pulsecount = 0
 			onoff = 0
            k =  (train/conv)/freq
 			i = 0
 			FROM j = 0 TO k  {
 				at_time (del + (j*(conv/freq)))
		 		at_time (del + PW + (j*(conv/freq)))
 		  	}
 		  	at_time (del + train)
 }

 BREAKPOINT {
		 		if (t < del + train && t > del) {
		 				if (t > del + (pulsecount*(conv/freq)) && t < del + (pulsecount*(conv/freq)) + PW)  {
		 						i = amp
		 						onoff = 1
		 				} else {
		 						if (onoff == 0) {
		 							i = 0
		 						} else {
		 							i = 0
		 							pulsecount = pulsecount + 1
		 							onoff = 0
		 						}
		 				}
		 		} else {
		 				i = 0
		 				pulsecount = 0
		 				onoff = 0
		 		}

 }

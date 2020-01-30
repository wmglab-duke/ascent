/* Created by Language version: 6.2.0 */
/* VECTORIZED */
#define NRN_VECTORIZED 1
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "scoplib_ansi.h"
#undef PI
#define nil 0
#include "md1redef.h"
#include "section.h"
#include "nrniv_mf.h"
#include "md2redef.h"
 
#if METHOD3
extern int _method3;
#endif

#if !NRNGPU
#undef exp
#define exp hoc_Exp
extern double hoc_Exp(double);
#endif
 
#define nrn_init _nrn_init__can
#define _nrn_initial _nrn_initial__can
#define nrn_cur _nrn_cur__can
#define _nrn_current _nrn_current__can
#define nrn_jacob _nrn_jacob__can
#define nrn_state _nrn_state__can
#define _net_receive _net_receive__can 
#define states states__can 
 
#define _threadargscomma_ _p, _ppvar, _thread, _nt,
#define _threadargsprotocomma_ double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt,
#define _threadargs_ _p, _ppvar, _thread, _nt
#define _threadargsproto_ double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt
 	/*SUPPRESS 761*/
	/*SUPPRESS 762*/
	/*SUPPRESS 763*/
	/*SUPPRESS 765*/
	 extern double *getarg();
 /* Thread safe. No static _p or _ppvar. */
 
#define t _nt->_t
#define dt _nt->_dt
#define gbar _p[0]
#define shiftcan _p[1]
#define ica _p[2]
#define ecan _p[3]
#define d _p[4]
#define f1 _p[5]
#define f2 _p[6]
#define cao _p[7]
#define cai _p[8]
#define g _p[9]
#define tau_f1 _p[10]
#define tau_d _p[11]
#define tau_f2 _p[12]
#define dinf _p[13]
#define f1inf _p[14]
#define f2inf _p[15]
#define rn _p[16]
#define Dd _p[17]
#define Df1 _p[18]
#define Df2 _p[19]
#define v _p[20]
#define _g _p[21]
#define _ion_cao	*_ppvar[0]._pval
#define _ion_cai	*_ppvar[1]._pval
#define _ion_ica	*_ppvar[2]._pval
#define _ion_dicadv	*_ppvar[3]._pval
 
#if MAC
#if !defined(v)
#define v _mlhv
#endif
#if !defined(h)
#define h _mlhh
#endif
#endif
 
#if defined(__cplusplus)
extern "C" {
#endif
 static int hoc_nrnpointerindex =  -1;
 static Datum* _extcall_thread;
 static Prop* _extcall_prop;
 /* external NEURON variables */
 extern double celsius;
 /* declaration of user functions */
 static void _hoc_rates(void);
 static int _mechtype;
extern void _nrn_cacheloop_reg(int, int);
extern void hoc_register_prop_size(int, int, int);
extern void hoc_register_limits(int, HocParmLimits*);
extern void hoc_register_units(int, HocParmUnits*);
extern void nrn_promote(Prop*, int, int);
extern Memb_func* memb_func;
 extern void _nrn_setdata_reg(int, void(*)(Prop*));
 static void _setdata(Prop* _prop) {
 _extcall_prop = _prop;
 }
 static void _hoc_setdata() {
 Prop *_prop, *hoc_getdata_range(int);
 _prop = hoc_getdata_range(_mechtype);
   _setdata(_prop);
 hoc_retpushx(1.);
}
 /* connect user functions to hoc names */
 static VoidFunc hoc_intfunc[] = {
 "setdata_can", _hoc_setdata,
 "rates_can", _hoc_rates,
 0, 0
};
#define rates rates_can
 extern double rates( _threadargsprotocomma_ double );
 /* declare global and static user variables */
#define A_rn A_rn_can
 double A_rn = 5;
#define A_tauf2 A_tauf2_can
 double A_tauf2 = 225;
#define A_tauf1 A_tauf1_can
 double A_tauf1 = 33.5;
#define A_taud A_taud_can
 double A_taud = 3.25;
#define B_rn B_rn_can
 double B_rn = -10;
#define B_tauf2 B_tauf2_can
 double B_tauf2 = 0.0275;
#define B_tauf1 B_tauf1_can
 double B_tauf1 = 0.0395;
#define B_taud B_taud_can
 double B_taud = 0.042;
#define C_tauf2 C_tauf2_can
 double C_tauf2 = 75;
#define C_tauf1 C_tauf1_can
 double C_tauf1 = 5;
#define C_taud C_taud_can
 double C_taud = 0.395;
#define Q10TempB Q10TempB_can
 double Q10TempB = 10;
#define Q10TempA Q10TempA_can
 double Q10TempA = 22.85;
#define Q10can Q10can_can
 double Q10can = 4.3;
#define R R_can
 double R = 8.314;
#define S0p5f2 S0p5f2_can
 double S0p5f2 = 10;
#define S0p5f1 S0p5f1_can
 double S0p5f1 = 25;
#define S0p5d S0p5d_can
 double S0p5d = -4.5;
#define Vpf2 Vpf2_can
 double Vpf2 = -40;
#define V0p5f2 V0p5f2_can
 double V0p5f2 = 40;
#define Vpf1 Vpf1_can
 double Vpf1 = -30;
#define V0p5f1 V0p5f1_can
 double V0p5f1 = 20;
#define Vpd Vpd_can
 double Vpd = -31;
#define V0p5d V0p5d_can
 double V0p5d = 20;
#define ecaoffset ecaoffset_can
 double ecaoffset = 78.7;
#define z z_can
 double z = 2;
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 0,0,0
};
 static HocParmUnits _hoc_parm_units[] = {
 "Q10TempA_can", "degC",
 "Q10TempB_can", "degC",
 "V0p5d_can", "mV",
 "S0p5d_can", "mV",
 "A_taud_can", "ms",
 "B_taud_can", "/mV",
 "C_taud_can", "ms",
 "Vpd_can", "mV",
 "V0p5f1_can", "mV",
 "S0p5f1_can", "mV",
 "A_tauf1_can", "ms",
 "B_tauf1_can", "/mV",
 "C_tauf1_can", "ms",
 "Vpf1_can", "mV",
 "V0p5f2_can", "mV",
 "S0p5f2_can", "mV",
 "A_tauf2_can", "ms",
 "B_tauf2_can", "/mV",
 "C_tauf2_can", "ms",
 "Vpf2_can", "mV",
 "A_rn_can", "mV",
 "B_rn_can", "mV",
 "R_can", "joule/degC",
 "ecaoffset_can", "mV",
 "gbar_can", "S/cm2",
 "shiftcan_can", "mV",
 "ica_can", "mA/cm2",
 "ecan_can", "mV",
 0,0
};
 static double delta_t = 0.01;
 static double d0 = 0;
 static double f20 = 0;
 static double f10 = 0;
 /* connect global user variables to hoc */
 static DoubScal hoc_scdoub[] = {
 "Q10can_can", &Q10can_can,
 "Q10TempA_can", &Q10TempA_can,
 "Q10TempB_can", &Q10TempB_can,
 "V0p5d_can", &V0p5d_can,
 "S0p5d_can", &S0p5d_can,
 "A_taud_can", &A_taud_can,
 "B_taud_can", &B_taud_can,
 "C_taud_can", &C_taud_can,
 "Vpd_can", &Vpd_can,
 "V0p5f1_can", &V0p5f1_can,
 "S0p5f1_can", &S0p5f1_can,
 "A_tauf1_can", &A_tauf1_can,
 "B_tauf1_can", &B_tauf1_can,
 "C_tauf1_can", &C_tauf1_can,
 "Vpf1_can", &Vpf1_can,
 "V0p5f2_can", &V0p5f2_can,
 "S0p5f2_can", &S0p5f2_can,
 "A_tauf2_can", &A_tauf2_can,
 "B_tauf2_can", &B_tauf2_can,
 "C_tauf2_can", &C_tauf2_can,
 "Vpf2_can", &Vpf2_can,
 "A_rn_can", &A_rn_can,
 "B_rn_can", &B_rn_can,
 "R_can", &R_can,
 "z_can", &z_can,
 "ecaoffset_can", &ecaoffset_can,
 0,0
};
 static DoubVec hoc_vdoub[] = {
 0,0,0
};
 static double _sav_indep;
 static void nrn_alloc(Prop*);
static void  nrn_init(_NrnThread*, _Memb_list*, int);
static void nrn_state(_NrnThread*, _Memb_list*, int);
 static void nrn_cur(_NrnThread*, _Memb_list*, int);
static void  nrn_jacob(_NrnThread*, _Memb_list*, int);
 
static int _ode_count(int);
static void _ode_map(int, double**, double**, double*, Datum*, double*, int);
static void _ode_spec(_NrnThread*, _Memb_list*, int);
static void _ode_matsol(_NrnThread*, _Memb_list*, int);
 
#define _cvode_ieq _ppvar[4]._i
 static void _ode_matsol_instance1(_threadargsproto_);
 /* connect range variables in _p that hoc is supposed to know about */
 static const char *_mechanism[] = {
 "6.2.0",
"can",
 "gbar_can",
 "shiftcan_can",
 0,
 "ica_can",
 "ecan_can",
 0,
 "d_can",
 "f1_can",
 "f2_can",
 0,
 0};
 static Symbol* _ca_sym;
 
extern Prop* need_memb(Symbol*);

static void nrn_alloc(Prop* _prop) {
	Prop *prop_ion;
	double *_p; Datum *_ppvar;
 	_p = nrn_prop_data_alloc(_mechtype, 22, _prop);
 	/*initialize range parameters*/
 	gbar = 0.000106103;
 	shiftcan = -7;
 	_prop->param = _p;
 	_prop->param_size = 22;
 	_ppvar = nrn_prop_datum_alloc(_mechtype, 5, _prop);
 	_prop->dparam = _ppvar;
 	/*connect ionic variables to this model*/
 prop_ion = need_memb(_ca_sym);
 nrn_promote(prop_ion, 1, 0);
 	_ppvar[0]._pval = &prop_ion->param[2]; /* cao */
 	_ppvar[1]._pval = &prop_ion->param[1]; /* cai */
 	_ppvar[2]._pval = &prop_ion->param[3]; /* ica */
 	_ppvar[3]._pval = &prop_ion->param[4]; /* _ion_dicadv */
 
}
 static void _initlists();
  /* some states have an absolute tolerance */
 static Symbol** _atollist;
 static HocStateTolerance _hoc_state_tol[] = {
 0,0
};
 static void _update_ion_pointer(Datum*);
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*)(Datum*));
extern void _nrn_thread_table_reg(int, void(*)(double*, Datum*, Datum*, _NrnThread*, int));
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 void _can_reg() {
	int _vectorized = 1;
  _initlists();
 	ion_reg("ca", -10000.);
 	_ca_sym = hoc_lookup("ca_ion");
 	register_mech(_mechanism, nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init, hoc_nrnpointerindex, 1);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
     _nrn_setdata_reg(_mechtype, _setdata);
     _nrn_thread_reg(_mechtype, 2, _update_ion_pointer);
  hoc_register_prop_size(_mechtype, 22, 5);
  hoc_register_dparam_semantics(_mechtype, 0, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 1, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 2, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 3, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 4, "cvodeieq");
 	hoc_register_cvode(_mechtype, _ode_count, _ode_map, _ode_spec, _ode_matsol);
 	hoc_register_tolerance(_mechtype, _hoc_state_tol, &_atollist);
 	hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 can D:/Documents/access/Test3/MOD_Files/can.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
 static double F = 96500.0;
static int _reset;
static char *modelname = "";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
 
static int _ode_spec1(_threadargsproto_);
/*static int _ode_matsol1(_threadargsproto_);*/
 static int _slist1[3], _dlist1[3];
 static int states(_threadargsproto_);
 
/*CVODE*/
 static int _ode_spec1 (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {int _reset = 0; {
   rates ( _threadargscomma_ v ) ;
   Dd = ( dinf - d ) / tau_d ;
   Df1 = ( f1inf - f1 ) / tau_f1 ;
   Df2 = ( f2inf - f2 ) / tau_f2 ;
   }
 return _reset;
}
 static int _ode_matsol1 (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
 rates ( _threadargscomma_ v ) ;
 Dd = Dd  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_d )) ;
 Df1 = Df1  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_f1 )) ;
 Df2 = Df2  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_f2 )) ;
 return 0;
}
 /*END CVODE*/
 static int states (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) { {
   rates ( _threadargscomma_ v ) ;
    d = d + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_d)))*(- ( ( ( dinf ) ) / tau_d ) / ( ( ( ( - 1.0 ) ) ) / tau_d ) - d) ;
    f1 = f1 + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_f1)))*(- ( ( ( f1inf ) ) / tau_f1 ) / ( ( ( ( - 1.0 ) ) ) / tau_f1 ) - f1) ;
    f2 = f2 + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_f2)))*(- ( ( ( f2inf ) ) / tau_f2 ) / ( ( ( ( - 1.0 ) ) ) / tau_f2 ) - f2) ;
   }
  return 0;
}
 
double rates ( _threadargsprotocomma_ double _lVm ) {
   double _lrates;
 rn = 0.2 / ( 1.0 + exp ( ( _lVm + A_rn + shiftcan ) / B_rn ) ) ;
   tau_d = A_taud * exp ( - pow( ( B_taud ) , 2.0 ) * pow( ( _lVm - Vpd ) , 2.0 ) ) + C_taud ;
   dinf = 1.0 / ( 1.0 + exp ( ( _lVm + V0p5d + shiftcan ) / S0p5d ) ) ;
   tau_f1 = A_tauf1 * exp ( - pow( ( B_tauf1 ) , 2.0 ) * pow( ( _lVm - Vpf1 ) , 2.0 ) ) + C_tauf1 ;
   f1inf = 1.0 / ( 1.0 + exp ( ( _lVm + V0p5f1 + shiftcan ) / S0p5f1 ) ) ;
   tau_f2 = A_tauf2 * exp ( - pow( ( B_tauf2 ) , 2.0 ) * pow( ( _lVm - Vpf2 ) , 2.0 ) ) + C_tauf2 ;
   f2inf = rn + ( 1.0 / ( 1.0 + exp ( ( _lVm + V0p5f2 + shiftcan ) / S0p5f2 ) ) ) ;
   ecan = ( 1000.0 ) * ( R * ( celsius + 273.15 ) / z / F * log ( cao / cai ) ) - ecaoffset ;
   tau_d = tau_d * pow( Q10can , ( ( Q10TempA - celsius ) / Q10TempB ) ) ;
   tau_f1 = tau_f1 * pow( Q10can , ( ( Q10TempA - celsius ) / Q10TempB ) ) ;
   tau_f2 = tau_f2 * pow( Q10can , ( ( Q10TempA - celsius ) / Q10TempB ) ) ;
   
return _lrates;
 }
 
static void _hoc_rates(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  rates ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
static int _ode_count(int _type){ return 3;}
 
static void _ode_spec(_NrnThread* _nt, _Memb_list* _ml, int _type) {
   double* _p; Datum* _ppvar; Datum* _thread;
   Node* _nd; double _v; int _iml, _cntml;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;
  for (_iml = 0; _iml < _cntml; ++_iml) {
    _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
    _nd = _ml->_nodelist[_iml];
    v = NODEV(_nd);
  cao = _ion_cao;
  cai = _ion_cai;
     _ode_spec1 (_p, _ppvar, _thread, _nt);
  }}
 
static void _ode_map(int _ieq, double** _pv, double** _pvdot, double* _pp, Datum* _ppd, double* _atol, int _type) { 
	double* _p; Datum* _ppvar;
 	int _i; _p = _pp; _ppvar = _ppd;
	_cvode_ieq = _ieq;
	for (_i=0; _i < 3; ++_i) {
		_pv[_i] = _pp + _slist1[_i];  _pvdot[_i] = _pp + _dlist1[_i];
		_cvode_abstol(_atollist, _atol, _i);
	}
 }
 
static void _ode_matsol_instance1(_threadargsproto_) {
 _ode_matsol1 (_p, _ppvar, _thread, _nt);
 }
 
static void _ode_matsol(_NrnThread* _nt, _Memb_list* _ml, int _type) {
   double* _p; Datum* _ppvar; Datum* _thread;
   Node* _nd; double _v; int _iml, _cntml;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;
  for (_iml = 0; _iml < _cntml; ++_iml) {
    _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
    _nd = _ml->_nodelist[_iml];
    v = NODEV(_nd);
  cao = _ion_cao;
  cai = _ion_cai;
 _ode_matsol_instance1(_threadargs_);
 }}
 extern void nrn_update_ion_pointer(Symbol*, Datum*, int, int);
 static void _update_ion_pointer(Datum* _ppvar) {
   nrn_update_ion_pointer(_ca_sym, _ppvar, 0, 2);
   nrn_update_ion_pointer(_ca_sym, _ppvar, 1, 1);
   nrn_update_ion_pointer(_ca_sym, _ppvar, 2, 3);
   nrn_update_ion_pointer(_ca_sym, _ppvar, 3, 4);
 }

static void initmodel(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
  int _i; double _save;{
  d = d0;
  f2 = f20;
  f1 = f10;
 {
   rates ( _threadargscomma_ v ) ;
   d = dinf ;
   f1 = f1inf ;
   f2 = f2inf ;
   }
 
}
}

static void nrn_init(_NrnThread* _nt, _Memb_list* _ml, int _type){
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; double _v; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
#if CACHEVEC
  if (use_cachevec) {
    _v = VEC_V(_ni[_iml]);
  }else
#endif
  {
    _nd = _ml->_nodelist[_iml];
    _v = NODEV(_nd);
  }
 v = _v;
  cao = _ion_cao;
  cai = _ion_cai;
 initmodel(_p, _ppvar, _thread, _nt);
 }
}

static double _nrn_current(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt, double _v){double _current=0.;v=_v;{ {
   g = gbar * d * ( 0.55 * f1 + 0.45 * f2 ) ;
   ica = g * ( v - ecan ) ;
   }
 _current += ica;

} return _current;
}

static void nrn_cur(_NrnThread* _nt, _Memb_list* _ml, int _type) {
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; int* _ni; double _rhs, _v; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
#if CACHEVEC
  if (use_cachevec) {
    _v = VEC_V(_ni[_iml]);
  }else
#endif
  {
    _nd = _ml->_nodelist[_iml];
    _v = NODEV(_nd);
  }
  cao = _ion_cao;
  cai = _ion_cai;
 _g = _nrn_current(_p, _ppvar, _thread, _nt, _v + .001);
 	{ double _dica;
  _dica = ica;
 _rhs = _nrn_current(_p, _ppvar, _thread, _nt, _v);
  _ion_dicadv += (_dica - ica)/.001 ;
 	}
 _g = (_g - _rhs)/.001;
  _ion_ica += ica ;
#if CACHEVEC
  if (use_cachevec) {
	VEC_RHS(_ni[_iml]) -= _rhs;
  }else
#endif
  {
	NODERHS(_nd) -= _rhs;
  }
 
}
 
}

static void nrn_jacob(_NrnThread* _nt, _Memb_list* _ml, int _type) {
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml];
#if CACHEVEC
  if (use_cachevec) {
	VEC_D(_ni[_iml]) += _g;
  }else
#endif
  {
     _nd = _ml->_nodelist[_iml];
	NODED(_nd) += _g;
  }
 
}
 
}

static void nrn_state(_NrnThread* _nt, _Memb_list* _ml, int _type) {
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; double _v = 0.0; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
 _nd = _ml->_nodelist[_iml];
#if CACHEVEC
  if (use_cachevec) {
    _v = VEC_V(_ni[_iml]);
  }else
#endif
  {
    _nd = _ml->_nodelist[_iml];
    _v = NODEV(_nd);
  }
 v=_v;
{
  cao = _ion_cao;
  cai = _ion_cai;
 {   states(_p, _ppvar, _thread, _nt);
  } }}

}

static void terminal(){}

static void _initlists(){
 double _x; double* _p = &_x;
 int _i; static int _first = 1;
  if (!_first) return;
 _slist1[0] = &(d) - _p;  _dlist1[0] = &(Dd) - _p;
 _slist1[1] = &(f1) - _p;  _dlist1[1] = &(Df1) - _p;
 _slist1[2] = &(f2) - _p;  _dlist1[2] = &(Df2) - _p;
_first = 0;
}

#if defined(__cplusplus)
} /* extern "C" */
#endif

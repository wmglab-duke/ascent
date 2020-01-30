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
 
#define nrn_init _nrn_init__gaines_node
#define _nrn_initial _nrn_initial__gaines_node
#define nrn_cur _nrn_cur__gaines_node
#define _nrn_current _nrn_current__gaines_node
#define nrn_jacob _nrn_jacob__gaines_node
#define nrn_state _nrn_state__gaines_node
#define _net_receive _net_receive__gaines_node 
#define evaluate_fct evaluate_fct__gaines_node 
#define states states__gaines_node 
 
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
#define gnapbar _p[0]
#define gnabar _p[1]
#define gkbar _p[2]
#define gkfbar _p[3]
#define gl _p[4]
#define ena _p[5]
#define ek _p[6]
#define el _p[7]
#define inap _p[8]
#define ina _p[9]
#define ik _p[10]
#define il _p[11]
#define ikf _p[12]
#define mp_inf _p[13]
#define m_inf _p[14]
#define h_inf _p[15]
#define n_inf _p[16]
#define s_inf _p[17]
#define tau_mp _p[18]
#define tau_m _p[19]
#define tau_h _p[20]
#define tau_n _p[21]
#define tau_s _p[22]
#define mp _p[23]
#define m _p[24]
#define h _p[25]
#define s _p[26]
#define n _p[27]
#define Dmp _p[28]
#define Dm _p[29]
#define Dh _p[30]
#define Ds _p[31]
#define Dn _p[32]
#define q10_1 _p[33]
#define q10_2 _p[34]
#define q10_3 _p[35]
#define q10_4 _p[36]
#define v _p[37]
#define _g _p[38]
 
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
 static void _hoc_Exp(void);
 static void _hoc_evaluate_fct(void);
 static void _hoc_vtrap13(void);
 static void _hoc_vtrap12(void);
 static void _hoc_vtrap11(void);
 static void _hoc_vtrap10(void);
 static void _hoc_vtrap9(void);
 static void _hoc_vtrap8(void);
 static void _hoc_vtrap7(void);
 static void _hoc_vtrap6(void);
 static void _hoc_vtrap2(void);
 static void _hoc_vtrap1(void);
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
 "setdata_gaines_node", _hoc_setdata,
 "Exp_gaines_node", _hoc_Exp,
 "evaluate_fct_gaines_node", _hoc_evaluate_fct,
 "vtrap13_gaines_node", _hoc_vtrap13,
 "vtrap12_gaines_node", _hoc_vtrap12,
 "vtrap11_gaines_node", _hoc_vtrap11,
 "vtrap10_gaines_node", _hoc_vtrap10,
 "vtrap9_gaines_node", _hoc_vtrap9,
 "vtrap8_gaines_node", _hoc_vtrap8,
 "vtrap7_gaines_node", _hoc_vtrap7,
 "vtrap6_gaines_node", _hoc_vtrap6,
 "vtrap2_gaines_node", _hoc_vtrap2,
 "vtrap1_gaines_node", _hoc_vtrap1,
 0, 0
};
#define Exp Exp_gaines_node
#define vtrap13 vtrap13_gaines_node
#define vtrap12 vtrap12_gaines_node
#define vtrap11 vtrap11_gaines_node
#define vtrap10 vtrap10_gaines_node
#define vtrap9 vtrap9_gaines_node
#define vtrap8 vtrap8_gaines_node
#define vtrap7 vtrap7_gaines_node
#define vtrap6 vtrap6_gaines_node
#define vtrap2 vtrap2_gaines_node
#define vtrap1 vtrap1_gaines_node
 extern double Exp( _threadargsprotocomma_ double );
 extern double vtrap13( _threadargsprotocomma_ double );
 extern double vtrap12( _threadargsprotocomma_ double );
 extern double vtrap11( _threadargsprotocomma_ double );
 extern double vtrap10( _threadargsprotocomma_ double );
 extern double vtrap9( _threadargsprotocomma_ double );
 extern double vtrap8( _threadargsprotocomma_ double );
 extern double vtrap7( _threadargsprotocomma_ double );
 extern double vtrap6( _threadargsprotocomma_ double );
 extern double vtrap2( _threadargsprotocomma_ double );
 extern double vtrap1( _threadargsprotocomma_ double );
 /* declare global and static user variables */
#define anC anC_gaines_node
 double anC = 1.1;
#define anB anB_gaines_node
 double anB = -83.2;
#define anA anA_gaines_node
 double anA = 0.0462;
#define asC asC_gaines_node
 double asC = -5;
#define asB asB_gaines_node
 double asB = -27;
#define asA asA_gaines_node
 double asA = 0.3;
#define ahC ahC_gaines_node
 double ahC = 11;
#define ahB ahB_gaines_node
 double ahB = 114;
#define ahA ahA_gaines_node
 double ahA = 0.062;
#define amC amC_gaines_node
 double amC = 10.3;
#define amB amB_gaines_node
 double amB = 20.4;
#define amA amA_gaines_node
 double amA = 1.86;
#define ampC ampC_gaines_node
 double ampC = 10.2;
#define ampB ampB_gaines_node
 double ampB = 27;
#define ampA ampA_gaines_node
 double ampA = 0.01;
#define bnC bnC_gaines_node
 double bnC = 10.5;
#define bnB bnB_gaines_node
 double bnB = -66;
#define bnA bnA_gaines_node
 double bnA = 0.0824;
#define bsC bsC_gaines_node
 double bsC = -1;
#define bsB bsB_gaines_node
 double bsB = 10;
#define bsA bsA_gaines_node
 double bsA = 0.03;
#define bhC bhC_gaines_node
 double bhC = 13.4;
#define bhB bhB_gaines_node
 double bhB = 31.8;
#define bhA bhA_gaines_node
 double bhA = 2.3;
#define bmC bmC_gaines_node
 double bmC = 9.16;
#define bmB bmB_gaines_node
 double bmB = 25.7;
#define bmA bmA_gaines_node
 double bmA = 0.086;
#define bmpC bmpC_gaines_node
 double bmpC = 10;
#define bmpB bmpB_gaines_node
 double bmpB = 34;
#define bmpA bmpA_gaines_node
 double bmpA = 0.00025;
#define vtraub vtraub_gaines_node
 double vtraub = -80;
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 0,0,0
};
 static HocParmUnits _hoc_parm_units[] = {
 "gnapbar_gaines_node", "mho/cm2",
 "gnabar_gaines_node", "mho/cm2",
 "gkbar_gaines_node", "mho/cm2",
 "gkfbar_gaines_node", "mho/cm2",
 "gl_gaines_node", "mho/cm2",
 "ena_gaines_node", "mV",
 "ek_gaines_node", "mV",
 "el_gaines_node", "mV",
 "inap_gaines_node", "mA/cm2",
 "ina_gaines_node", "mA/cm2",
 "ik_gaines_node", "mA/cm2",
 "il_gaines_node", "mA/cm2",
 "ikf_gaines_node", "mA/cm2",
 0,0
};
 static double delta_t = 1;
 static double h0 = 0;
 static double m0 = 0;
 static double mp0 = 0;
 static double n0 = 0;
 static double s0 = 0;
 /* connect global user variables to hoc */
 static DoubScal hoc_scdoub[] = {
 "vtraub_gaines_node", &vtraub_gaines_node,
 "ampA_gaines_node", &ampA_gaines_node,
 "ampB_gaines_node", &ampB_gaines_node,
 "ampC_gaines_node", &ampC_gaines_node,
 "bmpA_gaines_node", &bmpA_gaines_node,
 "bmpB_gaines_node", &bmpB_gaines_node,
 "bmpC_gaines_node", &bmpC_gaines_node,
 "amA_gaines_node", &amA_gaines_node,
 "amB_gaines_node", &amB_gaines_node,
 "amC_gaines_node", &amC_gaines_node,
 "bmA_gaines_node", &bmA_gaines_node,
 "bmB_gaines_node", &bmB_gaines_node,
 "bmC_gaines_node", &bmC_gaines_node,
 "ahA_gaines_node", &ahA_gaines_node,
 "ahB_gaines_node", &ahB_gaines_node,
 "ahC_gaines_node", &ahC_gaines_node,
 "bhA_gaines_node", &bhA_gaines_node,
 "bhB_gaines_node", &bhB_gaines_node,
 "bhC_gaines_node", &bhC_gaines_node,
 "asA_gaines_node", &asA_gaines_node,
 "asB_gaines_node", &asB_gaines_node,
 "asC_gaines_node", &asC_gaines_node,
 "bsA_gaines_node", &bsA_gaines_node,
 "bsB_gaines_node", &bsB_gaines_node,
 "bsC_gaines_node", &bsC_gaines_node,
 "anA_gaines_node", &anA_gaines_node,
 "anB_gaines_node", &anB_gaines_node,
 "anC_gaines_node", &anC_gaines_node,
 "bnA_gaines_node", &bnA_gaines_node,
 "bnB_gaines_node", &bnB_gaines_node,
 "bnC_gaines_node", &bnC_gaines_node,
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
 
#define _cvode_ieq _ppvar[0]._i
 static void _ode_matsol_instance1(_threadargsproto_);
 /* connect range variables in _p that hoc is supposed to know about */
 static const char *_mechanism[] = {
 "6.2.0",
"gaines_node",
 "gnapbar_gaines_node",
 "gnabar_gaines_node",
 "gkbar_gaines_node",
 "gkfbar_gaines_node",
 "gl_gaines_node",
 "ena_gaines_node",
 "ek_gaines_node",
 "el_gaines_node",
 0,
 "inap_gaines_node",
 "ina_gaines_node",
 "ik_gaines_node",
 "il_gaines_node",
 "ikf_gaines_node",
 "mp_inf_gaines_node",
 "m_inf_gaines_node",
 "h_inf_gaines_node",
 "n_inf_gaines_node",
 "s_inf_gaines_node",
 "tau_mp_gaines_node",
 "tau_m_gaines_node",
 "tau_h_gaines_node",
 "tau_n_gaines_node",
 "tau_s_gaines_node",
 0,
 "mp_gaines_node",
 "m_gaines_node",
 "h_gaines_node",
 "s_gaines_node",
 "n_gaines_node",
 0,
 0};
 
extern Prop* need_memb(Symbol*);

static void nrn_alloc(Prop* _prop) {
	Prop *prop_ion;
	double *_p; Datum *_ppvar;
 	_p = nrn_prop_data_alloc(_mechtype, 39, _prop);
 	/*initialize range parameters*/
 	gnapbar = 0.01;
 	gnabar = 3;
 	gkbar = 0.08;
 	gkfbar = 25.68;
 	gl = 0.007;
 	ena = 50;
 	ek = -90;
 	el = -90;
 	_prop->param = _p;
 	_prop->param_size = 39;
 	_ppvar = nrn_prop_datum_alloc(_mechtype, 1, _prop);
 	_prop->dparam = _ppvar;
 	/*connect ionic variables to this model*/
 
}
 static void _initlists();
  /* some states have an absolute tolerance */
 static Symbol** _atollist;
 static HocStateTolerance _hoc_state_tol[] = {
 0,0
};
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*)(Datum*));
extern void _nrn_thread_table_reg(int, void(*)(double*, Datum*, Datum*, _NrnThread*, int));
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 void _gaines_node_reg() {
	int _vectorized = 1;
  _initlists();
 	register_mech(_mechanism, nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init, hoc_nrnpointerindex, 1);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
     _nrn_setdata_reg(_mechtype, _setdata);
  hoc_register_prop_size(_mechtype, 39, 1);
  hoc_register_dparam_semantics(_mechtype, 0, "cvodeieq");
 	hoc_register_cvode(_mechtype, _ode_count, _ode_map, _ode_spec, _ode_matsol);
 	hoc_register_tolerance(_mechtype, _hoc_state_tol, &_atollist);
 	hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 gaines_node D:/Documents/access/Test3/MOD_Files/gaines_node.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
static int _reset;
static char *modelname = "Motor Axon Node channels";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
static int evaluate_fct(_threadargsprotocomma_ double);
 
static int _ode_spec1(_threadargsproto_);
/*static int _ode_matsol1(_threadargsproto_);*/
 static int _slist1[5], _dlist1[5];
 static int states(_threadargsproto_);
 
/*CVODE*/
 static int _ode_spec1 (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {int _reset = 0; {
   evaluate_fct ( _threadargscomma_ v ) ;
   Dmp = ( mp_inf - mp ) / tau_mp ;
   Dm = ( m_inf - m ) / tau_m ;
   Dn = ( n_inf - n ) / tau_n ;
   Dh = ( h_inf - h ) / tau_h ;
   Ds = ( s_inf - s ) / tau_s ;
   }
 return _reset;
}
 static int _ode_matsol1 (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
 evaluate_fct ( _threadargscomma_ v ) ;
 Dmp = Dmp  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_mp )) ;
 Dm = Dm  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_m )) ;
 Dn = Dn  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_n )) ;
 Dh = Dh  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_h )) ;
 Ds = Ds  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau_s )) ;
 return 0;
}
 /*END CVODE*/
 static int states (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) { {
   evaluate_fct ( _threadargscomma_ v ) ;
    mp = mp + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_mp)))*(- ( ( ( mp_inf ) ) / tau_mp ) / ( ( ( ( - 1.0 ) ) ) / tau_mp ) - mp) ;
    m = m + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_m)))*(- ( ( ( m_inf ) ) / tau_m ) / ( ( ( ( - 1.0 ) ) ) / tau_m ) - m) ;
    n = n + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_n)))*(- ( ( ( n_inf ) ) / tau_n ) / ( ( ( ( - 1.0 ) ) ) / tau_n ) - n) ;
    h = h + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_h)))*(- ( ( ( h_inf ) ) / tau_h ) / ( ( ( ( - 1.0 ) ) ) / tau_h ) - h) ;
    s = s + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau_s)))*(- ( ( ( s_inf ) ) / tau_s ) / ( ( ( ( - 1.0 ) ) ) / tau_s ) - s) ;
   }
  return 0;
}
 
static int  evaluate_fct ( _threadargsprotocomma_ double _lv ) {
   double _la , _lb , _lv2 ;
 _la = q10_1 * vtrap1 ( _threadargscomma_ _lv ) ;
   _lb = q10_1 * vtrap2 ( _threadargscomma_ _lv ) ;
   tau_mp = 1.0 / ( _la + _lb ) ;
   mp_inf = _la / ( _la + _lb ) ;
   _la = q10_1 * vtrap6 ( _threadargscomma_ _lv ) ;
   _lb = q10_1 * vtrap7 ( _threadargscomma_ _lv ) ;
   tau_m = 1.0 / ( _la + _lb ) ;
   m_inf = _la / ( _la + _lb ) ;
   _la = q10_2 * vtrap8 ( _threadargscomma_ _lv ) ;
   _lb = q10_2 * vtrap9 ( _threadargscomma_ _lv ) ;
   tau_h = 1.0 / ( _la + _lb ) ;
   h_inf = _la / ( _la + _lb ) ;
   _lv2 = _lv - vtraub ;
   _la = q10_3 * vtrap10 ( _threadargscomma_ _lv ) ;
   _lb = q10_3 * vtrap11 ( _threadargscomma_ _lv ) ;
   tau_s = 1.0 / ( _la + _lb ) ;
   s_inf = _la / ( _la + _lb ) ;
   _la = q10_4 * vtrap12 ( _threadargscomma_ _lv ) ;
   _lb = q10_4 * vtrap13 ( _threadargscomma_ _lv ) ;
   tau_n = 1.0 / ( _la + _lb ) ;
   n_inf = _la / ( _la + _lb ) ;
    return 0; }
 
static void _hoc_evaluate_fct(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r = 1.;
 evaluate_fct ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double vtrap1 ( _threadargsprotocomma_ double _lx ) {
   double _lvtrap1;
 if ( fabs ( ( _lx + ampB ) / ampC ) < 1e-6 ) {
     _lvtrap1 = ampA * ampC ;
     }
   else if ( _lx < - 150.0 ) {
     _lvtrap1 = 0.00086725 ;
     }
   else {
     _lvtrap1 = ( ampA * ( _lx + ampB ) ) / ( 1.0 - Exp ( _threadargscomma_ - ( _lx + ampB ) / ampC ) ) ;
     }
   
return _lvtrap1;
 }
 
static void _hoc_vtrap1(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  vtrap1 ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double vtrap2 ( _threadargsprotocomma_ double _lx ) {
   double _lvtrap2;
 if ( fabs ( ( _lx + bmpB ) / bmpC ) < 1e-6 ) {
     _lvtrap2 = bmpA * bmpC ;
     }
   else if ( _lx > 150.0 ) {
     _lvtrap2 = 1.5855e-05 ;
     }
   else {
     _lvtrap2 = ( bmpA * ( - ( _lx + bmpB ) ) ) / ( 1.0 - Exp ( _threadargscomma_ ( _lx + bmpB ) / bmpC ) ) ;
     }
   
return _lvtrap2;
 }
 
static void _hoc_vtrap2(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  vtrap2 ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double vtrap6 ( _threadargsprotocomma_ double _lx ) {
   double _lvtrap6;
 if ( fabs ( ( _lx + amB ) / amC ) < 1e-6 ) {
     _lvtrap6 = amA * amC ;
     }
   else if ( _lx < - 150.0 ) {
     _lvtrap6 = 0.15733 ;
     }
   else {
     _lvtrap6 = ( amA * ( _lx + amB ) ) / ( 1.0 - Exp ( _threadargscomma_ - ( _lx + amB ) / amC ) ) ;
     }
   
return _lvtrap6;
 }
 
static void _hoc_vtrap6(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  vtrap6 ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double vtrap7 ( _threadargsprotocomma_ double _lx ) {
   double _lvtrap7;
 if ( fabs ( ( _lx + bmB ) / bmC ) < 1e-6 ) {
     _lvtrap7 = bmA * bmC ;
     }
   else if ( _lx > 150.0 ) {
     _lvtrap7 = 0.0057268 ;
     }
   else {
     _lvtrap7 = ( bmA * ( - ( _lx + bmB ) ) ) / ( 1.0 - Exp ( _threadargscomma_ ( _lx + bmB ) / bmC ) ) ;
     }
   
return _lvtrap7;
 }
 
static void _hoc_vtrap7(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  vtrap7 ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double vtrap8 ( _threadargsprotocomma_ double _lx ) {
   double _lvtrap8;
 if ( fabs ( ( _lx + ahB ) / ahC ) < 1e-6 ) {
     _lvtrap8 = ahA * ahC ;
     }
   else if ( _lx > 150.0 ) {
     _lvtrap8 = 0.0032594 ;
     }
   else {
     _lvtrap8 = ( ahA * ( - ( _lx + ahB ) ) ) / ( 1.0 - Exp ( _threadargscomma_ ( _lx + ahB ) / ahC ) ) ;
     }
   
return _lvtrap8;
 }
 
static void _hoc_vtrap8(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  vtrap8 ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double vtrap9 ( _threadargsprotocomma_ double _lx ) {
   double _lvtrap9;
 if ( _lx < - 150.0 ) {
     _lvtrap9 = 0.0014054 ;
     }
   else {
     _lvtrap9 = bhA / ( 1.0 + Exp ( _threadargscomma_ - ( _lx + bhB ) / bhC ) ) ;
     }
   
return _lvtrap9;
 }
 
static void _hoc_vtrap9(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  vtrap9 ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double vtrap10 ( _threadargsprotocomma_ double _lx ) {
   double _lvtrap10;
 if ( _lx < - 150.0 ) {
     _lvtrap10 = 3.3484e-05 ;
     }
   else {
     _lvtrap10 = asA / ( Exp ( _threadargscomma_ ( _lx - vtraub + asB ) / asC ) + 1.0 ) ;
     }
   
return _lvtrap10;
 }
 
static void _hoc_vtrap10(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  vtrap10 ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double vtrap11 ( _threadargsprotocomma_ double _lx ) {
   double _lvtrap11;
 if ( _lx < - 150.0 ) {
     _lvtrap11 = 3.3484e-06 ;
     }
   else {
     _lvtrap11 = bsA / ( Exp ( _threadargscomma_ ( _lx - vtraub + bsB ) / bsC ) + 1.0 ) ;
     }
   
return _lvtrap11;
 }
 
static void _hoc_vtrap11(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  vtrap11 ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double vtrap12 ( _threadargsprotocomma_ double _lx ) {
   double _lvtrap12;
 _lvtrap12 = anA * ( _lx - anB ) / ( 1.0 - Exp ( _threadargscomma_ ( anB - _lx ) / anC ) ) ;
   
return _lvtrap12;
 }
 
static void _hoc_vtrap12(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  vtrap12 ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double vtrap13 ( _threadargsprotocomma_ double _lx ) {
   double _lvtrap13;
 _lvtrap13 = bnA * ( bnB - _lx ) / ( 1.0 - Exp ( _threadargscomma_ ( _lx - bnB ) / bnC ) ) ;
   
return _lvtrap13;
 }
 
static void _hoc_vtrap13(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  vtrap13 ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double Exp ( _threadargsprotocomma_ double _lx ) {
   double _lExp;
 if ( _lx < - 100.0 ) {
     _lExp = 0.0 ;
     }
   else {
     _lExp = exp ( _lx ) ;
     }
   
return _lExp;
 }
 
static void _hoc_Exp(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  Exp ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
static int _ode_count(int _type){ return 5;}
 
static void _ode_spec(_NrnThread* _nt, _Memb_list* _ml, int _type) {
   double* _p; Datum* _ppvar; Datum* _thread;
   Node* _nd; double _v; int _iml, _cntml;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;
  for (_iml = 0; _iml < _cntml; ++_iml) {
    _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
    _nd = _ml->_nodelist[_iml];
    v = NODEV(_nd);
     _ode_spec1 (_p, _ppvar, _thread, _nt);
 }}
 
static void _ode_map(int _ieq, double** _pv, double** _pvdot, double* _pp, Datum* _ppd, double* _atol, int _type) { 
	double* _p; Datum* _ppvar;
 	int _i; _p = _pp; _ppvar = _ppd;
	_cvode_ieq = _ieq;
	for (_i=0; _i < 5; ++_i) {
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
 _ode_matsol_instance1(_threadargs_);
 }}

static void initmodel(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
  int _i; double _save;{
  h = h0;
  m = m0;
  mp = mp0;
  n = n0;
  s = s0;
 {
   q10_1 = pow( 2.2 , ( ( celsius - 20.0 ) / 10.0 ) ) ;
   q10_2 = pow( 2.9 , ( ( celsius - 20.0 ) / 10.0 ) ) ;
   q10_3 = pow( 3.0 , ( ( celsius - 36.0 ) / 10.0 ) ) ;
   q10_4 = pow( 3.0 , ( ( celsius - 34.0 ) / 10.0 ) ) ;
   evaluate_fct ( _threadargscomma_ v ) ;
   mp = mp_inf ;
   m = m_inf ;
   h = h_inf ;
   n = n_inf ;
   s = s_inf ;
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
 initmodel(_p, _ppvar, _thread, _nt);
}
}

static double _nrn_current(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt, double _v){double _current=0.;v=_v;{ {
   inap = gnapbar * mp * mp * mp * ( v - ena ) ;
   ina = gnabar * m * m * m * h * ( v - ena ) ;
   ikf = gkfbar * n * n * n * n * ( v - ek ) ;
   ik = gkbar * s * ( v - ek ) ;
   il = gl * ( v - el ) ;
   }
 _current += ikf;
 _current += ina;
 _current += inap;
 _current += ik;
 _current += il;

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
 _g = _nrn_current(_p, _ppvar, _thread, _nt, _v + .001);
 	{ _rhs = _nrn_current(_p, _ppvar, _thread, _nt, _v);
 	}
 _g = (_g - _rhs)/.001;
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
 {   states(_p, _ppvar, _thread, _nt);
  }}}

}

static void terminal(){}

static void _initlists(){
 double _x; double* _p = &_x;
 int _i; static int _first = 1;
  if (!_first) return;
 _slist1[0] = &(mp) - _p;  _dlist1[0] = &(Dmp) - _p;
 _slist1[1] = &(m) - _p;  _dlist1[1] = &(Dm) - _p;
 _slist1[2] = &(n) - _p;  _dlist1[2] = &(Dn) - _p;
 _slist1[3] = &(h) - _p;  _dlist1[3] = &(Dh) - _p;
 _slist1[4] = &(s) - _p;  _dlist1[4] = &(Ds) - _p;
_first = 0;
}

#if defined(__cplusplus)
} /* extern "C" */
#endif

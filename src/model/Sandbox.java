/*
 * Sandbox.java
 */
import org.json.*;
import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Aug 31 2019, 09:22 by COMSOL 5.4.0.388. */
public class Sandbox {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model.modelPath("D:\\Documents\\ModularCuffs");

    model.label("UNI_TUBECUFF.mph");

    model.param().set("N_holes_EM", "0");
    model.param().set("Theta_EM", "theta_contact_EM+((2*(360*arc_ext_EM)/(2*pi*R_in_EM)) [deg])");
    model.param().set("Center_EM", "10 [mm]");
    model.param().set("R_in_EM", "max(r_nerve_EM+thk_medium_gap_internal_EM,r_cuff_in_pre_EM)");
    model.param().set("R_out_EM", "R_in_EM+thk_cuff_EM");
    model.param().set("L_EM", "3*z_elec_EM");
    model.param().set("Rot_def_EM", "-(360*arc_ext_EM)/(2*pi*R_in_EM)");
    model.param().set("D_hole_EM", "NaN");
    model.param().set("Buffer_hole_EM", "NaN");
    model.param().set("L_holecenter_cuffseam_EM", "NaN");
    model.param().set("Pitch_holecenter_holecenter_EM", "NaN");
    model.param().set("r_nerve_EM", "1.3 [mm]");
    model.param().set("thk_medium_gap_internal_EM", "0 [mm]");
    model.param().set("r_cuff_in_pre_EM", "1.651 [mm]");
    model.param().set("thk_cuff_EM", "1 [mm]");
    model.param().set("z_elec_EM", "1.397 [mm]");
    model.param().set("arc_ext_EM", "0.5 [mm]");
    model.param().set("theta_contact_pre_EM", "256.4287 [deg]");
    model.param().set("theta_contact_EM", "theta_contact_pre_EM*(r_cuff_in_pre_EM/R_in_EM)");
    model.param().set("z_nerve_EM", "20 [mm]");
    model.param().group().create("par2");
    model.param("par2").set("N_holes_M", "0");
    model.param("par2").set("Theta_M", "percent_circ_cuff_M*360 [deg]");
    model.param("par2").set("Center_M", "2*10 [mm]");
    model.param("par2").set("R_in_M", "max(r_nerve_M+thk_medium_gap_internal_M,r_cuff_in_pre_M)");
    model.param("par2").set("R_out_M", "R_in_M+thk_cuff_M");
    model.param("par2").set("L_M", "10 [mm]");
    model.param("par2").set("Rot_def_M", "0");
    model.param("par2").set("D_hole_M", "NaN");
    model.param("par2").set("Buffer_hole_M", "NaN");
    model.param("par2").set("L_holecenter_cuffseam_M", "NaN");
    model.param("par2").set("Pitch_holecenter_holecenter_M", "NaN");
    model.param("par2").set("percent_circ_cuff_M", "percent_circ_cuff_pre_M*(r_cuff_in_pre_M/R_in_M)");
    model.param("par2").set("percent_circ_cuff_pre_M", "1");
    model.param("par2").set("z_nerve_M", "20 [mm]");
    model.param("par2").set("r_cuff_in_pre_M", "1.5 [mm]");
    model.param("par2").set("r_nerve_M", "1.6 [mm]");
    model.param("par2").set("thk_medium_gap_internal_M", "0");
    model.param("par2").set("thk_cuff_M", "1 [mm]");
    model.param().group().create("par3");
    model.param("par3").set("N_holes_CT", "0");
    model.param("par3").set("Theta_CT", "percent_circ_cuff_CT*360 [deg]");
    model.param("par3").set("Center_CT", "3*10 [mm]");
    model.param("par3").set("R_in_CT", "max(r_nerve_CT+thk_medium_gap_internal_CT,r_cuff_in_pre_CT)");
    model.param("par3").set("R_out_CT", "R_in_CT+thk_cuff_CT");
    model.param("par3").set("L_CT", "2 [mm]");
    model.param("par3").set("Rot_def_CT", "-(theta_cuff_CT-theta_contact_CT)/2");
    model.param("par3").set("D_hole_CT", "NaN");
    model.param("par3").set("Buffer_hole_CT", "NaN");
    model.param("par3").set("L_holecenter_cuffseam_CT", "NaN");
    model.param("par3").set("Pitch_holecenter_holecenter_CT", "NaN");
    model.param("par3").set("percent_circ_cuff_CT", "percent_circ_cuff_pre_CT*(r_cuff_in_pre_CT/R_in_CT)");
    model.param("par3").set("r_nerve_CT", "160 [um]");
    model.param("par3").set("z_nerve_CT", "20 [mm]");
    model.param("par3").set("thk_medium_gap_internal_CT", "0");
    model.param("par3").set("r_cuff_in_pre_CT", "150 [um]");
    model.param("par3").set("thk_cuff_CT", "0.65 [mm]");
    model.param("par3").set("theta_cuff_CT", "percent_circ_cuff_CT*360 [deg]");
    model.param("par3").set("theta_contact_CT", "360*(B_CT/(2*pi*(R_in_CT+recess_CT))) [deg]");
    model.param("par3").set("percent_circ_cuff_pre_CT", "1");
    model.param("par3").set("B_CT", "0.6 [mm]");
    model.param("par3").set("recess_CT", "0");
    model.param().group().create("par4");
    model.param("par4").set("N_holes_P", "0");
    model.param("par4").set("Theta_P", "percent_circ_cuff_P*360 [deg]");
    model.param("par4").set("Center_P", "4*10 [mm]");
    model.param("par4")
         .set("R_in_P", "max(r_nerve_P+thk_medium_gap_internal_P+2*r_conductor_P+sep_conductor_P,r_cuff_in_pre_P)");
    model.param("par4").set("R_out_P", "R_in_P+thk_cuff_P");
    model.param("par4").set("L_P", "3.5 [mm]");
    model.param("par4").set("Rot_def_P", "-((theta_cuff_P-theta_conductor_P)/2)");
    model.param("par4").set("D_hole_P", "NaN");
    model.param("par4").set("Buffer_hole_P", "NaN");
    model.param("par4").set("L_holecenter_cuffseam_P", "NaN");
    model.param("par4").set("Pitch_holecenter_holecenter_P", "NaN");
    model.param("par4").set("z_nerve_P", "20 [mm]");
    model.param("par4").set("percent_circ_cuff_P", "percent_circ_cuff_pre_P*(r_cuff_in_pre_P/R_in_P)");
    model.param("par4").set("percent_circ_cuff_pre_P", "1");
    model.param("par4").set("r_cuff_in_pre_P", "317.5 [um]");
    model.param("par4").set("r_nerve_P", "300 [um]");
    model.param("par4").set("thk_medium_gap_internal_P", "0");
    model.param("par4").set("r_conductor_P", "37.5 [um]");
    model.param("par4").set("sep_conductor_P", "10 [um]");
    model.param("par4").set("thk_cuff_P", "0.279 [mm]");
    model.param("par4").set("theta_cuff_P", "percent_circ_cuff_P*360 [deg]");
    model.param("par4").set("theta_conductor_P", "percent_circ_conductor_P*360 [deg]");
    model.param("par4").set("percent_circ_conductor_pre_P", "0.8");
    model.param("par4")
         .set("percent_circ_conductor_P", "percent_circ_conductor_pre_P*((r_cuff_in_pre_P-sep_conductor_P-2*r_conductor_P)/(R_in_P-sep_conductor_P-2*r_conductor_P))");
    model.param().group().create("par5");
    model.param().group().create("par6");
    model.param("par6").set("N_holes_ITI", "1");
    model.param("par6").set("Theta_ITI", "theta_cuff_pre_ITI*(r_cuff_in_pre_ITI/R_in_ITI)");
    model.param("par6").set("Center_IT", "5*10 [mm]");
    model.param("par6").set("R_in_ITI", "max(r_nerve_IT+thk_medium_gap_internal_IT,r_cuff_in_pre_ITI)");
    model.param("par6").set("R_out_ITI", "R_in_ITI+thk_cuff_ITI");
    model.param("par6").set("L_IT", "0.354 [inch]");
    model.param("par6").set("Rot_def_ITI", "0");
    model.param("par6").set("D_hole_ITI", "0.02 [inch]");
    model.param("par6").set("Buffer_hole_ITI", "150 [um]");
    model.param("par6").set("L_holecenter_cuffseam_ITI", "0.03 [inch]");
    model.param("par6").set("N_holes_ITF", "2");
    model.param("par6")
         .set("Theta_ITF", "theta_cuff_pre_ITF*((r_cuff_in_pre_ITF+thk_cuff_ITI+thk_gap_cuff_furl_IT)/(R_in_ITI+thk_cuff_ITI+thk_gap_cuff_furl_IT))");
    model.param("par6").set("R_in_ITF", "R_in_ITI+thk_cuff_ITI+thk_gap_cuff_furl_IT");
    model.param("par6").set("R_out_ITF", "R_in_ITI+thk_cuff_ITI+thk_gap_cuff_furl_IT+thk_furl_ITF");
    model.param("par6").set("Rot_def_ITF", "-((2*pi-Theta_ITI)/2)-(Theta_ITF/2)");
    model.param("par6").set("D_hole_ITF", "0.02 [inch]");
    model.param("par6").set("Buffer_hole_ITF", "Buffer_hole_ITI");
    model.param("par6").set("L_holecenter_cuffseam_ITF", "(pi*2*R_in_ITF)*(Theta_ITF/(2*pi))-0.03 [inch]");
    model.param("par6").set("theta_cuff_pre_ITI", "360 [deg]");
    model.param("par6").set("r_cuff_in_pre_ITI", "(0.118/2) [inch]");
    model.param("par6").set("z_nerve_IT", "20 [mm]");
    model.param("par6").set("r_nerve_IT", "1.7 [mm]");
    model.param("par6").set("thk_medium_gap_internal_IT", "0");
    model.param("par6").set("thk_cuff_ITI", "r_cuff_out_pre_ITI-r_cuff_in_pre_ITI");
    model.param("par6").set("r_cuff_out_pre_ITI", "(0.178/2) [inch]");
    model.param("par6").set("Pitch_holecenter_holecenter_ITI", "0");
    model.param("par6").set("theta_cuff_pre_ITF", "250 [deg]");
    model.param("par6").set("r_cuff_in_pre_ITF", "(0.178/2) [inch]");
    model.param("par6").set("thk_gap_cuff_furl_IT", "0");
    model.param("par6").set("thk_furl_ITF", "r_furl_out_pre_ITF-r_furl_in_pre_ITF");
    model.param("par6").set("r_furl_out_pre_ITF", "(0.218/2) [inch]");
    model.param("par6").set("r_furl_in_pre_ITF", "(0.178/2) [inch]");
    model.param("par6").set("Pitch_holecenter_holecenter_ITF", "L_IT-2*0.077 [inch]");
    model.param().label("Enteromedics [EM]");
    model.param("par2").label("Madison [M]");
    model.param("par3").label("CorTec300 [CT]");
    model.param("par4").label("Purdue [P]");
    model.param("par5").label("Pitt (WIP)");
    model.param("par6").label("ImThera [IT: ITI+ITF]");

    model.component().create("comp1", true);

    model.component("comp1").geom().create("geom1", 3);

    model.component("comp1").mesh().create("mesh1");

    model.geom().create("part1", "Part", 3);
    model.geom().create("part2", "Part", 3);
    model.geom().create("part3", "Part", 3);
    model.geom("part1").label("TubeCuff_Primitive");
    model.geom("part1").inputParam().set("N_holes", "1");
    model.geom("part1").inputParam().set("Theta", "340 [deg]");
    model.geom("part1").inputParam().set("Center", "10 [mm]");
    model.geom("part1").inputParam().set("R_in", "1 [mm]");
    model.geom("part1").inputParam().set("R_out", "2 [mm]");
    model.geom("part1").inputParam().set("L", "5 [mm]");
    model.geom("part1").inputParam().set("Rot_def", "0 [deg]");
    model.geom("part1").inputParam().set("D_hole", "0.3 [mm]");
    model.geom("part1").inputParam().set("Buffer_hole", "0.1 [mm]");
    model.geom("part1").inputParam().set("L_holecenter_cuffseam", "0.3 [mm]");
    model.geom("part1").inputParam().set("Pitch_holecenter_holecenter", "0 [mm]");
    model.geom("part1").selection().create("csel1", "CumulativeSelection");
    model.geom("part1").selection("csel1").label("INNER CUFF SURFACE");
    model.geom("part1").selection().create("csel2", "CumulativeSelection");
    model.geom("part1").selection("csel2").label("OUTER CUFF SURFACE");
    model.geom("part1").selection().create("csel3", "CumulativeSelection");
    model.geom("part1").selection("csel3").label("CUFF FINAL");
    model.geom("part1").selection().create("csel11", "CumulativeSelection");
    model.geom("part1").selection("csel11").label("CUFF wGAP PRE HOLES");
    model.geom("part1").selection().create("csel4", "CumulativeSelection");
    model.geom("part1").selection("csel4").label("CUFF PRE GAP");
    model.geom("part1").selection().create("csel10", "CumulativeSelection");
    model.geom("part1").selection("csel10").label("CUFF PRE GAP PRE HOLES");
    model.geom("part1").selection().create("csel5", "CumulativeSelection");
    model.geom("part1").selection("csel5").label("CUFF GAP CROSS SECTION");
    model.geom("part1").selection().create("csel6", "CumulativeSelection");
    model.geom("part1").selection("csel6").label("CUFF GAP");
    model.geom("part1").selection().create("csel7", "CumulativeSelection");
    model.geom("part1").selection("csel7").label("CUFF PRE HOLES");
    model.geom("part1").selection().create("csel8", "CumulativeSelection");
    model.geom("part1").selection("csel8").label("HOLE 1");
    model.geom("part1").selection().create("csel9", "CumulativeSelection");
    model.geom("part1").selection("csel9").label("HOLES");
    model.geom("part1").create("cyl1", "Cylinder");
    model.geom("part1").feature("cyl1").label("Make Inner Cuff Surface");
    model.geom("part1").feature("cyl1").set("contributeto", "csel1");
    model.geom("part1").feature("cyl1").set("pos", new String[]{"0", "0", "Center-(L/2)"});
    model.geom("part1").feature("cyl1").set("r", "R_in");
    model.geom("part1").feature("cyl1").set("h", "L");
    model.geom("part1").create("cyl2", "Cylinder");
    model.geom("part1").feature("cyl2").label("Make Outer Cuff Surface");
    model.geom("part1").feature("cyl2").set("contributeto", "csel2");
    model.geom("part1").feature("cyl2").set("pos", new String[]{"0", "0", "Center-(L/2)"});
    model.geom("part1").feature("cyl2").set("r", "R_out");
    model.geom("part1").feature("cyl2").set("h", "L");
    model.geom("part1").create("if1", "If");
    model.geom("part1").feature("if1").label("If (No Gap AND No Holes)");
    model.geom("part1").feature("if1").set("condition", "(Theta==360) && (N_holes==0)");
    model.geom("part1").create("dif1", "Difference");
    model.geom("part1").feature("dif1").label("Remove Domain Within Inner Cuff Surface");
    model.geom("part1").feature("dif1").set("contributeto", "csel3");
    model.geom("part1").feature("dif1").selection("input").named("csel2");
    model.geom("part1").feature("dif1").selection("input2").named("csel1");
    model.geom("part1").create("elseif1", "ElseIf");
    model.geom("part1").feature("elseif1").label("If (Gap       AND No Holes)");
    model.geom("part1").feature("elseif1").set("condition", "(Theta<360) && (N_holes==0)");
    model.geom("part1").create("dif2", "Difference");
    model.geom("part1").feature("dif2").label("Remove Domain Within Inner Cuff Surface 1");
    model.geom("part1").feature("dif2").set("contributeto", "csel4");
    model.geom("part1").feature("dif2").selection("input").named("csel2");
    model.geom("part1").feature("dif2").selection("input2").named("csel1");
    model.geom("part1").create("wp1", "WorkPlane");
    model.geom("part1").feature("wp1").label("Make Cuff Gap Cross Section");
    model.geom("part1").feature("wp1").set("contributeto", "csel5");
    model.geom("part1").feature("wp1").set("quickplane", "xz");
    model.geom("part1").feature("wp1").set("unite", true);
    model.geom("part1").feature("wp1").geom().create("r1", "Rectangle");
    model.geom("part1").feature("wp1").geom().feature("r1").label("Cuff Gap Cross Section");
    model.geom("part1").feature("wp1").geom().feature("r1")
         .set("pos", new String[]{"R_in+((R_out-R_in)/2)", "Center"});
    model.geom("part1").feature("wp1").geom().feature("r1").set("base", "center");
    model.geom("part1").feature("wp1").geom().feature("r1").set("size", new String[]{"R_out-R_in", "L"});
    model.geom("part1").create("rev1", "Revolve");
    model.geom("part1").feature("rev1").label("Make Cuff Gap");
    model.geom("part1").feature("rev1").set("contributeto", "csel6");
    model.geom("part1").feature("rev1").set("angle1", "Theta");
    model.geom("part1").feature("rev1").selection("input").set("wp1");
    model.geom("part1").create("dif3", "Difference");
    model.geom("part1").feature("dif3").label("Remove Cuff Gap");
    model.geom("part1").feature("dif3").set("contributeto", "csel3");
    model.geom("part1").feature("dif3").selection("input").named("csel4");
    model.geom("part1").feature("dif3").selection("input2").named("csel6");
    model.geom("part1").create("rot4", "Rotate");
    model.geom("part1").feature("rot4").label("Rotate to Default Conformation 1");
    model.geom("part1").feature("rot4").set("rot", "Rot_def");
    model.geom("part1").feature("rot4").selection("input").named("csel3");
    model.geom("part1").create("elseif2", "ElseIf");
    model.geom("part1").feature("elseif2").label("If (No Gap AND       Holes)");
    model.geom("part1").feature("elseif2").set("condition", "(Theta==360) && (N_holes>0)");
    model.geom("part1").create("dif4", "Difference");
    model.geom("part1").feature("dif4").label("Remove Domain Within Inner Cuff Surface 2");
    model.geom("part1").feature("dif4").set("contributeto", "csel7");
    model.geom("part1").feature("dif4").selection("input").named("csel2");
    model.geom("part1").feature("dif4").selection("input2").named("csel1");
    model.geom("part1").create("econ1", "ECone");
    model.geom("part1").feature("econ1").label("Make Hole Shape");
    model.geom("part1").feature("econ1").set("contributeto", "csel9");
    model.geom("part1").feature("econ1")
         .set("pos", new String[]{"R_in-Buffer_hole/2", "0", "Center+Pitch_holecenter_holecenter/2"});
    model.geom("part1").feature("econ1").set("axis", new int[]{1, 0, 0});
    model.geom("part1").feature("econ1").set("semiaxes", new String[]{"D_hole/2", "D_hole/2"});
    model.geom("part1").feature("econ1").set("h", "(R_out-R_in)+Buffer_hole");
    model.geom("part1").feature("econ1").set("rat", "R_out/R_in");
    model.geom("part1").create("rot1", "Rotate");
    model.geom("part1").feature("rot1").label("Position Hole in Cuff");
    model.geom("part1").feature("rot1").set("rot", "(360*L_holecenter_cuffseam)/(pi*2*R_in)");
    model.geom("part1").feature("rot1").selection("input").named("csel9");
    model.geom("part1").create("dif5", "Difference");
    model.geom("part1").feature("dif5").label("Make Inner Cuff Hole");
    model.geom("part1").feature("dif5").set("contributeto", "csel3");
    model.geom("part1").feature("dif5").selection("input").named("csel7");
    model.geom("part1").feature("dif5").selection("input2").named("csel9");
    model.geom("part1").create("elseif3", "ElseIf");
    model.geom("part1").feature("elseif3").label("If (      Gap AND       Holes)");
    model.geom("part1").feature("elseif3").set("condition", "(Theta<360) && (N_holes>0)");
    model.geom("part1").create("dif6", "Difference");
    model.geom("part1").feature("dif6").label("Remove Domain Within Inner Cuff Surface 3");
    model.geom("part1").feature("dif6").set("contributeto", "csel10");
    model.geom("part1").feature("dif6").selection("input").named("csel2");
    model.geom("part1").feature("dif6").selection("input2").named("csel1");
    model.geom("part1").create("wp2", "WorkPlane");
    model.geom("part1").feature("wp2").label("Make Cuff Gap Cross Section 1");
    model.geom("part1").feature("wp2").set("contributeto", "csel5");
    model.geom("part1").feature("wp2").set("quickplane", "xz");
    model.geom("part1").feature("wp2").set("unite", true);
    model.geom("part1").feature("wp2").geom().create("r1", "Rectangle");
    model.geom("part1").feature("wp2").geom().feature("r1").label("Cuff Gap Cross Section");
    model.geom("part1").feature("wp2").geom().feature("r1")
         .set("pos", new String[]{"R_in+((R_out-R_in)/2)", "Center"});
    model.geom("part1").feature("wp2").geom().feature("r1").set("base", "center");
    model.geom("part1").feature("wp2").geom().feature("r1").set("size", new String[]{"R_out-R_in", "L"});
    model.geom("part1").create("rev2", "Revolve");
    model.geom("part1").feature("rev2").label("Make Cuff Gap 1");
    model.geom("part1").feature("rev2").set("contributeto", "csel6");
    model.geom("part1").feature("rev2").set("angle1", "Theta");
    model.geom("part1").feature("rev2").selection("input").named("csel5");
    model.geom("part1").create("dif7", "Difference");
    model.geom("part1").feature("dif7").label("Remove Cuff Gap 1");
    model.geom("part1").feature("dif7").set("contributeto", "csel11");
    model.geom("part1").feature("dif7").selection("input").named("csel10");
    model.geom("part1").feature("dif7").selection("input2").named("csel6");
    model.geom("part1").create("econ2", "ECone");
    model.geom("part1").feature("econ2").label("Make Hole Shape 1");
    model.geom("part1").feature("econ2").set("contributeto", "csel9");
    model.geom("part1").feature("econ2")
         .set("pos", new String[]{"R_in-Buffer_hole/2", "0", "Center+Pitch_holecenter_holecenter/2"});
    model.geom("part1").feature("econ2").set("axis", new int[]{1, 0, 0});
    model.geom("part1").feature("econ2").set("semiaxes", new String[]{"D_hole/2", "D_hole/2"});
    model.geom("part1").feature("econ2").set("h", "(R_out-R_in)+Buffer_hole");
    model.geom("part1").feature("econ2").set("rat", "R_out/R_in");
    model.geom("part1").create("rot2", "Rotate");
    model.geom("part1").feature("rot2").label("Position Hole in Cuff 1");
    model.geom("part1").feature("rot2").set("rot", "(360*L_holecenter_cuffseam)/(pi*2*R_in)");
    model.geom("part1").feature("rot2").selection("input").named("csel9");
    model.geom("part1").create("dif8", "Difference");
    model.geom("part1").feature("dif8").label("Make Inner Cuff Hole 1");
    model.geom("part1").feature("dif8").set("contributeto", "csel3");
    model.geom("part1").feature("dif8").selection("input").named("csel11");
    model.geom("part1").feature("dif8").selection("input2").named("csel9");
    model.geom("part1").create("rot3", "Rotate");
    model.geom("part1").feature("rot3").label("Rotate to Default Conformation");
    model.geom("part1").feature("rot3").set("rot", "Rot_def");
    model.geom("part1").feature("rot3").selection("input").named("csel3");
    model.geom("part1").create("endif1", "EndIf");
    model.geom("part1").run();
    model.geom("part2").label("RibbonContact");
    model.geom("part2").inputParam().set("Test", "NaN");
    model.geom("part3").label("WireContact");
    model.geom("part3").inputParam().set("Test", "NaN");
    model.component("comp1").geom("geom1").create("pi8", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi8").label("Enteromedics");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("inputexpr", "N_holes", "N_holes_EM");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("inputexpr", "Theta", "Theta_EM");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("inputexpr", "Center", "Center_EM");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("inputexpr", "R_in", "R_in_EM");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("inputexpr", "R_out", "R_out_EM");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("inputexpr", "L", "L_EM");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("inputexpr", "Rot_def", "Rot_def_EM");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("inputexpr", "D_hole", "D_hole_EM");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("inputexpr", "Buffer_hole", "Buffer_hole_EM");
    model.component("comp1").geom("geom1").feature("pi8")
         .setEntry("inputexpr", "L_holecenter_cuffseam", "L_holecenter_cuffseam_EM");
    model.component("comp1").geom("geom1").feature("pi8")
         .setEntry("inputexpr", "Pitch_holecenter_holecenter", "Pitch_holecenter_holecenter_EM");
    model.component("comp1").geom("geom1").feature("pi8").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").create("pi2", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi2").label("Madison");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "N_holes", "N_holes_M");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "Theta", "Theta_M");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "Center", "Center_M");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "R_in", "R_in_M");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "R_out", "R_out_M");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "L", "L_M");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "Rot_def", "Rot_def_M");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "D_hole", "D_hole_M");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "Buffer_hole", "Buffer_hole_M");
    model.component("comp1").geom("geom1").feature("pi2")
         .setEntry("inputexpr", "L_holecenter_cuffseam", "L_holecenter_cuffseam_M");
    model.component("comp1").geom("geom1").feature("pi2")
         .setEntry("inputexpr", "Pitch_holecenter_holecenter", "Pitch_holecenter_holecenter_M");
    model.component("comp1").geom("geom1").feature("pi2").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").create("pi3", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi3").label("CorTec300");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "N_holes", "N_holes_CT");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "Theta", "Theta_CT");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "Center", "Center_CT");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "R_in", "R_in_CT");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "R_out", "R_out_CT");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "L", "L_CT");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "Rot_def", "Rot_def_CT");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "D_hole", "D_hole_CT");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "Buffer_hole", "Buffer_hole_CT");
    model.component("comp1").geom("geom1").feature("pi3")
         .setEntry("inputexpr", "L_holecenter_cuffseam", "L_holecenter_cuffseam_CT");
    model.component("comp1").geom("geom1").feature("pi3")
         .setEntry("inputexpr", "Pitch_holecenter_holecenter", "Pitch_holecenter_holecenter_CT");
    model.component("comp1").geom("geom1").feature("pi3").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").create("pi4", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi4").label("Purdue");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "N_holes", "N_holes_P");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "Theta", "Theta_P");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "Center", "Center_P");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "R_in", "R_in_P");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "R_out", "R_out_P");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "L", "L_P");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "Rot_def", "Rot_def_P");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "D_hole", "D_hole_P");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "Buffer_hole", "Buffer_hole_P");
    model.component("comp1").geom("geom1").feature("pi4")
         .setEntry("inputexpr", "L_holecenter_cuffseam", "L_holecenter_cuffseam_P");
    model.component("comp1").geom("geom1").feature("pi4")
         .setEntry("inputexpr", "Pitch_holecenter_holecenter", "Pitch_holecenter_holecenter_P");
    model.component("comp1").geom("geom1").feature("pi4").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").create("pi5", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi5").active(false);
    model.component("comp1").geom("geom1").feature("pi5").label("Pitt (WIP)");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "N_holes", "1");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "Theta", "340 [deg]");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "Center", "50 [mm]");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "R_in", "1 [mm]");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "R_out", "2 [mm]");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "L", "5 [mm]");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "Rot_def", "0 [deg]");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "D_hole", "0.3 [mm]");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "Buffer_hole", "0.1 [mm]");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "L_holecenter_cuffseam", "0.3 [mm]");
    model.component("comp1").geom("geom1").feature("pi5")
         .setEntry("inputexpr", "Pitch_holecenter_holecenter", "0 [mm]");
    model.component("comp1").geom("geom1").feature("pi5").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").create("pi6", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi6").label("ImThera Inner");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("inputexpr", "N_holes", "N_holes_ITI");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("inputexpr", "Theta", "Theta_ITI");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("inputexpr", "Center", "Center_IT");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("inputexpr", "R_in", "R_in_ITI");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("inputexpr", "R_out", "R_out_ITI");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("inputexpr", "L", "L_IT");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("inputexpr", "Rot_def", "Rot_def_ITI");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("inputexpr", "D_hole", "D_hole_ITI");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("inputexpr", "Buffer_hole", "Buffer_hole_ITI");
    model.component("comp1").geom("geom1").feature("pi6")
         .setEntry("inputexpr", "L_holecenter_cuffseam", "L_holecenter_cuffseam_ITI");
    model.component("comp1").geom("geom1").feature("pi6")
         .setEntry("inputexpr", "Pitch_holecenter_holecenter", "Pitch_holecenter_holecenter_ITI");
    model.component("comp1").geom("geom1").feature("pi6").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").create("pi7", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi7").label("ImThera Furl");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("inputexpr", "N_holes", "N_holes_ITF");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("inputexpr", "Theta", "Theta_ITF");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("inputexpr", "Center", "Center_IT");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("inputexpr", "R_in", "R_in_ITF");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("inputexpr", "R_out", "R_out_ITF");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("inputexpr", "L", "L_IT");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("inputexpr", "Rot_def", "Rot_def_ITF");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("inputexpr", "D_hole", "D_hole_ITF");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("inputexpr", "Buffer_hole", "Buffer_hole_ITF");
    model.component("comp1").geom("geom1").feature("pi7")
         .setEntry("inputexpr", "L_holecenter_cuffseam", "L_holecenter_cuffseam_ITF");
    model.component("comp1").geom("geom1").feature("pi7")
         .setEntry("inputexpr", "Pitch_holecenter_holecenter", "Pitch_holecenter_holecenter_ITF");
    model.component("comp1").geom("geom1").feature("pi7").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").run();
    model.component("comp1").geom("geom1").run("fin");

    model.view("view5").tag("view51");
    model.view("view3").tag("view5");
    model.view("view6").tag("view61");
    model.view("view4").tag("view6");
    model.view("view51").tag("view3");
    model.view("view61").tag("view4");

    model.component("comp1").physics().create("ec", "ConductiveMedia", "geom1");

    model.component("comp1").view("view1").set("transparency", true);
    model.view("view3").label("View 3.1");
    model.view("view3").axis().set("xmin", -0.004384490195661783);
    model.view("view3").axis().set("xmax", 0.004384490195661783);
    model.view("view3").axis().set("ymin", 0.007130694109946489);
    model.view("view3").axis().set("ymax", 0.012869305908679962);
    model.view("view4").label("View 4.1");

    return model;
  }

  public static Model run2(Model model) {
    model.view("view5").label("View 5");
    model.view("view6").label("View 6");

    model.study().create("std1");
    model.study("std1").create("stat", "Stationary");

    model.geom("part1").run("cyl1");
    model.geom("part1").run("endif1");
    model.geom("part2").feature().create("wp1", "WorkPlane");
    model.geom("part2").feature("wp1").set("unite", true);
    model.geom("part2").feature("wp1").set("quickplane", "xz");
    model.geom("part2").selection().create("csel1", "CumulativeSelection");
    model.geom("part2").selection("csel1").label("CONTACT CROSS SECTION");
    model.geom("part2").feature("wp1").set("contributeto", "csel1");
    model.geom("part2").feature("wp1").geom().create("r1", "Rectangle");
    model.geom("part2").feature("wp1").geom().feature("r1").set("size", new String[]{"thk_elec", "z_elec"});
    model.geom("part2").feature("wp1").geom().feature("r1")
         .set("pos", new String[]{"r_cuff_in+recess+thk_elec/2", "0"});
    model.geom("part2").feature("wp1").geom().feature("r1").setIndex("pos", "z_center", 1);
    model.geom("part2").feature("wp1").geom().feature("r1").set("size", new String[]{"Thk_elec", "L_elec"});
    model.geom("part2").inputParam().rename("Test", "Thk_elec");
    model.geom("part2").inputParam().set("Thk_elec", "1 [mm]");
    model.geom("part2").inputParam().set("L_elec", "3 [mm]");
    model.geom("part2").inputParam().set("Thk_elec", "0.1 [mm]");
    model.geom("part2").feature("wp1").label("Contact Cross Section");
    model.geom("part2").feature("wp1").geom().feature("r1").label("Contact Cross Section");
    model.geom("part2").inputParam().set("R_in", "1 [mm]");
    model.component("comp1").geom("geom1").feature("pi8").label("Enteromedics Cuff");
    model.component("comp1").geom("geom1").feature("pi2").label("Madison Cuff");
    model.component("comp1").geom("geom1").feature("pi3").label("CorTec300 Cuff");
    model.component("comp1").geom("geom1").feature("pi4").label("Purdue Cuff");
    model.component("comp1").geom("geom1").feature("pi6").label("ImThera Inner Cuff");
    model.component("comp1").geom("geom1").feature("pi7").label("ImThera Furl Cuff");
    model.geom("part2").feature("wp1").geom().feature("r1")
         .set("pos", new String[]{"R_in+recess+thk_elec/2", "z_center"});
    model.geom("part2").inputParam().set("Recess", "0.1 [mm]");
    model.geom("part2").feature("wp1").geom().feature("r1")
         .set("pos", new String[]{"R_in+Recess+Thk_elec/2", "z_center"});
    model.geom("part2").feature("wp1").geom().feature("r1").setIndex("pos", "Center", 1);
    model.geom("part2").feature("wp1").geom().feature("r1").set("base", "center");
    model.geom("part2").inputParam().set("Center", "10 [mm]");
    model.geom("part2").run("wp1");
    model.geom("part2").run("wp1");
    model.geom("part2").feature().create("rev1", "Revolve");
    model.geom("part2").feature("rev1").set("angtype", "full");
    model.geom("part2").feature("rev1").label("Make Contact");
    model.geom("part2").feature("rev1").selection("input").named("csel1");
    model.geom("part2").feature("rev1").set("angtype", "specang");
    model.geom("part2").feature("rev1").set("angle2", "Theta_contact");
    model.geom("part2").inputParam().set("Theta_contact", "100 [deg]");
    model.geom("part2").run("rev1");
    model.geom("part2").feature().duplicate("wp2", "wp1");
    model.geom("part2").run("wp2");
    model.geom("part2").create("if1", "If");
    model.geom("part2").feature().createAfter("endif1", "EndIf", "if1");
    model.geom("part2").feature().move("wp2", 3);
    model.geom("part2").feature("if1").set("condition", "Recess>0");
    model.geom("part2").feature("wp2").label("Recess Cross Section 1");
    model.geom("part2").selection().create("csel2", "CumulativeSelection");
    model.geom("part2").selection("csel2").label("RECESS CROSS SECTION");
    model.geom("part2").feature("wp2").set("contributeto", "csel2");
    model.geom("part2").feature("wp2").geom().feature("r1").label("Recess Cross Section");
    model.geom("part2").feature("wp2").geom().selection().create("csel1", "CumulativeSelection");
    model.geom("part2").feature("wp2").geom().selection("csel1").label("Cumulative Selection 1");
    model.geom("part2").feature("wp2").geom().feature("r1").set("contributeto", "csel1");
    model.geom("part2").feature("wp2").geom().selection().create("csel2", "CumulativeSelection");
    model.geom("part2").feature("wp2").geom().selection("csel2").label("RECESS CROSS SECTION");
    model.geom("part2").feature("wp2").geom().feature("r1").set("contributeto", "csel2");
    model.geom("part2").feature("wp2").geom().feature("r1").set("size", new String[]{"Recess", "L_elec"});
    model.geom("part2").feature("wp2").geom().feature("r1").set("pos", new String[]{"R_in+Recess/2", "Center"});
    model.geom("part2").feature("wp2").geom().run("r1");
    model.geom("part2").feature("wp2").geom().run("r1");
    model.geom("part2").run("wp2");
    model.geom("part2").feature().duplicate("rev2", "rev1");
    model.geom("part2").feature("rev2").set("workplane", "wp2");
    model.geom("part2").runPre("rev2");
    model.geom("part2").feature("rev2").selection("input").named("csel2");
    model.geom("part2").run("rev2");
    model.geom("part2").run("endif1");
    model.geom("part2").inputParam().set("Recess", "0 [mm]");
    model.geom("part2").run("endif1");
    model.geom("part2").inputParam().set("Recess", "0.1 [mm]");
    model.geom("part2").run("endif1");
    model.component("comp1").geom("geom1").run("pi7");
    model.component("comp1").geom("geom1").create("pi9", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi9").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi9").set("part", "part2");
    model.component("comp1").geom("geom1").feature().move("pi9", 1);
    model.component("comp1").geom("geom1").feature("pi9").label("Enteromedics RibbonContact");
    model.component("comp1").geom("geom1").feature("pi9").setEntry("inputexpr", "Thk_elec", "Thk_elec_EM");

    model.param().set("Thk_elec_EM", "0.1 [mm]");

    model.component("comp1").geom("geom1").feature("pi9").setEntry("inputexpr", "L_elec", "L_elec_EM");

    model.param().rename("z_elec_EM", "L_elec_EM");
    model.param().set("L_EM", "3*L_elec_EM");

    model.component("comp1").geom("geom1").feature("pi9").setEntry("inputexpr", "R_in", "R_in_EM");
    model.component("comp1").geom("geom1").feature("pi9").setEntry("inputexpr", "Recess", "Recess_EM");

    model.param("par2").set("Recess_EM", "0 [mm]");

    model.component("comp1").geom("geom1").feature("pi9").setEntry("inputexpr", "Center", "Center_EM");
    model.component("comp1").geom("geom1").feature("pi9").setEntry("inputexpr", "Theta_contact", "Theta_contact_EM");
    model.component("comp1").geom("geom1").feature("pi9").setEntry("inputexpr", "Theta_contact", "theta_contact_EM");
    model.component("comp1").geom("geom1").feature("pi9").setEntry("inputexpr", "Theta_contact", "Theta_contact_EM");

    model.param().rename("theta_contact_EM", "Theta_contact_EM");

    model.component("comp1").geom("geom1").run("");

    model.param().set("Theta_EM", "Theta_contact_EM+((2*(360*arc_ext_EM)/(2*pi*R_in_EM)) [deg])");

    model.component("comp1").geom("geom1").run("pi8");
    model.component("comp1").geom("geom1").run("pi9");
    model.component("comp1").geom("geom1").feature().duplicate("pi10", "pi9");
    model.component("comp1").geom("geom1").feature().move("pi10", 3);
    model.component("comp1").geom("geom1").feature("pi10").label("Madison RibbonContact");
    model.component("comp1").geom("geom1").feature("pi10").setEntry("inputexpr", "Thk_elec", "Thk_elec_M");
    model.component("comp1").geom("geom1").feature("pi10").setEntry("inputexpr", "L_elec", "L_elec_M");
    model.component("comp1").geom("geom1").feature("pi10").setEntry("inputexpr", "R_in", "R_in_M");
    model.component("comp1").geom("geom1").feature("pi10").setEntry("inputexpr", "Recess", "Recess_M");
    model.component("comp1").geom("geom1").feature("pi10").setEntry("inputexpr", "Center", "Center_M");
    model.component("comp1").geom("geom1").feature("pi10").setEntry("inputexpr", "Theta_contact", "Theta_contact_M");

    model.param("par2").set("Thk_elec_M", "0.05 [mm]");

    model.geom("part2").run("endif1");
    model.geom("part2").create("pt1", "Point");
    model.geom("part2").feature("pt1").label("src");
    model.geom("part2").selection().create("csel3", "CumulativeSelection");
    model.geom("part2").selection("csel3").label("SRC");
    model.geom("part2").feature("pt1").set("contributeto", "csel3");
    model.geom("part2").feature("pt1").setIndex("p", "cos(Theta_contact/2)", 0);
    model.geom("part2").feature("pt1").setIndex("p", "sin(Theta_contact/2)", 1);
    model.geom("part2").feature("pt1").setIndex("p", "Center", 2);
    model.geom("part2").feature("pt1").setIndex("p", "(R_in+Recess+Thk_elec/2)*cos(Theta_contact/2)", 0);
    model.geom("part2").feature("pt1").setIndex("p", "(R_in+Recess+Thk_elec/2)*sin(Theta_contact/2)", 1);
    model.geom("part2").run("pt1");

    model.view("view5").set("transparency", true);

    model.component("comp1").geom("geom1").run("pi9");
    model.component("comp1").geom("geom1").run("pi2");

    model.param("par2").set("L_elec", "1 [mm]");
    model.param().rename("L_elec", "L_elec_M");
    model.param().rename("Recess_EM", "Recess_M");
    model.param().set("Recess_EM", "0 [mm]");

    model.component("comp1").geom("geom1").runPre("pi9");
    model.component("comp1").geom("geom1").run("pi9");
    model.component("comp1").geom("geom1").run("pi2");

    model.param("par2").set("Theta_elec_M", "360*(w_elec_M/(pi*2*(r_cuff_in+recess))) [deg]");
    model.param("par2").set("w_elec_M", "1 [mm]");
    model.param("par2").set("Theta_elec_M", "360*(w_elec_M/(pi*2*(R_in_M+Recess_M))) [deg]");
    model.param().rename("Theta_elec_M", "Theta_contact_M");

    model.component("comp1").geom("geom1").run("pi10");
    model.geom("part2").feature("rev1").set("angle1", "Rot_def");
    model.geom("part2").inputParam().set("Rot_def", "0 [deg]");
    model.geom("part2").feature("rev1").set("angle2", "Rot_def+Theta_contact");
    model.geom("part2").feature("rev2").label("Make Recess");
    model.geom("part2").feature("rev2").set("angle1", "Rot_def");
    model.geom("part2").feature("rev2").set("angle2", "Rot_def+Theta_contact");
    model.component("comp1").geom("geom1").run("fin");
    model.component("comp1").geom("geom1").run("pi10");
    model.component("comp1").geom("geom1").feature("pi10").setEntry("inputexpr", "Rot_def", "Rot_def_M");
    model.component("comp1").geom("geom1").run("pi10");
    model.component("comp1").geom("geom1").feature("pi10").setEntry("inputexpr", "Rot_def", "Theta_M/2");
    model.component("comp1").geom("geom1").run("pi10");
    model.component("comp1").geom("geom1").feature("pi10")
         .setEntry("inputexpr", "Rot_def", "Rot_def_M-Theta_contact_M/2");
    model.component("comp1").geom("geom1").run("pi10");
    model.geom("part2").feature("rev1").set("angle1", "Rot_def-(Theta_contact/2)");
    model.geom("part2").feature("rev1").set("angle2", "Rot_def+(Theta_contact/2)");
    model.component("comp1").geom("geom1").run("pi9");
    model.geom("part2").feature("rev1").set("angle1", "Rot_def");
    model.geom("part2").feature("rev1").set("angle2", "Rot_def+Theta_contact");
    model.component("comp1").geom("geom1").run("pi9");
    model.component("comp1").geom("geom1").run("pi2");
    model.component("comp1").geom("geom1").run("pi10");
    model.component("comp1").geom("geom1").feature("pi10").setEntry("inputexpr", "Rot_def", 0);
    model.component("comp1").geom("geom1").run("pi10");
    model.geom("part2").feature("rev1").set("angle2", "Rot_def+Theta_contact/2");
    model.geom("part2").feature("rev1").set("angle1", "Rot_def-Theta_contact/2");
    model.geom("part2").run("rev1");
    model.component("comp1").geom("geom1").run("pi10");
    model.geom("part2").feature("rev1").set("angle1", 0);
    model.geom("part2").feature("rev1").set("angle2", "Rot_def+Theta_contact");
    model.geom("part2").run("rev1");
    model.component("comp1").geom("geom1").run("fin");
    model.component("comp1").geom("geom1").run("pi10");
    model.component("comp1").geom("geom1").feature("pi10").setEntry("inputexpr", "Rot_def", "Theta_EM-");
    model.component("comp1").geom("geom1").feature("pi10")
         .setEntry("inputexpr", "Rot_def", "Theta_EM-(Theta_contact_M/2)");
    model.component("comp1").geom("geom1").run("pi10");
    model.component("comp1").geom("geom1").feature("pi10")
         .setEntry("inputexpr", "Rot_def", "Theta_M-(Theta_contact_M/2)");
    model.component("comp1").geom("geom1").run("pi10");
    model.geom("part2").feature("rev1").set("angle1", "Rot_def");
    model.geom("part2").run("rev1");
    model.component("comp1").geom("geom1").run("pi10");
    model.component("comp1").geom("geom1").feature("pi10")
         .setEntry("inputexpr", "Rot_def", "(Theta_M/2)-(Theta_contact_M/2)");
    model.component("comp1").geom("geom1").run("pi10");
    model.geom("part2").run("pt1");
    model.geom("part2").feature("pt1").setIndex("p", "(R_in+Recess+Thk_elec/2)*cos(Rot_def)", 0);
    model.geom("part2").feature("pt1").setIndex("p", "(R_in+Recess+Thk_elec/2)*sin(Rot_def)", 1);
    model.geom("part2").run("pt1");
    model.geom("part2").feature("pt1").setIndex("p", "(R_in+Recess+Thk_elec/2)*cos(Rot_def+Theta)", 0);
    model.geom("part2").feature("pt1").setIndex("p", "(R_in+Recess+Thk_elec/2)*cos(Rot_def+Theta_contact/2)", 0);
    model.geom("part2").feature("pt1").setIndex("p", "(R_in+Recess+Thk_elec/2)*sin(Rot_def+Theta_contact/2)", 1);
    model.geom("part2").run("pt1");
    model.component("comp1").geom("geom1").run("pi10");
    model.component("comp1").geom("geom1").run("pi10");
    model.component("comp1").geom("geom1").run("pi3");
    model.component("comp1").geom("geom1").feature().duplicate("pi11", "pi10");
    model.component("comp1").geom("geom1").feature("pi11").label("CorTec300 RibbonContact");
    model.component("comp1").geom("geom1").run("pi11");
    model.component("comp1").geom("geom1").feature("pi11").setEntry("inputexpr", "Thk_elec", "Thk_elec_CT");
    model.component("comp1").geom("geom1").feature("pi11").setEntry("inputexpr", "L_elec", "L_elec_CT");
    model.component("comp1").geom("geom1").feature("pi11").setEntry("inputexpr", "R_in", "R_in_CT");
    model.component("comp1").geom("geom1").feature("pi11").setEntry("inputexpr", "Recess", "Recess_CT");
    model.component("comp1").geom("geom1").feature("pi11").setEntry("inputexpr", "Center", "Center_CT");
    model.component("comp1").geom("geom1").feature("pi11")
         .setEntry("inputexpr", "Theta_contact", "Theta_contact_CT");
    model.component("comp1").geom("geom1").feature("pi11").setEntry("inputexpr", "Rot_def", "Rot_def_CT");
    model.component("comp1").geom("geom1").feature("pi11").setEntry("inputexpr", "Rot_def", "Rot_def_contact_CT");
    model.component("comp1").geom("geom1").feature("pi10").setEntry("inputexpr", "Rot_def", "Rot_def_contact_M");

    model.param("par2").set("Rot_def_contact_M", "(Theta_M/2)-(Theta_contact_M/2)");

    model.component("comp1").geom("geom1").run("pi10");
    model.component("comp1").geom("geom1").run("pi3");

    model.param("par3").set("Thk_elec_CT", "0.025 [mm]");
    model.param("par3").set("A_CT", "0.3 [mm]");
    model.param().remove("A_CT");
    model.param("par3").set("L_contact_CT", "0.3 [mm]");
    model.param().rename("L_contact_CT", "L_elec_CT");
    model.param("par3").set("Recess_CT", "0 [mm]");
    model.param("par3").set("Theta_contact_CT", "360*(B_CT/(2*pi*(R_in_CT+Recess_CT))) [deg]");

    model.component("comp1").geom("geom1").feature("pi11").setEntry("inputexpr", "Rot_def", 0);

    model.param("par3").set("Rot_def_contact_CT", "0");

    model.component("comp1").geom("geom1").run("pi11");
    model.component("comp1").geom("geom1").feature("pi11").setEntry("inputexpr", "Rot_def", "Rot_def_contact_CT");
    model.component("comp1").geom("geom1").run("pi11");

    model.param("par3").set("Pitch_CT", "1.5 [mm]");

    model.component("comp1").geom("geom1").feature("pi11").setEntry("inputexpr", "Center", "Center_CT+(Pitch_CT/2)");
    model.component("comp1").geom("geom1").run("pi11");
    model.component("comp1").geom("geom1").feature("pi11").label("CorTec300 RibbonContact 1");
    model.component("comp1").geom("geom1").feature().duplicate("pi12", "pi11");
    model.component("comp1").geom("geom1").feature("pi12").label("CorTec300 RibbonContact 2");
    model.component("comp1").geom("geom1").feature("pi12").setEntry("inputexpr", "Center", "Center_CT-(Pitch_CT/2)");
    model.component("comp1").geom("geom1").run("pi12");
    model.component("comp1").geom("geom1").run("pi4");
    model.geom("part3").feature().create("wp1", "WorkPlane");
    model.geom("part3").feature("wp1").set("unite", true);
    model.geom("part3").feature("wp1").label("Contact Cross Section");
    model.geom("part3").run("wp1");
    model.geom("part3").feature().create("rev1", "Revolve");
    model.geom("part3").feature("rev1").set("angtype", "full");
    model.geom("part3").feature("rev1").label("Make Contact");
    model.geom("part3").run("wp1");
    model.geom("part3").feature("wp1").set("quickplane", "zx");
    model.geom("part3").feature("wp1").geom().create("c1", "Circle");
    model.geom("part3").feature("wp1").geom().feature("c1").label("Contact Cross Section");
    model.geom("part3").feature("wp1").geom().selection().create("csel1", "CumulativeSelection");
    model.geom("part3").feature("wp1").geom().selection("csel1").label("CONTACT CROSS SECTION");
    model.geom("part3").feature("wp1").geom().feature("c1").set("contributeto", "csel1");
    model.geom("part3").feature("wp1").geom().feature("c1").set("r", "r_conductor");
    model.geom("part3").feature("wp1").geom().run("");
    model.geom("part3").feature("wp1").geom().feature("c1").set("r", "r_conductor_P");
    model.geom("part3").feature("wp1").geom().run("c1");
    model.geom("part3").run("wp1");
    model.geom("part3").selection().create("csel1", "CumulativeSelection");
    model.geom("part3").selection("csel1").label("CONTACT CROSS SECTION");
    model.geom("part3").feature("wp1").set("contributeto", "csel1");
    model.geom("part3").feature("rev1").selection("input").named("csel1");
    model.geom("part3").feature("wp1").geom().feature("c1").set("pos", new String[]{"z_center_P", "0"});

    model.param("par4").set("Pitch_P", "1.5 [mm]");

    model.geom("part3").feature("wp1").geom().feature("c1").set("pos", new String[]{"Center_Pitch_P", "0"});
    model.geom("part3").feature("wp1").geom().run("");
    model.geom("part3").feature("wp1").geom().feature("c1").set("pos", new String[]{"Center_P-Pitch_P", "0"});
    model.geom("part3").feature("wp1").geom().run("c1");
    model.geom("part3").runPre("rev1");
    model.geom("part3").run("rev1");
    model.geom("part3").feature("rev1").set("axis", new int[]{1, 0});
    model.geom("part3").run("wp1");
    model.geom("part3").feature("wp1").geom().run("c1");
    model.geom("part3").feature("wp1").geom().feature("c1")
         .setIndex("pos", "R_in_P-r_conductor_P-sep_conductor_P", 1);
    model.geom("part3").feature("wp1").geom().run("c1");
    model.geom("part3").run("rev1");
    model.geom("part3").feature("rev1").set("angtype", "specang");
    model.geom("part3").feature("rev1").set("angle2", "theta_conductor_P");
    model.geom("part3").run("rev1");
    model.component("comp1").geom("geom1").run("pi4");
    model.component("comp1").geom("geom1").run("pi4");
    model.component("comp1").geom("geom1").create("pi13", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi13").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi13").set("part", "part3");
    model.component("comp1").geom("geom1").feature("pi13").label("Purdue WireContact 1");
    model.component("comp1").geom("geom1").run("pi13");
    model.geom("part3").inputParam().rename("Test", "r_conductor");
    model.geom("part3").inputParam().set("r_conductor", "r_conductor_P");
    model.geom("part3").inputParam().set("R_in", "R_in_P");
    model.geom("part3").inputParam().set("Center", "Center_P");
    model.geom("part3").feature("wp1").geom().feature("c1").setIndex("pos", "Center-Pitch", 0);
    model.geom("part3").feature("wp1").geom().feature("c1").set("r", "r_conductor");
    model.geom("part3").feature("wp1").geom().feature("c1").setIndex("pos", "R_in-r_conductor-sep_conductor", 1);
    model.geom("part3").inputParam().set("Pitch", "Pitch_P");
    model.geom("part3").inputParam().set("sep_conductor", "sep_conductor_P");
    model.geom("part3").feature("wp1").geom().run("c1");
    model.geom("part3").run("rev1");
    model.geom("part3").feature("rev1").set("angle2", "theta_conductor");
    model.geom("part3").inputParam().set("theta_conductor", "theta_conductor_P");
    model.geom("part3").run("rev1");
    model.geom("part3").run("rev1");
    model.geom("part2").selection().create("csel4", "CumulativeSelection");
    model.geom("part2").selection("csel4").label("CONTACT FINAL");
    model.geom("part2").feature("rev1").set("contributeto", "csel4");
    model.geom("part2").selection().create("csel5", "CumulativeSelection");
    model.geom("part2").selection("csel5").label("RECESS FINAL");
    model.geom("part2").feature("rev2").set("contributeto", "csel5");
    model.geom("part3").selection().create("csel2", "CumulativeSelection");
    model.geom("part3").selection("csel2").label("CONTACT FINAL");
    model.geom("part3").feature("rev1").set("contributeto", "csel2");
    model.component("comp1").geom("geom1").run("pi4");
    model.component("comp1").geom("geom1").feature("pi13").setEntry("inputexpr", "r_conductor", "r_conductor_P");
    model.component("comp1").geom("geom1").run("pi13");
    model.geom("part3").feature("wp1").geom().feature("c1").setIndex("pos", "Center-(Pitch/2)", 0);
    model.geom("part3").feature("wp1").geom().run("c1");
    model.component("comp1").geom("geom1").run("pi13");
    model.component("comp1").geom("geom1").feature().duplicate("pi14", "pi13");
    model.component("comp1").geom("geom1").feature("pi14").label("Purdue WireContact 2");
    model.component("comp1").geom("geom1").feature("pi13").setEntry("inputexpr", "Center", "Center_P-(Pitch/2)");
    model.component("comp1").geom("geom1").feature("pi14").setEntry("inputexpr", "Center", "Center_P+(Pitch/2)");
    model.component("comp1").geom("geom1").feature("pi14").setEntry("inputexpr", "Center", "Center_P+(Pitch_P/2)");
    model.component("comp1").geom("geom1").feature("pi13").setEntry("inputexpr", "Center", "Center_P-(Pitch_P/2)");
    model.component("comp1").geom("geom1").run("pi14");
    model.component("comp1").geom("geom1").run("pi14");
    model.component("comp1").geom("geom1").feature("pi14").active(false);
    model.component("comp1").geom("geom1").run("pi13");
    model.component("comp1").geom("geom1").feature("pi13").setEntry("inputexpr", "Center", "Center_P");
    model.component("comp1").geom("geom1").run("pi13");
    model.geom("part2").feature("wp1").geom().run("r1");
    model.geom("part3").feature("wp1").geom().feature("c1").setIndex("pos", "Center", 0);
    model.geom("part3").run("rev1");
    model.component("comp1").geom("geom1").feature("pi13").setEntry("inputexpr", "Center", "Center_P-(Pitch/2)");
    model.component("comp1").geom("geom1").run("pi4");
    model.component("comp1").geom("geom1").feature("pi13").setEntry("inputexpr", "Center", "Center_P-(Pitch_P/2)");
    model.component("comp1").geom("geom1").run("pi13");
    model.component("comp1").geom("geom1").feature("pi14").setEntry("inputexpr", "Center", "Center_P-(Pitch_P/2)");
    model.component("comp1").geom("geom1").run("pi14");
    model.component("comp1").geom("geom1").feature("pi14").active(true);
    model.component("comp1").geom("geom1").run("pi14");
    model.component("comp1").geom("geom1").feature("pi14").setEntry("inputexpr", "Center", "Center_P+(Pitch_P/2)");
    model.component("comp1").geom("geom1").run("pi14");
    model.component("comp1").geom("geom1").run("fin");
    model.geom().create("part4", "Part", 3);
    model.geom("part4").label("Circle Contact");
    model.geom("part2").label("RibbonContact_Primitive");
    model.geom("part3").label("WireContact_Primitive");
    model.geom("part4").label("Circle Contact_Primitive");
    model.geom("part4").feature().create("wp1", "WorkPlane");
    model.geom("part4").feature("wp1").set("unite", true);
    model.geom("part4").feature("wp1").label("Base Plane (pre rotation)");
    model.geom("part4").feature("wp1").set("quickplane", "yz");
    model.geom("part4").selection().create("csel1", "CumulativeSelection");
    model.geom("part4").selection("csel1").label("BASE CONTACT PLANE (PRE ROTATION)");
    model.geom("part4").feature("wp1").set("contributeto", "csel1");
    model.geom("part4").feature("wp1").label("Base Contact Plane (Pre Rrotation)");
    model.geom("part4").run("wp1");
    model.geom("part4").feature().create("wp2", "WorkPlane");
    model.geom("part4").feature("wp2").set("unite", true);
    model.geom("part4").feature("wp2").label("Rotated Plane for Recess");
    model.geom("part4").feature("wp2").geom().create("e1", "Ellipse");
    model.geom("part4").feature("wp2").geom().feature("e1").label("Contact Outline");
    model.geom("part4").feature("wp2").geom().feature("e1").set("semiaxes", new String[]{"diam_contact/2", "1"});
    model.geom("part4").feature("wp2").geom().feature("e1").setIndex("semiaxes", "b_ellipse_contact", 1);
    model.geom("part4").feature("wp2").geom().feature("e1").set("pos", new String[]{"0", "z_src"});
    model.geom("part4").feature("wp2").geom().selection().create("csel1", "CumulativeSelection");
    model.geom("part4").feature("wp2").geom().selection("csel1").label("CONTACT OUTLINE SHAPE");
    model.geom("part4").feature("wp2").geom().feature("e1").set("contributeto", "csel1");
    model.geom("part4").feature("wp2").geom().feature("e1").label("Contact Outline Shape");
    model.geom("part4").feature("wp1").label("Base Plane (Pre Rrotation)");
    model.geom("part4").selection().create("csel2", "CumulativeSelection");
    model.geom("part4").selection("csel2").label("BASE PLANE (PRE ROTATION)");
    model.geom("part4").feature("wp1").set("contributeto", "csel2");
    model.geom("part4").run("wp1");
    model.geom("part4").feature("wp2").active(false);
    model.geom("part4").feature().remove("wp2");
    model.geom("part4").run("wp1");
    model.geom("part4").create("if1", "If");
    model.geom("part4").feature().createAfter("endif1", "EndIf", "if1");
    model.geom("part4").feature("if1").label("If Recess");
    model.geom("part4").feature("if1").set("condition", "Recess>0");
    model.geom("part4").feature().duplicate("wp2", "wp1");
    model.geom("part4").feature("wp2").label("Rotated Plane for Recess");
    model.geom("part4").feature("wp2").set("planetype", "transformed");
    model.geom("part4").run("wp1");
    model.geom("part4").inputParam().set("Recess", "0.01 [mm]");
    model.geom("part4").run("if1");
    model.geom("part4").run("wp2");
    model.geom("part4").feature("wp2").set("workplane", "wp1");
    model.geom("part4").feature("wp2").set("transaxistype", "y");
    model.geom("part4").feature("wp2").set("transrot", "rotation_angle");
    model.geom("part4").inputParam().set("rotation_angle", "0 [deg]");
    model.geom("part4").selection().create("csel3", "CumulativeSelection");
    model.geom("part4").selection("csel3").label("PLANE FOR RECESS");
    model.geom("part4").feature("wp2").set("contributeto", "csel3");
    model.geom("part4").run("wp2");
    model.geom("part4").feature().create("ext1", "Extrude");
    model.geom("part4").feature("ext1").selection("input").named("csel3");
    model.geom("part4").feature("wp2").geom().create("e1", "Ellipse");
    model.geom("part4").feature("wp2").geom().feature("e1").label("Contact Outline");
    model.geom("part4").feature("wp2").geom().feature("e1").set("semiaxes", new String[]{"diam_contact/2", "1"});
    model.geom("part4").feature("wp2").geom().feature("e1").setIndex("semiaxes", "b_ellipse_contact", 1);
    model.geom("part4").feature("wp2").geom().feature("e1").set("pos", new String[]{"0", "Center"});
    model.geom("part4").inputParam().set("Center", "0 [mm]");
    model.geom("part4").feature("wp2").geom().feature("e1").setIndex("semiaxes", "diam_contact_ITC/2", 0);
    model.geom("part4").feature("wp2").geom().feature("e1").setIndex("semiaxes", "b_ellipse_contact_ITC", 1);

    model.param("par6").set("diam_contact_ITC", "0");
    model.param("par6").set("b_ellipse_contact_ITC", "0");
    model.param("par6").set("diam_contact_ITC", "2 [mm]");
    model.param("par6")
         .set("b_ellipse_contact_ITC", "(R_in_ITI+recess_depth)*cos((pi/2) - 2*pi*(((diam_contact/2) + recess_depth)/(pi*(2*r_cuff_in+2*recess_depth))))");
    model.param("par6").set("Recess_ITC", "0.1 [mm]");

    model.geom("part4").inputParam().set("Recess", "Recess_ITC");

    model.param("par6")
         .set("b_ellipse_contact_ITC", "(R_in_ITI+Recess_ITC)*cos((pi/2) - 2*pi*(((diam_contact_ITC/2) + Recess_ITC)/(pi*(2*R_in_ITI+2*Recess_ITC))))");

    model.geom("part4").feature("wp2").geom().run("e1");
    model.geom("part4").run("wp2");
    model.geom("part4").feature("wp2").geom().run("e1");
    model.geom("part4").feature("wp2").geom().feature().duplicate("e2", "e1");
    model.geom("part4").feature("wp2").geom().feature("e2").setIndex("semiaxes", "diam_contact_ITC/2", 1);
    model.geom("part4").feature("wp2").geom().run("e2");
    model.geom("part4").feature("wp2").geom().feature("e2").active(false);
    model.geom("part4").feature("wp2").geom().run("e1");
    model.geom("part4").feature("wp2").geom().run("e1");
    model.geom("part4").feature("wp2").geom().create("if1", "If");
    model.geom("part4").feature("wp2").geom().feature().createAfter("endif1", "EndIf", "if1");
    model.geom("part4").feature("wp2").geom().feature().move("if1", 0);
    model.geom("part4").feature("wp2").geom().run("if1");
    model.geom("part4").feature("wp2").geom().create("elseif1", "ElseIf");
    model.geom("part4").feature("wp2").geom().feature().move("e1", 1);
    model.geom("part4").feature("wp2").geom().feature().move("e2", 3);
    model.geom("part4").feature("wp2").geom().feature("e2").active(true);
    model.geom("part4").feature("wp2").geom().run("e2");
    model.geom("part4").feature("wp2").geom().run("e1");
    model.geom("part4").feature("wp2").geom().selection().create("csel1", "CumulativeSelection");
    model.geom("part4").feature("wp2").geom().selection("csel1").label("CONTACT OUTLINE SHAPE");
    model.geom("part4").feature("wp2").geom().feature("e1").set("contributeto", "csel1");
    model.geom("part4").feature("wp2").geom().feature("e2").set("contributeto", "csel1");
    model.geom("part4").inputParam().set("Round_def", "Round_def_ITC");

    model.param("par6").set("Round_def_ITC", "1");

    model.geom("part4").feature("wp2").geom().feature("if1").set("condition", "Round_def_ITC==1");
    model.geom("part4").feature("wp2").geom().feature("elseif1").set("condition", "Round_def_ITC==2");
    model.geom("part4").feature("wp2").geom().feature("elseif1").label("Else If Contact Outline is Circle");
    model.geom("part4").feature("wp2").geom().feature("if1").label("If Contact Surface is Circle");
    model.geom("part4").run("wp2");
    model.geom("part4").feature().create("ext2", "Extrude");
    model.geom("part4").feature("ext2").selection("input").named("csel3");
    model.geom("part4").feature("ext2").setIndex("distance", "R_in_ITI+Recess_ITI+contact_depth+overshoot", 0);

    return model;
  }

  public static Model run3(Model model) {
    model.geom("part4").feature("ext2").set("includeinput", false);
    model.geom("part4").feature("ext2").label("Make Pre Cut Recess Domains");
    model.geom("part4").inputParam().set("R_in", "R_in_ITI");
    model.geom("part4").feature("ext2").setIndex("distance", "R_in+Recess+contact_depth+overshoot", 0);

    model.param("par6").set("Contact_depth_ITC", "0.05 [mm]");

    model.geom("part4").inputParam().set("Contact_depth", "Contact_depth_ITC");
    model.geom("part4").feature("ext2").setIndex("distance", "R_in+Recess+Contact_depth+Overshoot", 0);
    model.geom("part4").inputParam().set("Overshoot", "Overshoot_ITC");

    model.param("par6").set("Overshoot_ITC", "0.05 [mm]");

    model.geom("part4").run("wp2");
    model.geom("part4").feature("ext2").setIndex("distance", "(R_in+Recess+Contact_depth+Overshoot)", 0);
    model.geom("part4").lengthUnit("\u00b5m");
    model.geom("part3").lengthUnit("\u00b5m");
    model.geom("part2").lengthUnit("\u00b5m");
    model.geom("part1").lengthUnit("\u00b5m");
    model.component("comp1").geom("geom1").run("fin");
    model.geom("part4").feature("ext2").setIndex("distance", 10, 0);
    model.geom("part4").feature("ext2").setIndex("distance", 1000, 0);
    model.geom("part4").feature("ext2").selection("input").init();
    model.geom("part4").feature("ext2").selection("input").set("wp2");
    model.geom("part4").feature("ext2").selection("input").named("csel3");
    model.geom("part4").feature().remove("ext2");
    model.geom("part4").feature().remove("ext1");
    model.geom("part4").run("wp2");
    model.geom("part4").feature().create("ext1", "Extrude");
    model.geom("part4").feature("ext1").set("workplane", "wp2");
    model.geom("part4").feature("ext1").selection("input").set("wp2");
    model.geom("part4").feature("ext1").selection("input").named("csel3");
    model.geom("part4").feature("ext1").setIndex("distance", "(R_in+Recess+Contact_depth+Overshoot)", 0);
    model.geom("part4").run("ext1");
    model.geom("part4").feature("ext1").setIndex("distance", "R_in+Recess+Contact_depth+Overshoot", 0);
    model.geom("part4").run("ext1");
    model.geom("part4").feature("ext1").label("Make Pre Cut Recess Domains");
    model.geom("part4").selection().create("csel4", "CumulativeSelection");
    model.geom("part4").selection("csel4").label("PRE CUT RECESS");
    model.geom("part4").feature("ext1").set("contributeto", "csel4");
    model.geom("part4").run("ext1");
    model.geom("part4").run("ext1");
    model.geom("part4").create("cyl1", "Cylinder");
    model.geom("part4").feature().duplicate("cyl2", "cyl1");
    model.geom("part4").feature("cyl1").label("Recess Cut In");
    model.geom("part4").feature("cyl2").label("Recess Cut Out");
    model.geom("part4").feature("cyl1").set("r", "R_in");
    model.geom("part4").feature("cyl1").set("h", "L_cuff_ITI");

    model.param("par6").label("ImThera [IT: ITI+ITF+ITC]");

    model.geom("part4").feature("cyl1").set("h", "L_IT");
    model.geom("part4").feature("cyl1").set("pos", new String[]{"0", "0", "Center-L_IT/2"});
    model.geom("part4").run("cyl1");
    model.geom("part4").selection().create("csel5", "CumulativeSelection");
    model.geom("part4").selection("csel5").label("RECESS CUTTER IN");
    model.geom("part4").feature("cyl1").set("contributeto", "csel5");
    model.geom("part4").feature("cyl2").set("r", "R_in+Recess");
    model.geom("part4").feature("cyl2").set("h", "L_IT");
    model.geom("part4").feature("cyl2").set("pos", new String[]{"0", "0", "Center-L_IT/2"});
    model.geom("part4").selection().create("csel6", "CumulativeSelection");
    model.geom("part4").selection("csel6").label("RECESS CUTTER OUT");
    model.geom("part4").feature("cyl2").set("contributeto", "csel6");
    model.geom("part4").run("cyl2");
    model.geom("part4").run("cyl2");
    model.geom("part4").create("dif1", "Difference");
    model.geom("part4").feature("dif1").selection("input").named("csel4");
    model.geom("part4").feature("dif1").selection("input2").named("csel5");
    model.geom("part4").selection().create("csel7", "CumulativeSelection");
    model.geom("part4").selection("csel7").label("RECESS FINAL");
    model.geom("part4").feature("dif1").set("contributeto", "csel7");
    model.geom("part4").run("dif1");

    model.view("view10").set("transparency", true);

    model.geom("part4").feature("dif1").label("Execute Recess Cut In");
    model.geom("part4").run("dif1");
    model.geom("part4").create("pard1", "PartitionDomains");
    model.geom("part4").feature("pard1").selection("domain").named("csel4");
    model.geom("part4").feature("pard1").set("partitionwith", "objects");
    model.geom("part4").feature("pard1").selection("object").named("csel6");
    model.geom("part4").feature("pard1").set("contributeto", "csel7");
    model.geom("part4").run("pard1");
    model.geom("part4").feature("pard1").set("keepobject", false);
    model.geom("part4").run("pard1");
    model.geom("part4").run("pard1");
    model.geom("part4").create("del1", "Delete");
    model.geom("part4").run("pard1");
    model.geom("part4").feature("del1").active(false);
    model.geom("part4").run("pard1");
    model.geom("part4").create("ballsel1", "BallSelection");
    model.geom("part4").feature("ballsel1").label("Select Overshoot");
    model.geom("part4").selection().create("csel8", "CumulativeSelection");
    model.geom("part4").selection("csel8").label("RECESS OVERSHOOT");
    model.geom("part4").feature("ballsel1").set("contributeto", "csel8");
    model.geom("part4").feature("ballsel1")
         .set("posx", "(r_cuff_in+recess_depth+contact_depth+overshoot/2)*cos(rotation_angle)");
    model.geom("part4").feature("ballsel1")
         .set("posy", "(r_cuff_in+recess_depth+contact_depth+overshoot/2)*sin(rotation_angle)");
    model.geom("part4").feature("ballsel1").set("posz", "Center");
    model.geom("part4").feature("ballsel1")
         .set("posx", "(R_in+Recess+contact_depth+overshoot/2)*cos(rotation_angle)");
    model.geom("part4").feature("ballsel1")
         .set("posy", "(R_in+Recess+contact_depth+Overshoot/2)*sin(rotation_angle)");
    model.geom("part4").feature("ballsel1")
         .set("posx", "(R_in+Recess+Contact_depth+Overshoot/2)*cos(rotation_angle)");
    model.geom("part4").feature("ballsel1")
         .set("posy", "(R_in+Recess+Contact_depth+Overshoot/2)*sin(rotation_angle)");
    model.geom("part4").run("ballsel1");
    model.geom("part4").run("ballsel1");
    model.geom("part4").feature("ballsel1").set("r", 1);
    model.geom("part4").run("ballsel1");
    model.geom("part4").feature("del1").label("Delete Recess Overshoot");
    model.geom("part4").feature("del1").selection("input").init();
    model.geom("part4").runPre("del1");
    model.geom("part4").feature("del1").active(true);
    model.geom("part4").feature("del1").selection("input").init(3);
    model.geom("part4").feature("del1").selection("input").named("csel8");
    model.geom("part4").run("del1");
    model.geom("part4").feature().duplicate("wp3", "wp2");
    model.geom("part4").feature().duplicate("ext2", "ext1");
    model.geom("part4").feature().duplicate("cyl3", "cyl1");
    model.geom("part4").feature().duplicate("cyl4", "cyl2");
    model.geom("part4").feature().duplicate("dif2", "dif1");
    model.geom("part4").feature().duplicate("pard2", "pard1");
    model.geom("part4").feature().duplicate("ballsel2", "ballsel1");
    model.geom("part4").feature().duplicate("del2", "del1");
    model.geom("part4").feature().move("del2", 18);
    model.geom("part4").feature().move("ballsel2", 17);
    model.geom("part4").feature().move("pard2", 16);
    model.geom("part4").feature().move("dif2", 15);
    model.geom("part4").feature().move("cyl4", 14);
    model.geom("part4").feature().move("cyl3", 13);
    model.geom("part4").feature().move("ext2", 12);
    model.geom("part4").feature().move("wp3", 11);
    model.geom("part4").feature("wp3").label("Rotated Plane for Contact");
    model.geom("part4").selection().create("csel9", "CumulativeSelection");
    model.geom("part4").selection("csel9").label("PLANE FOR CONTACT");
    model.geom("part4").feature("wp3").set("contributeto", "csel9");
    model.geom("part4").feature("ext2").label("Make Pre Cut Contact Domains");
    model.geom("part4").selection().create("csel10", "CumulativeSelection");
    model.geom("part4").selection("csel10").label("PRE CUT CONTACT");
    model.geom("part4").feature("ext2").set("contributeto", "csel10");
    model.geom("part4").feature("ext1").setIndex("distance", "R_in+Recess+Overshoot", 0);
    model.geom("part4").run("ext1");
    model.geom("part4").run("dif1");
    model.geom("part4").run("pard1");
    model.geom("part4").run("ballsel1");
    model.geom("part4").run("del1");
    model.geom("part4").feature("ballsel1").set("posx", "(R_in+Recess+Overshoot/2)*cos(rotation_angle)");
    model.geom("part4").feature("ballsel1").set("posy", "(R_in+Recess+Overshoot/2)*sin(rotation_angle)");
    model.geom("part4").run("ballsel1");
    model.geom("part4").run("dif1");
    model.geom("part4").run("pard1");
    model.geom("part4").run("ballsel1");
    model.geom("part4").run("del1");
    model.geom("part4").run("wp3");
    model.geom("part4").run("ext2");
    model.geom("part4").feature("ext2").set("workplane", "wp3");
    model.geom("part4").runPre("ext2");
    model.geom("part4").feature("ext2").selection("input").named("csel9");
    model.geom("part4").run("ext2");
    model.geom("part4").feature("cyl3").label("Contact Cut In");
    model.geom("part4").selection().create("csel11", "CumulativeSelection");
    model.geom("part4").selection("csel11").label("CONTACT CUTTER IN");
    model.geom("part4").feature("cyl3").set("contributeto", "csel11");
    model.geom("part4").feature("cyl3").set("r", "R_in+Recess");
    model.geom("part4").feature("cyl4").label("Contact Cut Out");
    model.geom("part4").feature("cyl4").set("r", "R_in+Recess+Contact_depth+Overshoot");
    model.geom("part4").selection().create("csel12", "CumulativeSelection");
    model.geom("part4").selection("csel12").label("CONTACT CUTTER OUT");
    model.geom("part4").feature("cyl4").set("contributeto", "csel12");
    model.geom("part4").run("cyl4");
    model.geom("part4").runPre("dif2");
    model.geom("part4").run("ext2");
    model.geom("part4").runPre("dif2");
    model.geom("part4").feature("dif2").label("Execute Contact Cut In");
    model.geom("part4").feature("dif2").selection("input").named("csel10");
    model.geom("part4").feature("dif2").selection("input2").named("csel11");
    model.geom("part4").selection().create("csel13", "CumulativeSelection");
    model.geom("part4").selection("csel13").label("CONTACT FINAL");
    model.geom("part4").feature("dif2").set("contributeto", "csel13");
    model.geom("part4").run("dif2");
    model.geom("part4").feature("pard2").selection("domain").named("csel10");
    model.geom("part4").feature("pard2").selection("object").named("csel12");
    model.geom("part4").feature("pard2").set("contributeto", "csel13");
    model.geom("part4").run("pard2");
    model.geom("part4").run("ext1");
    model.geom("part4").run("cyl1");
    model.geom("part4").run("cyl2");
    model.geom("part4").run("cyl2");
    model.geom("part4").run("dif1");
    model.geom("part4").run("pard1");
    model.geom("part4").run("ballsel1");
    model.geom("part4").run("del1");
    model.geom("part4").run("endif1");
    model.geom("part4").run("wp3");
    model.geom("part4").run("ext2");
    model.geom("part4").run("cyl3");
    model.geom("part4").run("cyl4");
    model.geom("part4").feature("cyl4").set("r", "R_in+Recess+Contact_depth");
    model.geom("part4").run("cyl4");
    model.geom("part4").run("dif2");
    model.geom("part4").run("pard2");
    model.geom("part4").run("ballsel2");
    model.geom("part4").run("del2");
    model.geom("part4").run("del2");
    model.geom("part4").create("pt1", "Point");
    model.geom("part4").feature("pt1").setIndex("p", "(R_in+Recess+Contact_depth/2)*cos(rotation_angle)", 0);
    model.geom("part4").feature("pt1").setIndex("p", "(R_in+Recess+Contact_depth/2)*sin(rotation_angle)", 1);
    model.geom("part4").feature("pt1").setIndex("p", "Center", 2);
    model.geom("part4").selection().create("csel14", "CumulativeSelection");
    model.geom("part4").selection("csel14").label("SRC");
    model.geom("part4").feature("pt1").set("contributeto", "csel14");
    model.geom("part4").run("pt1");
    model.geom("part4").feature("pt1").label("Src");
    model.geom("part4").run("pt1");
    model.geom("part4").feature("wp2").set("transrot", "Rotation_angle");
    model.geom("part4").inputParam().rename("rotation_angle", "Rotation_angle");
    model.geom("part4").inputParam().set("Center", "Center_IT");
    model.geom("part4").run("dif1");
    model.geom("part4").feature("ballsel1").set("posx", "(R_in+Recess+Overshoot/2)*cos(Rotation_angle)");
    model.geom("part4").feature("ballsel1").set("posy", "(R_in+Recess+Overshoot/2)*sin(Rotation_angle)");
    model.geom("part4").feature("wp3").set("transrot", "Rotation_angle");
    model.geom("part4").feature("ballsel2")
         .set("posx", "(R_in+Recess+Contact_depth+Overshoot/2)*cos(Rotation_angle)");
    model.geom("part4").feature("ballsel2")
         .set("posy", "(R_in+Recess+Contact_depth+Overshoot/2)*sin(Rotation_angle)");
    model.geom("part4").feature("pt1").setIndex("p", "(R_in+Recess+Contact_depth/2)*cos(Rotation_angle)", 0);
    model.geom("part4").feature("pt1").setIndex("p", "(R_in+Recess+Contact_depth/2)*sin(Rotation_angle)", 1);
    model.geom("part4").run("pt1");
    model.geom("part4").feature("wp2").geom().feature("e1").setIndex("semiaxes", "Diam_contact_ITC/2", 0);
    model.geom("part4").feature("wp2").geom().feature("e1").setIndex("semiaxes", "B_ellipse_contact_ITC", 1);
    model.geom("part4").feature("wp2").geom().feature("e1").setIndex("semiaxes", "Diam_contact/2", 0);
    model.geom("part4").feature("wp2").geom().feature("e1").setIndex("semiaxes", "B_ellipse_contact", 1);
    model.geom("part4").inputParam().set("D_contact", "diam_contact_ITC");
    model.geom("part4").inputParam().set("B_ellipse_contact", "b_ellipse_contact_ITC");
    model.geom("part4").inputParam().rename("D_contact", "Diam_contact");
    model.geom("part4").feature("wp2").geom().feature("e2").setIndex("semiaxes", "diam_contact/2", 0);
    model.geom("part4").feature("wp2").geom().feature("e2").setIndex("semiaxes", "diam_contact/2", 1);
    model.geom("part4").feature("wp2").geom().feature("e2").setIndex("semiaxes", "Diam_contact/2", 0);
    model.geom("part4").feature("wp2").geom().feature("e2").setIndex("semiaxes", "Diam_contact/2", 1);
    model.geom("part4").feature("cyl1").set("pos", new String[]{"0", "0", "Center-L/2"});
    model.geom("part4").feature("cyl1").set("h", "L");
    model.geom("part4").inputParam().set("L", "L_IT");
    model.geom("part4").run("ext1");
    model.geom("part4").run("cyl1");
    model.geom("part4").feature("cyl2").set("h", "L");
    model.geom("part4").feature("cyl2").set("pos", new String[]{"0", "0", "Center-L/2"});
    model.geom("part4").run("cyl2");
    model.geom("part4").run("dif1");
    model.geom("part4").run("pard1");
    model.geom("part4").run("ballsel1");
    model.geom("part4").run("del1");
    model.geom("part4").run("endif1");
    model.geom("part4").run("wp3");
    model.geom("part4").feature("wp3").geom().feature("e1").setIndex("semiaxes", "Diam_contact_/2", 0);
    model.geom("part4").feature("wp3").geom().feature("e1").setIndex("semiaxes", "B_ellipse_contact", 1);
    model.geom("part4").feature("wp3").geom().feature("e1").setIndex("semiaxes", "Diam_contact/2", 0);
    model.geom("part4").feature("wp3").geom().run("e1");
    model.geom("part4").feature("wp3").geom().feature("e2").setIndex("semiaxes", "Diam_contact/2", 0);
    model.geom("part4").feature("wp3").geom().feature("e2").setIndex("semiaxes", "Diam_contact/2", 1);
    model.geom("part4").feature("wp3").geom().run("e2");
    model.geom("part4").run("ext2");
    model.geom("part4").feature("cyl3").set("h", "L");
    model.geom("part4").feature("cyl3").set("pos", new String[]{"0", "0", "Center-L/2"});
    model.geom("part4").run("cyl3");
    model.geom("part4").run("cyl4");
    model.geom("part4").feature("cyl4").set("h", "L");
    model.geom("part4").feature("cyl4").set("pos", new String[]{"0", "0", "Center-L/2"});
    model.geom("part4").run("cyl4");
    model.geom("part4").run("dif2");
    model.geom("part4").run("pard2");
    model.geom("part4").run("ballsel2");
    model.geom("part4").run("del2");
    model.geom("part4").run("pt1");
    model.geom("part4").run("pt1");
    model.component("comp1").geom("geom1").run("pi7");
    model.component("comp1").geom("geom1").create("pi15", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi15").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi15").set("part", "part4");
    model.component("comp1").geom("geom1").run("pi15");
    model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepdom", "pi15_csel7.dom", true);
    model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepdom", "pi15_csel13.dom", true);
    model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeeppnt", "pi15_csel14.pnt", true);
    model.component("comp1").geom("geom1").run("pi15");
    model.component("comp1").geom("geom1").feature().duplicate("pi16", "pi15");
    model.component("comp1").geom("geom1").feature().duplicate("pi17", "pi16");
    model.component("comp1").geom("geom1").feature().duplicate("pi18", "pi17");
    model.component("comp1").geom("geom1").feature().duplicate("pi19", "pi18");
    model.component("comp1").geom("geom1").feature().duplicate("pi20", "pi19");
    model.component("comp1").geom("geom1").feature("pi15").label("ImThera Contact 1");
    model.component("comp1").geom("geom1").feature("pi16").label("ImThera Contact 2");
    model.component("comp1").geom("geom1").feature("pi17").label("ImThera Contact 3");
    model.component("comp1").geom("geom1").feature("pi18").label("ImThera Contact 4");
    model.component("comp1").geom("geom1").feature("pi19").label("ImThera Contact 5");
    model.component("comp1").geom("geom1").feature("pi20").label("ImThera Contact 6");
    model.component("comp1").geom("geom1").feature("pi15")
         .setEntry("inputexpr", "Center", "Center_IT-length_contactcenter_contactcenter");
    model.component("comp1").geom("geom1").feature("pi15")
         .setEntry("inputexpr", "Center", "Center_IT-length_contactcenter_contactcenter_ITC");

    model.param("par6").set("length_contactcenter_contactcenter_ITC", "0.108 [inch]");

    model.component("comp1").geom("geom1").feature("pi15")
         .setEntry("inputexpr", "Rotation_angle", "ang_cuffseam_contactcenter_ITC");

    model.param("par6")
         .set("ang_cuffseam_contactcenter_ITC", "ang_cuffseam_contactcenter_pre*(r_cuff_in_pre_ITI/R_in_ITI)");
    model.param("par6").set("ang_cuffseam_contactcenter_pre_ITC", "53 [deg]");
    model.param("par6")
         .set("ang_cuffseam_contactcenter_ITC", "ang_cuffseam_contactcenter_pre_ITC*(r_cuff_in_pre_ITI/R_in_ITI)");

    model.component("comp1").geom("geom1").run("pi15");
    model.component("comp1").geom("geom1").feature("pi16")
         .setEntry("inputexpr", "Rotation_angle", "ang_cuffseam_contactcenter+ang_contactcenter_contactcenter [deg]");
    model.component("comp1").geom("geom1").feature("pi16")
         .setEntry("inputexpr", "Rotation_angle", "ang_cuffseam_contactcenter_ITC+ang_contactcenter_contactcenter [deg]");
    model.component("comp1").geom("geom1").feature("pi16")
         .setEntry("inputexpr", "Rotation_angle", "ang_cuffseam_contactcenter_ITC+ang_contactcenter_contactcenter_ITC [deg]");

    model.param("par6")
         .set("ang_contactcenter_contactcenter_ITC", "ang_contactcenter_contactcenter_pre_ITC*(r_cuff_in_pre_ITI/R_in_ITI)");
    model.param("par6").set("ang_contactcenter_contactcenter_pre_ITC", "51 [deg]");

    model.component("comp1").geom("geom1").run("pi16");
    model.component("comp1").geom("geom1").feature("pi17")
         .setEntry("inputexpr", "Rotation_angle", "ang_cuffseam_contactcenter_ITC+2*ang_contactcenter_contactcenter_ITC [deg]");
    model.component("comp1").geom("geom1").feature("pi17")
         .setEntry("inputexpr", "Center", "Center_IT+length_contactcenter_contactcenter_ITC");
    model.component("comp1").geom("geom1").run("pi17");
    model.component("comp1").geom("geom1").feature("pi18")
         .setEntry("inputexpr", "Center", "Center_IT-length_contactcenter_contactcenter_ITC");
    model.component("comp1").geom("geom1").feature("pi18")
         .setEntry("inputexpr", "Rotation_angle", "ang_cuffseam_contactcenter_ITC+3*ang_contactcenter_contactcenter_ITC [deg]");
    model.component("comp1").geom("geom1").run("pi18");
    model.component("comp1").geom("geom1").feature("pi19")
         .setEntry("inputexpr", "Rotation_angle", "ang_cuffseam_contactcenter_ITC+4*ang_contactcenter_contactcenter_ITC [deg]");
    model.component("comp1").geom("geom1").run("pi19");
    model.component("comp1").geom("geom1").feature("pi20")
         .setEntry("inputexpr", "Center", "Center_IT+length_contactcenter_contactcenter_ITC");
    model.component("comp1").geom("geom1").feature("pi20")
         .setEntry("inputexpr", "Rotation_angle", "ang_cuffseam_contactcenter_ITC+5*ang_contactcenter_contactcenter_ITC [deg]");
    model.component("comp1").geom("geom1").run("pi20");
    model.component("comp1").geom("geom1").run("fin");
    model.geom("part1").run("endif1");
    model.geom("part1").feature().move("rot1", 14);
    model.geom("part3").inputParam().rename("r_conductor", "R_conductor");
    model.geom("part3").inputParam().rename("sep_conductor", "Sep_conductor");
    model.geom("part3").inputParam().rename("theta_conductor", "Sheta_conductor");
    model.geom("part3").inputParam().rename("Sheta_conductor", "Theta_conductor");
    model.geom("part3").feature("wp1").geom().feature("c1").set("r", "R_conductor");
    model.geom("part3").feature("wp1").geom().feature("c1")
         .set("pos", new String[]{"Center", "R_in-R_conductor-Rep_conductor"});
    model.geom("part3").feature("rev1").set("angle2", "Theta_conductor");
    model.geom("part3").run("");
    model.geom("part3").feature("wp1").geom().feature("c1")
         .set("pos", new String[]{"Center", "R_in-R_conductor-Sep_conductor"});
    model.geom("part3").run("rev1");
    model.component("comp1").geom("geom1").run("pi13");
    model.component("comp1").geom("geom1").run("pi14");
    model.component("comp1").geom("geom1").run("fin");
    model.geom("part4").label("CircleContact_Primitive");
    model.component("comp1").geom("geom1").run("fin");

    model.material().create("mat1", "Common", "");
    model.material("mat1").label("Saline");
    model.material().duplicate("mat2", "mat1");
    model.material("mat2").label("Platinum");
    model.material().duplicate("mat3", "mat2");
    model.material("mat3").label("Silicone");
    model.material().duplicate("mat4", "mat3");
    model.material("mat4").label("Scar");
    model.component("comp1").material().create("matlnk1", "Link");

    model.component("comp1").geom("geom1").feature("pi13").setEntry("selkeepobj", "pi13_csel2", true);
    model.component("comp1").geom("geom1").feature("pi14").setEntry("selkeepobj", "pi14_csel2", true);
    model.component("comp1").geom("geom1").feature("pi13").setEntry("selkeepobj", "pi13_csel2", false);
    model.component("comp1").geom("geom1").feature("pi13").setEntry("selkeepdom", "pi13_csel2.dom", true);
    model.component("comp1").geom("geom1").feature("pi14").setEntry("selkeepdom", "pi14_csel2.dom", true);

    model.component("comp1").material("matlnk1").selection().named("geom1_pi13_csel2_dom");
    model.component("comp1").material("matlnk1").set("link", "mat2");
    model.component("comp1").material().duplicate("matlnk2", "matlnk1");
    model.component("comp1").material("matlnk1").label("Purdue Contact 1 is Platinum");
    model.component("comp1").material("matlnk2").label("Purdue Contact 2 is Platinum");
    model.component("comp1").material("matlnk2").selection().named("geom1_pi14_csel2_dom");
    model.component("comp1").material().create("matlnk3", "Link");

    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepdom", "pi4_csel3.dom", true);

    model.component("comp1").material("matlnk3").label("Purdue Cuff is Silicone");
    model.component("comp1").material("matlnk3").selection().named("geom1_pi4_csel3_dom");
    model.component("comp1").material("matlnk3").set("link", "mat3");

    model.geom("part3").run("rev1");
    model.geom("part3").create("pt1", "Point");
    model.geom("part3").feature("pt1").label("Src");
    model.geom("part3").selection().create("csel3", "CumulativeSelection");
    model.geom("part3").selection("csel3").label("SRC");
    model.geom("part3").feature("pt1").set("contributeto", "csel3");
    model.geom("part3").feature("pt1").setIndex("p", "(Theta_conductor/2)", 0);
    model.geom("part3").feature("pt1").setIndex("p", "(Theta_conductor/2)", 1);
    model.geom("part3").feature("pt1").setIndex("p", "(R_in-R_conductor-Sep_conductor)*cos(Theta_conductor/2)", 0);
    model.geom("part3").feature("pt1").setIndex("p", "(R_in-R_conductor-Sep_conductor)*sin(Theta_conductor/2)", 1);
    model.geom("part3").feature("pt1").setIndex("p", "Center", 2);
    model.geom("part3").run("pt1");
    model.geom("part3").run("pt1");

    model.view("view6").set("transparency", true);

    model.component("comp1").geom("geom1").run("pi13");
    model.component("comp1").geom("geom1").run("pi14");
    model.component("comp1").geom("geom1").run("fin");
    model.component("comp1").geom("geom1").feature("pi13").setEntry("selkeeppnt", "pi13_csel3.pnt", true);
    model.component("comp1").geom("geom1").feature("pi14").setEntry("selkeeppnt", "pi14_csel3.pnt", true);

    model.component("comp1").view("view1").set("renderwireframe", true);

    model.component("comp1").physics("ec").create("pcs1", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs1").selection().named("geom1_pi13_csel3_pnt");
    model.component("comp1").physics("ec").feature("pcs1").set("Qjp", 0.001);
    model.component("comp1").physics("ec").feature("pcs1").label("Purdue Point Current Source 1");
    model.component("comp1").physics("ec").feature().duplicate("pcs2", "pcs1");
    model.component("comp1").physics("ec").feature("pcs2").label("Purdue Point Current Source 2");
    model.component("comp1").physics("ec").feature("pcs2").set("Qjp", -0.001);
    model.component("comp1").physics("ec").feature("pcs2").selection().named("geom1_pi14_csel3_pnt");

    model.component("comp1").geom("geom1").feature("pi9").setEntry("selkeeppnt", "pi9_csel3.pnt", true);

    model.component("comp1").physics("ec").feature().duplicate("pcs3", "pcs2");
    model.component("comp1").physics("ec").feature("pcs3").label("Enteromedics Point Current Source 1");
    model.component("comp1").physics("ec").feature("pcs3").set("Qjp", 0.001);
    model.component("comp1").physics("ec").feature("pcs3").selection().named("geom1_pi9_csel3_pnt");
    model.component("comp1").physics("ec").feature().move("pcs3", 3);
    model.component("comp1").physics("ec").feature().duplicate("pcs4", "pcs3");
    model.component("comp1").physics("ec").feature().move("pcs4", 4);
    model.component("comp1").physics("ec").feature("pcs4").label("Madison Point Current Source 1");

    model.component("comp1").geom("geom1").feature("pi10").setEntry("selkeeppnt", "pi10_csel3.pnt", true);

    model.component("comp1").physics("ec").feature("pcs4").selection().named("geom1_pi10_csel3_pnt");
    model.component("comp1").physics("ec").feature().duplicate("pcs5", "pcs4");
    model.component("comp1").physics("ec").feature().move("pcs5", 5);
    model.component("comp1").physics("ec").feature("pcs5").label("CorTec300 Point Current Source 1");

    model.component("comp1").geom("geom1").feature("pi11").setEntry("selkeeppnt", "pi11_csel3.pnt", true);
    model.component("comp1").geom("geom1").feature("pi12").setEntry("selkeeppnt", "pi12_csel3.pnt", true);

    model.component("comp1").physics("ec").feature("pcs5").selection().named("geom1_pi11_csel3_pnt");
    model.component("comp1").physics("ec").feature().duplicate("pcs6", "pcs5");
    model.component("comp1").physics("ec").feature("pcs6").label("CorTec300 Point Current Source 2");
    model.component("comp1").physics("ec").feature("pcs6").selection().named("geom1_pi12_csel3_pnt");
    model.component("comp1").physics("ec").feature("pcs6").set("Qjp", -0.001);
    model.component("comp1").physics("ec").feature().move("pcs6", 6);
    model.component("comp1").physics("ec").feature().duplicate("pcs7", "pcs2");
    model.component("comp1").physics("ec").feature("pcs7").label("ImThera Point Current Source 1");
    model.component("comp1").physics("ec").feature("pcs7").selection().named("geom1_pi15_csel14_pnt");
    model.component("comp1").physics("ec").feature("pcs7").set("Qjp", 0.001);
    model.component("comp1").physics("ec").feature().duplicate("pcs8", "pcs7");
    model.component("comp1").physics("ec").feature().duplicate("pcs9", "pcs8");
    model.component("comp1").physics("ec").feature().duplicate("pcs10", "pcs9");
    model.component("comp1").physics("ec").feature().duplicate("pcs11", "pcs10");
    model.component("comp1").physics("ec").feature("pcs8").label("ImThera Point Current Source 2");
    model.component("comp1").physics("ec").feature("pcs9").label("ImThera Point Current Source 3");
    model.component("comp1").physics("ec").feature("pcs10").label("ImThera Point Current Source 4");
    model.component("comp1").physics("ec").feature("pcs11").label("ImThera Point Current Source 5");
    model.component("comp1").physics("ec").feature().duplicate("pcs12", "pcs11");
    model.component("comp1").physics("ec").feature("pcs12").label("ImThera Point Current Source 6");
    model.component("comp1").physics("ec").feature("pcs8").selection().named("geom1_pi16_csel14_pnt");
    model.component("comp1").physics("ec").feature("pcs9").selection().named("geom1_pi17_csel14_pnt");
    model.component("comp1").physics("ec").feature("pcs10").selection().named("geom1_pi18_csel14_pnt");
    model.component("comp1").physics("ec").feature("pcs11").selection().named("geom1_pi19_csel14_pnt");
    model.component("comp1").physics("ec").feature("pcs12").selection().named("geom1_pi20_csel14_pnt");

    model.component("comp1").material().create("matlnk4", "Link");
    model.component("comp1").material().move("matlnk4", 0);
    model.component("comp1").material("matlnk4").label("Enteromedics Cuff is Silicone");

    model.component("comp1").geom("geom1").feature("pi8").setEntry("selkeepdom", "pi8_csel3.dom", true);

    model.component("comp1").material("matlnk4").selection().named("geom1_pi8_csel3_dom");
    model.component("comp1").material("matlnk4").set("link", "mat3");
    model.component("comp1").material().duplicate("matlnk5", "matlnk4");
    model.component("comp1").material().move("matlnk5", 1);
    model.component("comp1").material("matlnk5").label("Enteromedics Contact is Platinum");

    model.component("comp1").geom("geom1").feature("pi9").setEntry("selkeepdom", "pi9_csel4.dom", true);

    model.component("comp1").material("matlnk5").selection().named("geom1_pi9_csel4_dom");
    model.component("comp1").material("matlnk5").set("link", "mat2");
    model.component("comp1").material().create("matlnk6", "Link");
    model.component("comp1").material().move("matlnk6", 2);
    model.component("comp1").material("matlnk6").label("Madison Cuff is Silicone");

    model.component("comp1").geom("geom1").feature("pi2").setEntry("selkeepdom", "pi2_csel3.dom", true);

    return model;
  }

  public static Model run4(Model model) {
    model.component("comp1").geom("geom1").feature("pi10").setEntry("selkeepdom", "pi10_csel4.dom", true);

    model.component("comp1").material("matlnk6").selection().named("geom1_pi2_csel3_dom");
    model.component("comp1").material("matlnk6").set("link", "mat3");
    model.component("comp1").material().duplicate("matlnk7", "matlnk6");
    model.component("comp1").material().move("matlnk7", 3);
    model.component("comp1").material("matlnk7").label("Madison Contact is Platinum");
    model.component("comp1").material("matlnk7").selection().named("geom1_pi10_csel4_dom");
    model.component("comp1").material("matlnk7").set("link", "mat2");
    model.component("comp1").material().create("matlnk8", "Link");
    model.component("comp1").material().move("matlnk8", 4);
    model.component("comp1").material("matlnk8").label("CorTec300 Cuff is Silicone");

    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel3.dom", true);
    model.component("comp1").geom("geom1").feature("pi11").setEntry("selkeepdom", "pi11_csel4.dom", true);
    model.component("comp1").geom("geom1").feature("pi12").setEntry("selkeepdom", "pi12_csel4.dom", true);

    model.component("comp1").material("matlnk8").selection().named("geom1_pi3_csel3_dom");
    model.component("comp1").material("matlnk8").set("link", "mat3");
    model.component("comp1").material().duplicate("matlnk9", "matlnk8");
    model.component("comp1").material().move("matlnk9", 5);
    model.component("comp1").material("matlnk9").label("CorTec300 Contact 1 is Platinum");
    model.component("comp1").material("matlnk9").selection().named("geom1_pi11_csel4_dom");
    model.component("comp1").material("matlnk9").set("link", "mat2");
    model.component("comp1").material().duplicate("matlnk10", "matlnk9");
    model.component("comp1").material().move("matlnk10", 6);
    model.component("comp1").material("matlnk10").label("CorTec300 Contact 2 is Platinum");
    model.component("comp1").material("matlnk10").selection().named("geom1_pi12_csel4_dom");
    model.component("comp1").material().create("matlnk11", "Link");
    model.component("comp1").material("matlnk11").label("ImThera Inner Cuff is Silicone");

    model.component("comp1").geom("geom1").feature("pi6").setEntry("selkeepdom", "pi6_csel3.dom", true);
    model.component("comp1").geom("geom1").feature("pi7").setEntry("selkeepdom", "pi7_csel3.dom", true);

    model.component("comp1").material("matlnk11").selection().named("geom1_pi6_csel3_dom");
    model.component("comp1").material("matlnk11").set("link", "mat3");
    model.component("comp1").material().duplicate("matlnk12", "matlnk11");
    model.component("comp1").material("matlnk12").label("ImThera Furl is Silicone");
    model.component("comp1").material("matlnk12").selection().named("geom1_pi7_csel3_dom");
    model.component("comp1").material().duplicate("matlnk13", "matlnk12");
    model.component("comp1").material("matlnk13").label("ImThera Contact 1 is Platinum");
    model.component("comp1").material("matlnk13").selection().named("geom1_pi15_csel13_dom");
    model.component("comp1").material("matlnk13").set("link", "mat2");
    model.component("comp1").material().duplicate("matlnk14", "matlnk13");
    model.component("comp1").material().duplicate("matlnk15", "matlnk14");
    model.component("comp1").material().duplicate("matlnk16", "matlnk15");
    model.component("comp1").material().duplicate("matlnk17", "matlnk16");
    model.component("comp1").material().duplicate("matlnk18", "matlnk17");
    model.component("comp1").material("matlnk15").label("ImThera Contact 1 is Platinum 2");
    model.component("comp1").material("matlnk16").label("ImThera Contact 1 is Platinum 3");
    model.component("comp1").material("matlnk17").label("ImThera Contact 1 is Platinum 4");
    model.component("comp1").material("matlnk18").label("ImThera Contact 1 is Platinum 5");
    model.component("comp1").material().duplicate("matlnk19", "matlnk18");
    model.component("comp1").material("matlnk19").label("ImThera Contact 1 is Platinum 6");
    model.component("comp1").material("matlnk15").selection().named("geom1_pi16_csel13_dom");
    model.component("comp1").material("matlnk16").selection().named("geom1_pi17_csel13_dom");
    model.component("comp1").material("matlnk17").selection().named("geom1_pi17_csel13_dom");
    model.component("comp1").material("matlnk17").selection().named("geom1_pi18_csel13_dom");
    model.component("comp1").material("matlnk18").selection().named("geom1_pi19_csel13_dom");
    model.component("comp1").material("matlnk19").selection().named("geom1_pi20_csel13_dom");
    model.component("comp1").material().duplicate("matlnk20", "matlnk19");
    model.component("comp1").material("matlnk20").label("ImThera Recess1 is Saline");
    model.component("comp1").material("matlnk20").set("link", "mat1");
    model.component("comp1").material("matlnk20").label("ImThera Recess 1 is Saline");
    model.component("comp1").material("matlnk20").selection().named("geom1_pi15_csel7_dom");
    model.component("comp1").material().duplicate("matlnk21", "matlnk20");
    model.component("comp1").material().duplicate("matlnk22", "matlnk21");
    model.component("comp1").material().duplicate("matlnk23", "matlnk22");
    model.component("comp1").material().duplicate("matlnk24", "matlnk23");
    model.component("comp1").material().duplicate("matlnk25", "matlnk24");
    model.component("comp1").material("matlnk21").label("ImThera Recess 2 is Saline");
    model.component("comp1").material("matlnk21").selection().named("geom1_pi16_csel7_dom");
    model.component("comp1").material("matlnk22").label("ImThera Recess 3 is Saline");
    model.component("comp1").material("matlnk22").selection().named("geom1_pi17_csel7_dom");
    model.component("comp1").material("matlnk23").label("ImThera Recess 4 is Saline");
    model.component("comp1").material("matlnk23").selection().named("geom1_pi18_csel7_dom");
    model.component("comp1").material("matlnk24").selection().named("geom1_pi19_csel7_dom");
    model.component("comp1").material("matlnk24").label("ImThera Recess 5 is Saline");
    model.component("comp1").material("matlnk25").label("ImThera Recess 6 is Saline");
    model.component("comp1").material("matlnk25").selection().named("geom1_pi20_csel7_dom");
    model.component("comp1").material().move("matlnk3", 7);
    model.component("comp1").material().remove("matlnk13");

    return model;
  }

  public static void main(String[] args) {
    Model model = run();
    model = run2(model);
    model = run3(model);
    run4(model);
  }

}

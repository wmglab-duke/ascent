/*
 * parts_test.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Nov 2 2019, 17:32 by COMSOL 5.4.0.388. */
public class parts_test {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model.modelPath("D:\\Documents\\access\\src");

    model.component().create("comp1", true);

    model.component("comp1").geom().create("geom1", 3);

    model.component("comp1").physics().create("ec", "ConductiveMedia", "geom1");

    model.component("comp1").mesh().create("mesh1");

    model.param().group().create("par1");
    model.param("par1").label("Enteromedics");
    model.param("par1").set("N_holes_EM", "0", "number of holes");
    model.param("par1").set("Theta_EM", "Theta_contact_EM+((2*(360*arc_ext_EM)/(2*pi*R_in_EM)) [deg])", "test");
    model.param("par1").set("Center_EM", "Length_EM/2", "");
    model.param("par1").set("R_in_EM", "max(r_nerve_EM+thk_medium_gap_internal_EM,r_cuff_in_pre_EM)", "");
    model.param("par1").set("R_out_EM", "R_in_EM+thk_cuff_EM", "");
    model.param("par1").set("L_EM", "3*L_elec_EM", "");
    model.param("par1").set("Rot_def_EM", "-(360*arc_ext_EM)/(2*pi*R_in_EM)", "");
    model.param("par1").set("D_hole_EM", "NaN", "");
    model.param("par1").set("Buffer_hole_EM", "NaN", "");
    model.param("par1").set("L_holecenter_cuffseam_EM", "NaN", "");
    model.param("par1").set("Pitch_holecenter_holecenter_EM", "NaN", "");
    model.param("par1").set("r_nerve_EM", "1.3 [mm]", "");
    model.param("par1").set("thk_medium_gap_internal_EM", "0 [mm]", "");
    model.param("par1").set("r_cuff_in_pre_EM", "1.651 [mm]", "");
    model.param("par1").set("thk_cuff_EM", "1 [mm]", "");
    model.param("par1").set("L_elec_EM", "1.397 [mm]", "");
    model.param("par1").set("arc_ext_EM", "0.5 [mm]", "");
    model.param("par1").set("theta_contact_pre_EM", "256.4287 [deg]", "");
    model.param("par1").set("Theta_contact_EM", "theta_contact_pre_EM*(r_cuff_in_pre_EM/R_in_EM)", "");
    model.param("par1").set("z_nerve_EM", "20 [mm]", "");
    model.param("par1").set("Thk_elec_EM", "0.1 [mm]", "");
    model.param("par1").set("Recess_EM", "0 [mm]", "");
    model.param("par1").set("Thk_fill_EM", "100 [um]", "");
    model.param("par1").set("Radius_EM", "10 [mm]", "");
    model.param("par1").set("Length_EM", "100 [mm]", "");

    model.geom().create("part1", "Part", 3);
    model.geom("part1").label("Medium_Primitive");
    model.geom("part1").lengthUnit("\u00b5m");
    model.geom("part1").inputParam().set("Radius", "10 [mm]");
    model.geom("part1").inputParam().set("Length", "100 [mm]");
    model.geom("part1").selection().create("csel1", "CumulativeSelection");
    model.geom("part1").selection("csel1").label("MEDIUM");
    model.geom("part1").create("cyl1", "Cylinder");
    model.geom("part1").feature("cyl1").label("Medium");
    model.geom("part1").feature("cyl1").set("r", "Radius");
    model.geom("part1").feature("cyl1").set("h", "Length");
    model.geom("part1").feature("cyl1").set("contributeto", "csel1");
    model.geom().create("part2", "Part", 3);
    model.geom("part2").label("CuffFill_Primitive");
    model.geom("part2").lengthUnit("\u00b5m");
    model.geom("part2").inputParam().set("Radius", "0.5 [mm]");
    model.geom("part2").inputParam().set("Thk", "100 [um]");
    model.geom("part2").inputParam().set("L", "2.5 [mm]");
    model.geom("part2").inputParam().set("z_center", "0");
    model.geom("part2").selection().create("csel1", "CumulativeSelection");
    model.geom("part2").selection("csel1").label("CUFF FILL FINAL");
    model.geom("part2").create("cyl1", "Cylinder");
    model.geom("part2").feature("cyl1").label("Cuff Fill");
    model.geom("part2").feature("cyl1").set("contributeto", "csel1");
    model.geom("part2").feature("cyl1").set("pos", new String[]{"0", "0", "z_center-(L/2)"});
    model.geom("part2").feature("cyl1").set("r", "Radius");
    model.geom("part2").feature("cyl1").set("h", "L");
    model.geom("part2").run();
    model.geom().create("part3", "Part", 3);
    model.geom("part3").label("TubeCuff_Primitive");
    model.geom("part3").lengthUnit("\u00b5m");
    model.geom("part3").inputParam().set("N_holes", "1");
    model.geom("part3").inputParam().set("Theta", "340 [deg]");
    model.geom("part3").inputParam().set("Center", "10 [mm]");
    model.geom("part3").inputParam().set("R_in", "1 [mm]");
    model.geom("part3").inputParam().set("R_out", "2 [mm]");
    model.geom("part3").inputParam().set("L", "5 [mm]");
    model.geom("part3").inputParam().set("Rot_def", "0 [deg]");
    model.geom("part3").inputParam().set("D_hole", "0.3 [mm]");
    model.geom("part3").inputParam().set("Buffer_hole", "0.1 [mm]");
    model.geom("part3").inputParam().set("L_holecenter_cuffseam", "0.3 [mm]");
    model.geom("part3").inputParam().set("Pitch_holecenter_holecenter", "0 [mm]");
    model.geom("part3").selection().create("csel1", "CumulativeSelection");
    model.geom("part3").selection("csel1").label("INNER CUFF SURFACE");
    model.geom("part3").selection().create("csel2", "CumulativeSelection");
    model.geom("part3").selection("csel2").label("OUTER CUFF SURFACE");
    model.geom("part3").selection().create("csel3", "CumulativeSelection");
    model.geom("part3").selection("csel3").label("CUFF FINAL");
    model.geom("part3").selection().create("csel4", "CumulativeSelection");
    model.geom("part3").selection("csel4").label("CUFF wGAP PRE HOLES");
    model.geom("part3").selection().create("csel5", "CumulativeSelection");
    model.geom("part3").selection("csel5").label("CUFF PRE GAP");
    model.geom("part3").selection().create("csel6", "CumulativeSelection");
    model.geom("part3").selection("csel6").label("CUFF PRE GAP PRE HOLES");
    model.geom("part3").selection().create("csel7", "CumulativeSelection");
    model.geom("part3").selection("csel7").label("CUFF GAP CROSS SECTION");
    model.geom("part3").selection().create("csel8", "CumulativeSelection");
    model.geom("part3").selection("csel8").label("CUFF GAP");
    model.geom("part3").selection().create("csel9", "CumulativeSelection");
    model.geom("part3").selection("csel9").label("CUFF PRE HOLES");
    model.geom("part3").selection().create("csel10", "CumulativeSelection");
    model.geom("part3").selection("csel10").label("HOLE 1");
    model.geom("part3").selection().create("csel11", "CumulativeSelection");
    model.geom("part3").selection("csel11").label("HOLE 2");
    model.geom("part3").selection().create("csel12", "CumulativeSelection");
    model.geom("part3").selection("csel12").label("HOLES");
    model.geom("part3").create("cyl1", "Cylinder");
    model.geom("part3").feature("cyl1").label("Make Inner Cuff Surface");
    model.geom("part3").feature("cyl1").set("contributeto", "csel1");
    model.geom("part3").feature("cyl1").set("pos", new String[]{"0", "0", "Center-(L/2)"});
    model.geom("part3").feature("cyl1").set("r", "R_in");
    model.geom("part3").feature("cyl1").set("h", "L");
    model.geom("part3").create("cyl2", "Cylinder");
    model.geom("part3").feature("cyl2").label("Make Outer Cuff Surface");
    model.geom("part3").feature("cyl2").set("contributeto", "csel2");
    model.geom("part3").feature("cyl2").set("pos", new String[]{"0", "0", "Center-(L/2)"});
    model.geom("part3").feature("cyl2").set("r", "R_out");
    model.geom("part3").feature("cyl2").set("h", "L");
    model.geom("part3").create("if1", "If");
    model.geom("part3").feature("if1").label("If (No Gap AND No Holes)");
    model.geom("part3").feature("if1").set("condition", "(Theta==360) && (N_holes==0)");
    model.geom("part3").create("dif1", "Difference");
    model.geom("part3").feature("dif1").label("Remove Domain Within Inner Cuff Surface");
    model.geom("part3").feature("dif1").set("contributeto", "csel3");
    model.geom("part3").feature("dif1").selection("input").named("csel2");
    model.geom("part3").feature("dif1").selection("input2").named("csel1");
    model.geom("part3").create("elseif1", "ElseIf");
    model.geom("part3").feature("elseif1").label("If (Gap AND No Holes)");
    model.geom("part3").feature("elseif1").set("condition", "(Theta<360) && (N_holes==0)");
    model.geom("part3").create("dif2", "Difference");
    model.geom("part3").feature("dif2").label("Remove Domain Within Inner Cuff Surface 1");
    model.geom("part3").feature("dif2").set("contributeto", "csel5");
    model.geom("part3").feature("dif2").selection("input").named("csel2");
    model.geom("part3").feature("dif2").selection("input2").named("csel1");
    model.geom("part3").create("wp1", "WorkPlane");
    model.geom("part3").feature("wp1").label("Make Cuff Gap Cross Section");
    model.geom("part3").feature("wp1").set("contributeto", "csel7");
    model.geom("part3").feature("wp1").set("quickplane", "xz");
    model.geom("part3").feature("wp1").set("unite", true);
    model.geom("part3").feature("wp1").geom().create("r1", "Rectangle");
    model.geom("part3").feature("wp1").geom().feature("r1").label("Cuff Gap Cross Section");
    model.geom("part3").feature("wp1").geom().feature("r1")
         .set("pos", new String[]{"R_in+((R_out-R_in)/2)", "Center"});
    model.geom("part3").feature("wp1").geom().feature("r1").set("base", "center");
    model.geom("part3").feature("wp1").geom().feature("r1").set("size", new String[]{"R_out-R_in", "L"});
    model.geom("part3").create("rev1", "Revolve");
    model.geom("part3").feature("rev1").label("Make Cuff Gap");
    model.geom("part3").feature("rev1").set("contributeto", "csel8");
    model.geom("part3").feature("rev1").set("angle1", "Theta");
    model.geom("part3").feature("rev1").selection("input").set("wp1");
    model.geom("part3").create("dif3", "Difference");
    model.geom("part3").feature("dif3").label("Remove Cuff Gap");
    model.geom("part3").feature("dif3").set("contributeto", "csel3");
    model.geom("part3").feature("dif3").selection("input").named("csel5");
    model.geom("part3").feature("dif3").selection("input2").named("csel8");
    model.geom("part3").create("rot1", "Rotate");
    model.geom("part3").feature("rot1").label("Rotate to Default Conformation 1");
    model.geom("part3").feature("rot1").set("rot", "Rot_def");
    model.geom("part3").feature("rot1").selection("input").named("csel3");
    model.geom("part3").create("elseif2", "ElseIf");
    model.geom("part3").feature("elseif2").label("If (No Gap AND Holes)");
    model.geom("part3").feature("elseif2").set("condition", "(Theta==360) && (N_holes>0)");
    model.geom("part3").create("dif4", "Difference");
    model.geom("part3").feature("dif4").label("Remove Domain Within Inner Cuff Surface 2");
    model.geom("part3").feature("dif4").set("contributeto", "csel9");
    model.geom("part3").feature("dif4").selection("input").named("csel2");
    model.geom("part3").feature("dif4").selection("input2").named("csel1");
    model.geom("part3").create("econ1", "ECone");
    model.geom("part3").feature("econ1").label("Make Hole Shape");
    model.geom("part3").feature("econ1").set("contributeto", "csel12");
    model.geom("part3").feature("econ1")
         .set("pos", new String[]{"R_in-Buffer_hole/2", "0", "Center+Pitch_holecenter_holecenter/2"});
    model.geom("part3").feature("econ1").set("axis", new int[]{1, 0, 0});
    model.geom("part3").feature("econ1").set("semiaxes", new String[]{"D_hole/2", "D_hole/2"});
    model.geom("part3").feature("econ1").set("h", "(R_out-R_in)+Buffer_hole");
    model.geom("part3").feature("econ1").set("rat", "R_out/R_in");
    model.geom("part3").create("rot2", "Rotate");
    model.geom("part3").feature("rot2").label("Position Hole in Cuff");
    model.geom("part3").feature("rot2").set("rot", "(360*L_holecenter_cuffseam)/(pi*2*R_in)");
    model.geom("part3").feature("rot2").selection("input").named("csel12");
    model.geom("part3").create("dif5", "Difference");
    model.geom("part3").feature("dif5").label("Make Inner Cuff Hole");
    model.geom("part3").feature("dif5").set("contributeto", "csel3");
    model.geom("part3").feature("dif5").selection("input").named("csel9");
    model.geom("part3").feature("dif5").selection("input2").named("csel12");
    model.geom("part3").create("elseif3", "ElseIf");
    model.geom("part3").feature("elseif3").label("If (Gap AND Holes)");
    model.geom("part3").feature("elseif3").set("condition", "(Theta<360) && (N_holes>0)");
    model.geom("part3").create("dif6", "Difference");
    model.geom("part3").feature("dif6").label("Remove Domain Within Inner Cuff Surface 3");
    model.geom("part3").feature("dif6").set("contributeto", "csel6");
    model.geom("part3").feature("dif6").selection("input").named("csel2");
    model.geom("part3").feature("dif6").selection("input2").named("csel1");
    model.geom("part3").create("wp2", "WorkPlane");
    model.geom("part3").feature("wp2").label("Make Cuff Gap Cross Section 1");
    model.geom("part3").feature("wp2").set("contributeto", "csel7");
    model.geom("part3").feature("wp2").set("quickplane", "xz");
    model.geom("part3").feature("wp2").set("unite", true);
    model.geom("part3").feature("wp2").geom().create("r1", "Rectangle");
    model.geom("part3").feature("wp2").geom().feature("r1").label("Cuff Gap Cross Section");
    model.geom("part3").feature("wp2").geom().feature("r1")
         .set("pos", new String[]{"R_in+((R_out-R_in)/2)", "Center"});
    model.geom("part3").feature("wp2").geom().feature("r1").set("base", "center");
    model.geom("part3").feature("wp2").geom().feature("r1").set("size", new String[]{"R_out-R_in", "L"});
    model.geom("part3").create("rev2", "Revolve");
    model.geom("part3").feature("rev2").label("Make Cuff Gap 1");
    model.geom("part3").feature("rev2").set("contributeto", "csel8");
    model.geom("part3").feature("rev2").set("angle1", "Theta");
    model.geom("part3").feature("rev2").selection("input").named("csel7");
    model.geom("part3").create("dif7", "Difference");
    model.geom("part3").feature("dif7").label("Remove Cuff Gap 1");
    model.geom("part3").feature("dif7").set("contributeto", "csel4");
    model.geom("part3").feature("dif7").selection("input").named("csel6");
    model.geom("part3").feature("dif7").selection("input2").named("csel8");
    model.geom("part3").create("econ2", "ECone");
    model.geom("part3").feature("econ2").label("Make Hole Shape 1");
    model.geom("part3").feature("econ2").set("contributeto", "csel12");
    model.geom("part3").feature("econ2")
         .set("pos", new String[]{"R_in-Buffer_hole/2", "0", "Center+Pitch_holecenter_holecenter/2"});
    model.geom("part3").feature("econ2").set("axis", new int[]{1, 0, 0});
    model.geom("part3").feature("econ2").set("semiaxes", new String[]{"D_hole/2", "D_hole/2"});
    model.geom("part3").feature("econ2").set("h", "(R_out-R_in)+Buffer_hole");
    model.geom("part3").feature("econ2").set("rat", "R_out/R_in");
    model.geom("part3").create("rot3", "Rotate");
    model.geom("part3").feature("rot3").label("Position Hole in Cuff 1");
    model.geom("part3").feature("rot3").set("rot", "(360*L_holecenter_cuffseam)/(pi*2*R_in)");
    model.geom("part3").feature("rot3").selection("input").named("csel12");
    model.geom("part3").create("dif8", "Difference");
    model.geom("part3").feature("dif8").label("Make Inner Cuff Hole 1");
    model.geom("part3").feature("dif8").set("contributeto", "csel3");
    model.geom("part3").feature("dif8").selection("input").named("csel4");
    model.geom("part3").feature("dif8").selection("input2").named("csel12");
    model.geom("part3").create("rot4", "Rotate");
    model.geom("part3").feature("rot4").label("Rotate to Default Conformation");
    model.geom("part3").feature("rot4").set("rot", "Rot_def");
    model.geom("part3").feature("rot4").selection("input").named("csel3");
    model.geom("part3").create("endif1", "EndIf");
    model.geom("part3").feature("endif1").label("End");
    model.geom("part3").run();
    model.geom().create("part4", "Part", 3);
    model.geom("part4").label("RibbonContact_Primitive");
    model.geom("part4").lengthUnit("\u00b5m");
    model.geom("part4").inputParam().set("Thk_elec", "0.1 [mm]");
    model.geom("part4").inputParam().set("L_elec", "3 [mm]");
    model.geom("part4").inputParam().set("R_in", "1 [mm]");
    model.geom("part4").inputParam().set("Recess", "0.1 [mm]");
    model.geom("part4").inputParam().set("Center", "10 [mm]");
    model.geom("part4").inputParam().set("Theta_contact", "100 [deg]");
    model.geom("part4").inputParam().set("Rot_def", "0 [deg]");
    model.geom("part4").selection().create("csel1", "CumulativeSelection");
    model.geom("part4").selection("csel1").label("CONTACT CROSS SECTION");
    model.geom("part4").selection().create("csel2", "CumulativeSelection");
    model.geom("part4").selection("csel2").label("RECESS CROSS SECTION");
    model.geom("part4").selection().create("csel3", "CumulativeSelection");
    model.geom("part4").selection("csel3").label("SRC");
    model.geom("part4").selection().create("csel4", "CumulativeSelection");
    model.geom("part4").selection("csel4").label("CONTACT FINAL");
    model.geom("part4").selection().create("csel5", "CumulativeSelection");
    model.geom("part4").selection("csel5").label("RECESS FINAL");
    model.geom("part4").create("wp1", "WorkPlane");
    model.geom("part4").feature("wp1").label("Contact Cross Section");
    model.geom("part4").feature("wp1").set("contributeto", "csel1");
    model.geom("part4").feature("wp1").set("quickplane", "xz");
    model.geom("part4").feature("wp1").set("unite", true);
    model.geom("part4").feature("wp1").geom().create("r1", "Rectangle");
    model.geom("part4").feature("wp1").geom().feature("r1").label("Contact Cross Section");
    model.geom("part4").feature("wp1").geom().feature("r1")
         .set("pos", new String[]{"R_in+Recess+Thk_elec/2", "Center"});
    model.geom("part4").feature("wp1").geom().feature("r1").set("base", "center");
    model.geom("part4").feature("wp1").geom().feature("r1").set("size", new String[]{"Thk_elec", "L_elec"});
    model.geom("part4").create("rev1", "Revolve");
    model.geom("part4").feature("rev1").label("Make Contact");
    model.geom("part4").feature("rev1").set("contributeto", "csel4");
    model.geom("part4").feature("rev1").set("angle1", "Rot_def");
    model.geom("part4").feature("rev1").set("angle2", "Rot_def+Theta_contact");
    model.geom("part4").feature("rev1").selection("input").named("csel1");
    model.geom("part4").create("if1", "If");
    model.geom("part4").feature("if1").set("condition", "Recess>0");
    model.geom("part4").feature("if1").label("IF RECESS");
    model.geom("part4").create("wp2", "WorkPlane");
    model.geom("part4").feature("wp2").label("Recess Cross Section 1");
    model.geom("part4").feature("wp2").set("contributeto", "csel2");
    model.geom("part4").feature("wp2").set("quickplane", "xz");
    model.geom("part4").feature("wp2").set("unite", true);
    model.geom("part4").feature("wp2").geom().selection().create("csel6", "CumulativeSelection");
    model.geom("part4").feature("wp2").geom().selection("csel6").label("Cumulative Selection 1");
    model.geom("part4").feature("wp2").geom().selection().create("csel7", "CumulativeSelection");
    model.geom("part4").feature("wp2").geom().selection("csel7").label("wp RECESS CROSS SECTION");
    model.geom("part4").feature("wp2").geom().create("r1", "Rectangle");
    model.geom("part4").feature("wp2").geom().feature("r1").label("Recess Cross Section");
    model.geom("part4").feature("wp2").geom().feature("r1").set("contributeto", "csel7");
    model.geom("part4").feature("wp2").geom().feature("r1").set("pos", new String[]{"R_in+Recess/2", "Center"});
    model.geom("part4").feature("wp2").geom().feature("r1").set("base", "center");
    model.geom("part4").feature("wp2").geom().feature("r1").set("size", new String[]{"Recess", "L_elec"});
    model.geom("part4").create("rev2", "Revolve");
    model.geom("part4").feature("rev2").label("Make Recess");
    model.geom("part4").feature("rev2").set("contributeto", "csel5");
    model.geom("part4").feature("rev2").set("angle1", "Rot_def");
    model.geom("part4").feature("rev2").set("angle2", "Rot_def+Theta_contact");
    model.geom("part4").feature("rev2").selection("input").named("csel2");
    model.geom("part4").create("endif1", "EndIf");
    model.geom("part4").feature("endif1").label("EndIf");
    model.geom("part4").create("pt1", "Point");
    model.geom("part4").feature("pt1").label("Src");
    model.geom("part4").feature("pt1").set("contributeto", "csel3");
    model.geom("part4").feature("pt1")
         .set("p", new String[]{"(R_in+Recess+Thk_elec/2)*cos(Rot_def+Theta_contact/2)", "(R_in+Recess+Thk_elec/2)*sin(Rot_def+Theta_contact/2)", "Center"});
    model.geom("part4").run();

    model.material().create("mat1", "Common", "");
    model.material("mat1").label("fat");
    model.material("mat1").propertyGroup("def").set("electricconductivity", new String[]{"1/30"});
    model.material().create("mat2", "Common", "");
    model.material("mat2").label("encapsulation");
    model.material("mat2").propertyGroup("def").set("electricconductivity", new String[]{"1/6.3"});
    model.material().create("mat3", "Common", "");
    model.material("mat3").label("silicone");
    model.material("mat3").propertyGroup("def").set("electricconductivity", new String[]{"10^(-12)"});
    model.material().create("mat4", "Common", "");
    model.material("mat4").label("platinum");
    model.material("mat4").propertyGroup("def").set("electricconductivity", new String[]{"9.43*10^6"});
    model.material().create("mat5", "Common", "");
    model.material("mat5").label("saline");
    model.material("mat5").propertyGroup("def").set("electricconductivity", new String[]{"1.76"});

    model.component("comp1").geom("geom1").lengthUnit("\u00b5m");
    model.component("comp1").geom("geom1").create("pi1", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi1").label("Enteromedics Medium");
    model.component("comp1").geom("geom1").feature("pi1").set("part", "part1");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("inputexpr", "Radius", "Radius_EM");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("inputexpr", "Length", "Length_EM");
    model.component("comp1").geom("geom1").feature("pi1").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi1").setEntry("selkeepdom", "pi1_csel1.dom", "on");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("selkeepbnd", "pi1_csel1.bnd", "on");

    model.component("comp1").physics("ec").create("gnd1", "Ground", 2);
    model.component("comp1").physics("ec").feature("gnd1").label("Ground");
    model.component("comp1").physics("ec").feature("gnd1").selection().named("geom1_pi1_csel1_bnd");

    model.component("comp1").material().create("matlnk1", "Link");
    model.component("comp1").material("matlnk1").label("Enteromedics Medium/MEDIUM/fat");
    model.component("comp1").material("matlnk1").set("link", "mat1");
    model.component("comp1").material("matlnk1").selection().named("geom1_pi1_csel1_dom");

    model.component("comp1").geom("geom1").lengthUnit("\u00b5m");
    model.component("comp1").geom("geom1").create("pi2", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi2").label("Enteromedics Cuff Fill");
    model.component("comp1").geom("geom1").feature("pi2").set("part", "part2");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "Radius", "R_out_EM+Thk_fill_EM");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "Thk", "Thk_fill_EM");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "L", "L_EM+2*Thk_fill_EM");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "z_center", "Center_EM");
    model.component("comp1").geom("geom1").feature("pi2").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi2").setEntry("selkeepdom", "pi2_csel1.dom", "on");

    model.component("comp1").material().create("matlnk2", "Link");
    model.component("comp1").material("matlnk2").label("Enteromedics Cuff Fill/CUFF FILL FINAL/encapsulation");
    model.component("comp1").material("matlnk2").set("link", "mat2");
    model.component("comp1").material("matlnk2").selection().named("geom1_pi2_csel1_dom");

    model.component("comp1").geom("geom1").lengthUnit("\u00b5m");
    model.component("comp1").geom("geom1").create("pi3", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi3").label("Enteromedics Cuff");
    model.component("comp1").geom("geom1").feature("pi3").set("part", "part3");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "N_holes", "N_holes_EM");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "Theta", "Theta_EM");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "Center", "Center_EM");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "R_in", "R_in_EM");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "R_out", "R_out_EM");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "L", "L_EM");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "Rot_def", "Rot_def_EM");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "D_hole", "D_hole_EM");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "Buffer_hole", "Buffer_hole_EM");
    model.component("comp1").geom("geom1").feature("pi3")
         .setEntry("inputexpr", "L_holecenter_cuffseam", "L_holecenter_cuffseam_EM");
    model.component("comp1").geom("geom1").feature("pi3")
         .setEntry("inputexpr", "Pitch_holecenter_holecenter", "Pitch_holecenter_holecenter_EM");
    model.component("comp1").geom("geom1").feature("pi3").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel3.dom", "on");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel2.dom", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel4.dom", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel5.dom", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel6.dom", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel7.dom", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel8.dom", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel9.dom", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel10.dom", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel11.dom", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel12.dom", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel2.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel3.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel4.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel5.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel6.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel7.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel8.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel9.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel10.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel11.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel12.pnt", "off");

    model.component("comp1").material().create("matlnk3", "Link");
    model.component("comp1").material("matlnk3").label("Enteromedics Cuff/CUFF FINAL/silicone");
    model.component("comp1").material("matlnk3").set("link", "mat3");
    model.component("comp1").material("matlnk3").selection().named("geom1_pi3_csel3_dom");

    model.component("comp1").geom("geom1").lengthUnit("\u00b5m");
    model.component("comp1").geom("geom1").create("pi4", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi4").label("Enteromedics Contact 1");
    model.component("comp1").geom("geom1").feature("pi4").set("part", "part4");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "Thk_elec", "Thk_elec_EM");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "L_elec", "L_elec_EM");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "R_in", "R_in_EM");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "Recess", "Recess_EM");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "Center", "Center_EM");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "Theta_contact", "Theta_contact_EM");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "Rot_def", "0 [deg]");
    model.component("comp1").geom("geom1").feature("pi4").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepdom", "pi4_csel2.dom", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepdom", "pi4_csel3.dom", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepdom", "pi4_csel4.dom", "on");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepdom", "pi4_csel5.dom", "on");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeeppnt", "pi4_csel2.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeeppnt", "pi4_csel3.pnt", "on");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeeppnt", "pi4_csel4.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeeppnt", "pi4_csel5.pnt", "off");

    model.component("comp1").physics("ec").create("pcs1", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs1").selection().named("geom1_pi4_csel3_pnt");
    model.component("comp1").physics("ec").feature("pcs1").set("Qjp", 0.001);
    model.component("comp1").physics("ec").feature("pcs1").label("Enteromedics Contact 1 Current Source");

    model.component("comp1").material().create("matlnk4", "Link");
    model.component("comp1").material("matlnk4").label("Enteromedics Contact 1/CONTACT FINAL/platinum");
    model.component("comp1").material("matlnk4").set("link", "mat4");
    model.component("comp1").material("matlnk4").selection().named("geom1_pi4_csel4_dom");
    model.component("comp1").material().create("matlnk5", "Link");
    model.component("comp1").material("matlnk5").label("Enteromedics Contact 1/RECESS FINAL/saline");
    model.component("comp1").material("matlnk5").set("link", "mat5");
    model.component("comp1").material("matlnk5").selection().named("geom1_pi4_csel5_dom");

    model.param()
         .set("fascicle0", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/0/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel1", "CumulativeSelection");

    return model;
  }

  public static Model run2(Model model) {
    model.component("comp1").geom("geom1").selection("csel1").label("fascicle0_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel2", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel2").label("fascicle0_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp1", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp1").label("fascicle0_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp1").set("contributeto", "csel1");
    model.component("comp1").geom("geom1").feature("wp1").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp1").geom().selection().create("csel3", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp1").geom().selection("csel3").label("fascicle0_IC");
    model.component("comp1").geom("geom1").feature("wp1").geom().create("ic1", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp1").geom().feature("ic1")
         .label("fascicle0_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp1").geom().feature("ic1").set("contributeto", "csel3");
    model.component("comp1").geom("geom1").feature("wp1").geom().feature("ic1").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp1").geom().feature("ic1")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/0/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp1").geom().feature("ic1").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp1").geom().create("csol1", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp1").geom().feature("csol1")
         .label("fascicle0_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp1").geom().feature("csol1").selection("input").named("csel3");
    model.component("comp1").geom("geom1").create("ext1", "Extrude");
    model.component("comp1").geom("geom1").feature("ext1").label("fascicle0_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext1").set("contributeto", "csel2");
    model.component("comp1").geom("geom1").feature("ext1").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext1").selection("input").named("csel1");

    model.param()
         .set("fascicle1", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/1/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel4", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel4").label("fascicle1_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel5", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel5").label("fascicle1_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp2", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp2").label("fascicle1_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp2").set("contributeto", "csel4");
    model.component("comp1").geom("geom1").feature("wp2").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp2").geom().selection().create("csel6", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp2").geom().selection("csel6").label("fascicle1_IC");
    model.component("comp1").geom("geom1").feature("wp2").geom().create("ic2", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic2")
         .label("fascicle1_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic2").set("contributeto", "csel6");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic2").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic2")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/1/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic2").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp2").geom().create("csol2", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("csol2")
         .label("fascicle1_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("csol2").selection("input").named("csel6");
    model.component("comp1").geom("geom1").create("ext2", "Extrude");
    model.component("comp1").geom("geom1").feature("ext2").label("fascicle1_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext2").set("contributeto", "csel5");
    model.component("comp1").geom("geom1").feature("ext2").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext2").selection("input").named("csel4");

    model.param()
         .set("fascicle2", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/10/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel7", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel7").label("fascicle2_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel8", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel8").label("fascicle2_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp3", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp3").label("fascicle2_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp3").set("contributeto", "csel7");
    model.component("comp1").geom("geom1").feature("wp3").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp3").geom().selection().create("csel9", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp3").geom().selection("csel9").label("fascicle2_IC");
    model.component("comp1").geom("geom1").feature("wp3").geom().create("ic3", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("ic3")
         .label("fascicle2_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("ic3").set("contributeto", "csel9");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("ic3").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("ic3")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/10/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("ic3").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp3").geom().create("csol3", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("csol3")
         .label("fascicle2_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("csol3").selection("input").named("csel9");
    model.component("comp1").geom("geom1").create("ext3", "Extrude");
    model.component("comp1").geom("geom1").feature("ext3").label("fascicle2_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext3").set("contributeto", "csel8");
    model.component("comp1").geom("geom1").feature("ext3").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext3").selection("input").named("csel7");

    model.param()
         .set("fascicle3", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/11/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel10", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel10").label("fascicle3_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel11", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel11").label("fascicle3_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp4", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp4").label("fascicle3_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp4").set("contributeto", "csel10");
    model.component("comp1").geom("geom1").feature("wp4").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp4").geom().selection().create("csel12", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp4").geom().selection("csel12").label("fascicle3_IC");
    model.component("comp1").geom("geom1").feature("wp4").geom().create("ic4", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp4").geom().feature("ic4")
         .label("fascicle3_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp4").geom().feature("ic4").set("contributeto", "csel12");
    model.component("comp1").geom("geom1").feature("wp4").geom().feature("ic4").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp4").geom().feature("ic4")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/11/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp4").geom().feature("ic4").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp4").geom().create("csol4", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp4").geom().feature("csol4")
         .label("fascicle3_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp4").geom().feature("csol4").selection("input").named("csel12");
    model.component("comp1").geom("geom1").create("ext4", "Extrude");
    model.component("comp1").geom("geom1").feature("ext4").label("fascicle3_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext4").set("contributeto", "csel11");
    model.component("comp1").geom("geom1").feature("ext4").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext4").selection("input").named("csel10");

    model.param()
         .set("fascicle4", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/12/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel13", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel13").label("fascicle4_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel14", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel14").label("fascicle4_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp5", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp5").label("fascicle4_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp5").set("contributeto", "csel13");
    model.component("comp1").geom("geom1").feature("wp5").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp5").geom().selection().create("csel15", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp5").geom().selection("csel15").label("fascicle4_IC");
    model.component("comp1").geom("geom1").feature("wp5").geom().create("ic5", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp5").geom().feature("ic5")
         .label("fascicle4_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp5").geom().feature("ic5").set("contributeto", "csel15");
    model.component("comp1").geom("geom1").feature("wp5").geom().feature("ic5").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp5").geom().feature("ic5")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/12/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp5").geom().feature("ic5").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp5").geom().create("csol5", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp5").geom().feature("csol5")
         .label("fascicle4_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp5").geom().feature("csol5").selection("input").named("csel15");
    model.component("comp1").geom("geom1").create("ext5", "Extrude");
    model.component("comp1").geom("geom1").feature("ext5").label("fascicle4_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext5").set("contributeto", "csel14");
    model.component("comp1").geom("geom1").feature("ext5").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext5").selection("input").named("csel13");

    model.param()
         .set("fascicle5", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/13/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel16", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel16").label("fascicle5_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel17", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel17").label("fascicle5_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp6", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp6").label("fascicle5_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp6").set("contributeto", "csel16");
    model.component("comp1").geom("geom1").feature("wp6").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp6").geom().selection().create("csel18", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp6").geom().selection("csel18").label("fascicle5_IC");
    model.component("comp1").geom("geom1").feature("wp6").geom().create("ic6", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp6").geom().feature("ic6")
         .label("fascicle5_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp6").geom().feature("ic6").set("contributeto", "csel18");
    model.component("comp1").geom("geom1").feature("wp6").geom().feature("ic6").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp6").geom().feature("ic6")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/13/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp6").geom().feature("ic6").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp6").geom().create("csol6", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp6").geom().feature("csol6")
         .label("fascicle5_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp6").geom().feature("csol6").selection("input").named("csel18");
    model.component("comp1").geom("geom1").create("ext6", "Extrude");
    model.component("comp1").geom("geom1").feature("ext6").label("fascicle5_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext6").set("contributeto", "csel17");
    model.component("comp1").geom("geom1").feature("ext6").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext6").selection("input").named("csel16");

    model.param()
         .set("fascicle6", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/14/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel19", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel19").label("fascicle6_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel20", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel20").label("fascicle6_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp7", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp7").label("fascicle6_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp7").set("contributeto", "csel19");
    model.component("comp1").geom("geom1").feature("wp7").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp7").geom().selection().create("csel21", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp7").geom().selection("csel21").label("fascicle6_IC");
    model.component("comp1").geom("geom1").feature("wp7").geom().create("ic7", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp7").geom().feature("ic7")
         .label("fascicle6_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp7").geom().feature("ic7").set("contributeto", "csel21");
    model.component("comp1").geom("geom1").feature("wp7").geom().feature("ic7").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp7").geom().feature("ic7")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/14/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp7").geom().feature("ic7").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp7").geom().create("csol7", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp7").geom().feature("csol7")
         .label("fascicle6_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp7").geom().feature("csol7").selection("input").named("csel21");
    model.component("comp1").geom("geom1").create("ext7", "Extrude");
    model.component("comp1").geom("geom1").feature("ext7").label("fascicle6_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext7").set("contributeto", "csel20");
    model.component("comp1").geom("geom1").feature("ext7").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext7").selection("input").named("csel19");

    model.param()
         .set("fascicle7", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/15/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel22", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel22").label("fascicle7_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel23", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel23").label("fascicle7_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp8", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp8").label("fascicle7_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp8").set("contributeto", "csel22");
    model.component("comp1").geom("geom1").feature("wp8").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp8").geom().selection().create("csel24", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp8").geom().selection("csel24").label("fascicle7_IC");
    model.component("comp1").geom("geom1").feature("wp8").geom().create("ic8", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp8").geom().feature("ic8")
         .label("fascicle7_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp8").geom().feature("ic8").set("contributeto", "csel24");
    model.component("comp1").geom("geom1").feature("wp8").geom().feature("ic8").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp8").geom().feature("ic8")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/15/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp8").geom().feature("ic8").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp8").geom().create("csol8", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp8").geom().feature("csol8")
         .label("fascicle7_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp8").geom().feature("csol8").selection("input").named("csel24");
    model.component("comp1").geom("geom1").create("ext8", "Extrude");
    model.component("comp1").geom("geom1").feature("ext8").label("fascicle7_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext8").set("contributeto", "csel23");
    model.component("comp1").geom("geom1").feature("ext8").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext8").selection("input").named("csel22");

    model.param()
         .set("fascicle8", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/16/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel25", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel25").label("fascicle8_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel26", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel26").label("fascicle8_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp9", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp9").label("fascicle8_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp9").set("contributeto", "csel25");
    model.component("comp1").geom("geom1").feature("wp9").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp9").geom().selection().create("csel27", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp9").geom().selection("csel27").label("fascicle8_IC");
    model.component("comp1").geom("geom1").feature("wp9").geom().create("ic9", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp9").geom().feature("ic9")
         .label("fascicle8_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp9").geom().feature("ic9").set("contributeto", "csel27");
    model.component("comp1").geom("geom1").feature("wp9").geom().feature("ic9").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp9").geom().feature("ic9")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/16/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp9").geom().feature("ic9").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp9").geom().create("csol9", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp9").geom().feature("csol9")
         .label("fascicle8_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp9").geom().feature("csol9").selection("input").named("csel27");
    model.component("comp1").geom("geom1").create("ext9", "Extrude");
    model.component("comp1").geom("geom1").feature("ext9").label("fascicle8_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext9").set("contributeto", "csel26");
    model.component("comp1").geom("geom1").feature("ext9").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext9").selection("input").named("csel25");

    model.param()
         .set("fascicle9", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/17/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel28", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel28").label("fascicle9_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel29", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel29").label("fascicle9_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp10", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp10").label("fascicle9_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp10").set("contributeto", "csel28");
    model.component("comp1").geom("geom1").feature("wp10").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp10").geom().selection()
         .create("csel30", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp10").geom().selection("csel30").label("fascicle9_IC");
    model.component("comp1").geom("geom1").feature("wp10").geom().create("ic10", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic10")
         .label("fascicle9_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic10").set("contributeto", "csel30");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic10").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic10")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/17/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic10").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp10").geom().create("csol10", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("csol10")
         .label("fascicle9_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("csol10").selection("input")
         .named("csel30");
    model.component("comp1").geom("geom1").create("ext10", "Extrude");
    model.component("comp1").geom("geom1").feature("ext10").label("fascicle9_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext10").set("contributeto", "csel29");
    model.component("comp1").geom("geom1").feature("ext10").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext10").selection("input").named("csel28");

    model.param()
         .set("fascicle10", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/18/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel31", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel31").label("fascicle10_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel32", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel32").label("fascicle10_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp11", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp11").label("fascicle10_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp11").set("contributeto", "csel31");
    model.component("comp1").geom("geom1").feature("wp11").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp11").geom().selection()
         .create("csel33", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp11").geom().selection("csel33").label("fascicle10_IC");
    model.component("comp1").geom("geom1").feature("wp11").geom().create("ic11", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("ic11")
         .label("fascicle10_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("ic11").set("contributeto", "csel33");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("ic11").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("ic11")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/18/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("ic11").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp11").geom().create("csol11", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("csol11")
         .label("fascicle10_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("csol11").selection("input")
         .named("csel33");
    model.component("comp1").geom("geom1").create("ext11", "Extrude");
    model.component("comp1").geom("geom1").feature("ext11").label("fascicle10_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext11").set("contributeto", "csel32");
    model.component("comp1").geom("geom1").feature("ext11").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext11").selection("input").named("csel31");

    model.param()
         .set("fascicle11", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/19/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel34", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel34").label("fascicle11_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel35", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel35").label("fascicle11_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp12", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp12").label("fascicle11_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp12").set("contributeto", "csel34");
    model.component("comp1").geom("geom1").feature("wp12").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp12").geom().selection()
         .create("csel36", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp12").geom().selection("csel36").label("fascicle11_IC");
    model.component("comp1").geom("geom1").feature("wp12").geom().create("ic12", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp12").geom().feature("ic12")
         .label("fascicle11_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp12").geom().feature("ic12").set("contributeto", "csel36");
    model.component("comp1").geom("geom1").feature("wp12").geom().feature("ic12").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp12").geom().feature("ic12")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/19/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp12").geom().feature("ic12").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp12").geom().create("csol12", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp12").geom().feature("csol12")
         .label("fascicle11_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp12").geom().feature("csol12").selection("input")
         .named("csel36");
    model.component("comp1").geom("geom1").create("ext12", "Extrude");
    model.component("comp1").geom("geom1").feature("ext12").label("fascicle11_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext12").set("contributeto", "csel35");
    model.component("comp1").geom("geom1").feature("ext12").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext12").selection("input").named("csel34");

    model.param()
         .set("fascicle12", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/2/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel37", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel37").label("fascicle12_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel38", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel38").label("fascicle12_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp13", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp13").label("fascicle12_Fascicle Cross Section");

    return model;
  }

  public static Model run3(Model model) {
    model.component("comp1").geom("geom1").feature("wp13").set("contributeto", "csel37");
    model.component("comp1").geom("geom1").feature("wp13").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp13").geom().selection()
         .create("csel39", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp13").geom().selection("csel39").label("fascicle12_IC");
    model.component("comp1").geom("geom1").feature("wp13").geom().create("ic13", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp13").geom().feature("ic13")
         .label("fascicle12_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp13").geom().feature("ic13").set("contributeto", "csel39");
    model.component("comp1").geom("geom1").feature("wp13").geom().feature("ic13").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp13").geom().feature("ic13")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/2/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp13").geom().feature("ic13").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp13").geom().create("csol13", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp13").geom().feature("csol13")
         .label("fascicle12_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp13").geom().feature("csol13").selection("input")
         .named("csel39");
    model.component("comp1").geom("geom1").create("ext13", "Extrude");
    model.component("comp1").geom("geom1").feature("ext13").label("fascicle12_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext13").set("contributeto", "csel38");
    model.component("comp1").geom("geom1").feature("ext13").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext13").selection("input").named("csel37");

    model.param()
         .set("fascicle13", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/20/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel40", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel40").label("fascicle13_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel41", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel41").label("fascicle13_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp14", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp14").label("fascicle13_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp14").set("contributeto", "csel40");
    model.component("comp1").geom("geom1").feature("wp14").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp14").geom().selection()
         .create("csel42", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp14").geom().selection("csel42").label("fascicle13_IC");
    model.component("comp1").geom("geom1").feature("wp14").geom().create("ic14", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic14")
         .label("fascicle13_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic14").set("contributeto", "csel42");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic14").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic14")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/20/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic14").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp14").geom().create("csol14", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("csol14")
         .label("fascicle13_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("csol14").selection("input")
         .named("csel42");
    model.component("comp1").geom("geom1").create("ext14", "Extrude");
    model.component("comp1").geom("geom1").feature("ext14").label("fascicle13_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext14").set("contributeto", "csel41");
    model.component("comp1").geom("geom1").feature("ext14").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext14").selection("input").named("csel40");

    model.param()
         .set("fascicle14", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/21/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel43", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel43").label("fascicle14_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel44", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel44").label("fascicle14_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp15", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp15").label("fascicle14_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp15").set("contributeto", "csel43");
    model.component("comp1").geom("geom1").feature("wp15").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp15").geom().selection()
         .create("csel45", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp15").geom().selection("csel45").label("fascicle14_IC");
    model.component("comp1").geom("geom1").feature("wp15").geom().create("ic15", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("ic15")
         .label("fascicle14_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("ic15").set("contributeto", "csel45");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("ic15").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("ic15")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/21/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("ic15").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp15").geom().create("csol15", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("csol15")
         .label("fascicle14_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("csol15").selection("input")
         .named("csel45");
    model.component("comp1").geom("geom1").create("ext15", "Extrude");
    model.component("comp1").geom("geom1").feature("ext15").label("fascicle14_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext15").set("contributeto", "csel44");
    model.component("comp1").geom("geom1").feature("ext15").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext15").selection("input").named("csel43");

    model.param()
         .set("fascicle15", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/22/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel46", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel46").label("fascicle15_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel47", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel47").label("fascicle15_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp16", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp16").label("fascicle15_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp16").set("contributeto", "csel46");
    model.component("comp1").geom("geom1").feature("wp16").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp16").geom().selection()
         .create("csel48", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp16").geom().selection("csel48").label("fascicle15_IC");
    model.component("comp1").geom("geom1").feature("wp16").geom().create("ic16", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp16").geom().feature("ic16")
         .label("fascicle15_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp16").geom().feature("ic16").set("contributeto", "csel48");
    model.component("comp1").geom("geom1").feature("wp16").geom().feature("ic16").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp16").geom().feature("ic16")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/22/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp16").geom().feature("ic16").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp16").geom().create("csol16", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp16").geom().feature("csol16")
         .label("fascicle15_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp16").geom().feature("csol16").selection("input")
         .named("csel48");
    model.component("comp1").geom("geom1").create("ext16", "Extrude");
    model.component("comp1").geom("geom1").feature("ext16").label("fascicle15_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext16").set("contributeto", "csel47");
    model.component("comp1").geom("geom1").feature("ext16").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext16").selection("input").named("csel46");

    model.param()
         .set("fascicle16", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/23/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel49", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel49").label("fascicle16_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel50", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel50").label("fascicle16_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp17", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp17").label("fascicle16_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp17").set("contributeto", "csel49");
    model.component("comp1").geom("geom1").feature("wp17").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp17").geom().selection()
         .create("csel51", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp17").geom().selection("csel51").label("fascicle16_IC");
    model.component("comp1").geom("geom1").feature("wp17").geom().create("ic17", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp17").geom().feature("ic17")
         .label("fascicle16_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp17").geom().feature("ic17").set("contributeto", "csel51");
    model.component("comp1").geom("geom1").feature("wp17").geom().feature("ic17").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp17").geom().feature("ic17")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/23/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp17").geom().feature("ic17").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp17").geom().create("csol17", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp17").geom().feature("csol17")
         .label("fascicle16_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp17").geom().feature("csol17").selection("input")
         .named("csel51");
    model.component("comp1").geom("geom1").create("ext17", "Extrude");
    model.component("comp1").geom("geom1").feature("ext17").label("fascicle16_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext17").set("contributeto", "csel50");
    model.component("comp1").geom("geom1").feature("ext17").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext17").selection("input").named("csel49");

    model.param()
         .set("fascicle17", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/24/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel52", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel52").label("fascicle17_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel53", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel53").label("fascicle17_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp18", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp18").label("fascicle17_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp18").set("contributeto", "csel52");
    model.component("comp1").geom("geom1").feature("wp18").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp18").geom().selection()
         .create("csel54", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp18").geom().selection("csel54").label("fascicle17_IC");
    model.component("comp1").geom("geom1").feature("wp18").geom().create("ic18", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp18").geom().feature("ic18")
         .label("fascicle17_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp18").geom().feature("ic18").set("contributeto", "csel54");
    model.component("comp1").geom("geom1").feature("wp18").geom().feature("ic18").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp18").geom().feature("ic18")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/24/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp18").geom().feature("ic18").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp18").geom().create("csol18", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp18").geom().feature("csol18")
         .label("fascicle17_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp18").geom().feature("csol18").selection("input")
         .named("csel54");
    model.component("comp1").geom("geom1").create("ext18", "Extrude");
    model.component("comp1").geom("geom1").feature("ext18").label("fascicle17_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext18").set("contributeto", "csel53");
    model.component("comp1").geom("geom1").feature("ext18").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext18").selection("input").named("csel52");

    model.param()
         .set("fascicle18", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/25/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel55", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel55").label("fascicle18_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel56", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel56").label("fascicle18_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp19", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp19").label("fascicle18_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp19").set("contributeto", "csel55");
    model.component("comp1").geom("geom1").feature("wp19").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp19").geom().selection()
         .create("csel57", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp19").geom().selection("csel57").label("fascicle18_IC");
    model.component("comp1").geom("geom1").feature("wp19").geom().create("ic19", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp19").geom().feature("ic19")
         .label("fascicle18_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp19").geom().feature("ic19").set("contributeto", "csel57");
    model.component("comp1").geom("geom1").feature("wp19").geom().feature("ic19").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp19").geom().feature("ic19")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/25/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp19").geom().feature("ic19").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp19").geom().create("csol19", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp19").geom().feature("csol19")
         .label("fascicle18_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp19").geom().feature("csol19").selection("input")
         .named("csel57");
    model.component("comp1").geom("geom1").create("ext19", "Extrude");
    model.component("comp1").geom("geom1").feature("ext19").label("fascicle18_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext19").set("contributeto", "csel56");
    model.component("comp1").geom("geom1").feature("ext19").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext19").selection("input").named("csel55");

    model.param()
         .set("fascicle19", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/26/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel58", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel58").label("fascicle19_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel59", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel59").label("fascicle19_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp20", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp20").label("fascicle19_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp20").set("contributeto", "csel58");
    model.component("comp1").geom("geom1").feature("wp20").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp20").geom().selection()
         .create("csel60", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp20").geom().selection("csel60").label("fascicle19_IC");
    model.component("comp1").geom("geom1").feature("wp20").geom().create("ic20", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp20").geom().feature("ic20")
         .label("fascicle19_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp20").geom().feature("ic20").set("contributeto", "csel60");
    model.component("comp1").geom("geom1").feature("wp20").geom().feature("ic20").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp20").geom().feature("ic20")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/26/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp20").geom().feature("ic20").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp20").geom().create("csol20", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp20").geom().feature("csol20")
         .label("fascicle19_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp20").geom().feature("csol20").selection("input")
         .named("csel60");
    model.component("comp1").geom("geom1").create("ext20", "Extrude");
    model.component("comp1").geom("geom1").feature("ext20").label("fascicle19_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext20").set("contributeto", "csel59");
    model.component("comp1").geom("geom1").feature("ext20").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext20").selection("input").named("csel58");

    model.param()
         .set("fascicle20", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/27/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel61", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel61").label("fascicle20_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel62", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel62").label("fascicle20_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp21", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp21").label("fascicle20_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp21").set("contributeto", "csel61");
    model.component("comp1").geom("geom1").feature("wp21").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp21").geom().selection()
         .create("csel63", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp21").geom().selection("csel63").label("fascicle20_IC");
    model.component("comp1").geom("geom1").feature("wp21").geom().create("ic21", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp21").geom().feature("ic21")
         .label("fascicle20_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp21").geom().feature("ic21").set("contributeto", "csel63");
    model.component("comp1").geom("geom1").feature("wp21").geom().feature("ic21").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp21").geom().feature("ic21")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/27/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp21").geom().feature("ic21").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp21").geom().create("csol21", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp21").geom().feature("csol21")
         .label("fascicle20_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp21").geom().feature("csol21").selection("input")
         .named("csel63");
    model.component("comp1").geom("geom1").create("ext21", "Extrude");
    model.component("comp1").geom("geom1").feature("ext21").label("fascicle20_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext21").set("contributeto", "csel62");
    model.component("comp1").geom("geom1").feature("ext21").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext21").selection("input").named("csel61");

    model.param()
         .set("fascicle21", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/28/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel64", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel64").label("fascicle21_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel65", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel65").label("fascicle21_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp22", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp22").label("fascicle21_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp22").set("contributeto", "csel64");
    model.component("comp1").geom("geom1").feature("wp22").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp22").geom().selection()
         .create("csel66", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp22").geom().selection("csel66").label("fascicle21_IC");
    model.component("comp1").geom("geom1").feature("wp22").geom().create("ic22", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp22").geom().feature("ic22")
         .label("fascicle21_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp22").geom().feature("ic22").set("contributeto", "csel66");
    model.component("comp1").geom("geom1").feature("wp22").geom().feature("ic22").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp22").geom().feature("ic22")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/28/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp22").geom().feature("ic22").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp22").geom().create("csol22", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp22").geom().feature("csol22")
         .label("fascicle21_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp22").geom().feature("csol22").selection("input")
         .named("csel66");
    model.component("comp1").geom("geom1").create("ext22", "Extrude");
    model.component("comp1").geom("geom1").feature("ext22").label("fascicle21_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext22").set("contributeto", "csel65");
    model.component("comp1").geom("geom1").feature("ext22").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext22").selection("input").named("csel64");

    model.param()
         .set("fascicle22", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/29/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel67", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel67").label("fascicle22_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel68", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel68").label("fascicle22_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp23", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp23").label("fascicle22_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp23").set("contributeto", "csel67");
    model.component("comp1").geom("geom1").feature("wp23").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp23").geom().selection()
         .create("csel69", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp23").geom().selection("csel69").label("fascicle22_IC");
    model.component("comp1").geom("geom1").feature("wp23").geom().create("ic23", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp23").geom().feature("ic23")
         .label("fascicle22_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp23").geom().feature("ic23").set("contributeto", "csel69");
    model.component("comp1").geom("geom1").feature("wp23").geom().feature("ic23").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp23").geom().feature("ic23")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/29/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp23").geom().feature("ic23").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp23").geom().create("csol23", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp23").geom().feature("csol23")
         .label("fascicle22_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp23").geom().feature("csol23").selection("input")
         .named("csel69");
    model.component("comp1").geom("geom1").create("ext23", "Extrude");
    model.component("comp1").geom("geom1").feature("ext23").label("fascicle22_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext23").set("contributeto", "csel68");
    model.component("comp1").geom("geom1").feature("ext23").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext23").selection("input").named("csel67");

    model.param()
         .set("fascicle23", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/3/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel70", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel70").label("fascicle23_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel71", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel71").label("fascicle23_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp24", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp24").label("fascicle23_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp24").set("contributeto", "csel70");
    model.component("comp1").geom("geom1").feature("wp24").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp24").geom().selection()
         .create("csel72", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp24").geom().selection("csel72").label("fascicle23_IC");
    model.component("comp1").geom("geom1").feature("wp24").geom().create("ic24", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp24").geom().feature("ic24")
         .label("fascicle23_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp24").geom().feature("ic24").set("contributeto", "csel72");
    model.component("comp1").geom("geom1").feature("wp24").geom().feature("ic24").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp24").geom().feature("ic24")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/3/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp24").geom().feature("ic24").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp24").geom().create("csol24", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp24").geom().feature("csol24")
         .label("fascicle23_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp24").geom().feature("csol24").selection("input")
         .named("csel72");
    model.component("comp1").geom("geom1").create("ext24", "Extrude");
    model.component("comp1").geom("geom1").feature("ext24").label("fascicle23_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext24").set("contributeto", "csel71");
    model.component("comp1").geom("geom1").feature("ext24").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext24").selection("input").named("csel70");

    model.param()
         .set("fascicle24", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/30/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel73", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel73").label("fascicle24_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel74", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel74").label("fascicle24_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp25", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp25").label("fascicle24_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp25").set("contributeto", "csel73");

    return model;
  }

  public static Model run4(Model model) {
    model.component("comp1").geom("geom1").feature("wp25").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp25").geom().selection()
         .create("csel75", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp25").geom().selection("csel75").label("fascicle24_IC");
    model.component("comp1").geom("geom1").feature("wp25").geom().create("ic25", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp25").geom().feature("ic25")
         .label("fascicle24_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp25").geom().feature("ic25").set("contributeto", "csel75");
    model.component("comp1").geom("geom1").feature("wp25").geom().feature("ic25").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp25").geom().feature("ic25")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/30/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp25").geom().feature("ic25").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp25").geom().create("csol25", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp25").geom().feature("csol25")
         .label("fascicle24_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp25").geom().feature("csol25").selection("input")
         .named("csel75");
    model.component("comp1").geom("geom1").create("ext25", "Extrude");
    model.component("comp1").geom("geom1").feature("ext25").label("fascicle24_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext25").set("contributeto", "csel74");
    model.component("comp1").geom("geom1").feature("ext25").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext25").selection("input").named("csel73");

    model.param()
         .set("fascicle25", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/31/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel76", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel76").label("fascicle25_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel77", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel77").label("fascicle25_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp26", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp26").label("fascicle25_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp26").set("contributeto", "csel76");
    model.component("comp1").geom("geom1").feature("wp26").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp26").geom().selection()
         .create("csel78", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp26").geom().selection("csel78").label("fascicle25_IC");
    model.component("comp1").geom("geom1").feature("wp26").geom().create("ic26", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp26").geom().feature("ic26")
         .label("fascicle25_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp26").geom().feature("ic26").set("contributeto", "csel78");
    model.component("comp1").geom("geom1").feature("wp26").geom().feature("ic26").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp26").geom().feature("ic26")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/31/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp26").geom().feature("ic26").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp26").geom().create("csol26", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp26").geom().feature("csol26")
         .label("fascicle25_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp26").geom().feature("csol26").selection("input")
         .named("csel78");
    model.component("comp1").geom("geom1").create("ext26", "Extrude");
    model.component("comp1").geom("geom1").feature("ext26").label("fascicle25_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext26").set("contributeto", "csel77");
    model.component("comp1").geom("geom1").feature("ext26").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext26").selection("input").named("csel76");

    model.param()
         .set("fascicle26", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/32/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel79", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel79").label("fascicle26_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel80", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel80").label("fascicle26_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp27", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp27").label("fascicle26_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp27").set("contributeto", "csel79");
    model.component("comp1").geom("geom1").feature("wp27").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp27").geom().selection()
         .create("csel81", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp27").geom().selection("csel81").label("fascicle26_IC");
    model.component("comp1").geom("geom1").feature("wp27").geom().create("ic27", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp27").geom().feature("ic27")
         .label("fascicle26_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp27").geom().feature("ic27").set("contributeto", "csel81");
    model.component("comp1").geom("geom1").feature("wp27").geom().feature("ic27").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp27").geom().feature("ic27")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/32/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp27").geom().feature("ic27").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp27").geom().create("csol27", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp27").geom().feature("csol27")
         .label("fascicle26_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp27").geom().feature("csol27").selection("input")
         .named("csel81");
    model.component("comp1").geom("geom1").create("ext27", "Extrude");
    model.component("comp1").geom("geom1").feature("ext27").label("fascicle26_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext27").set("contributeto", "csel80");
    model.component("comp1").geom("geom1").feature("ext27").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext27").selection("input").named("csel79");

    model.param()
         .set("fascicle27", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/33/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel82", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel82").label("fascicle27_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel83", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel83").label("fascicle27_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp28", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp28").label("fascicle27_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp28").set("contributeto", "csel82");
    model.component("comp1").geom("geom1").feature("wp28").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp28").geom().selection()
         .create("csel84", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp28").geom().selection("csel84").label("fascicle27_IC");
    model.component("comp1").geom("geom1").feature("wp28").geom().create("ic28", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp28").geom().feature("ic28")
         .label("fascicle27_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp28").geom().feature("ic28").set("contributeto", "csel84");
    model.component("comp1").geom("geom1").feature("wp28").geom().feature("ic28").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp28").geom().feature("ic28")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/33/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp28").geom().feature("ic28").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp28").geom().create("csol28", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp28").geom().feature("csol28")
         .label("fascicle27_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp28").geom().feature("csol28").selection("input")
         .named("csel84");
    model.component("comp1").geom("geom1").create("ext28", "Extrude");
    model.component("comp1").geom("geom1").feature("ext28").label("fascicle27_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext28").set("contributeto", "csel83");
    model.component("comp1").geom("geom1").feature("ext28").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext28").selection("input").named("csel82");

    model.param()
         .set("fascicle28", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/34/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel85", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel85").label("fascicle28_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel86", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel86").label("fascicle28_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp29", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp29").label("fascicle28_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp29").set("contributeto", "csel85");
    model.component("comp1").geom("geom1").feature("wp29").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp29").geom().selection()
         .create("csel87", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp29").geom().selection("csel87").label("fascicle28_IC");
    model.component("comp1").geom("geom1").feature("wp29").geom().create("ic29", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp29").geom().feature("ic29")
         .label("fascicle28_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp29").geom().feature("ic29").set("contributeto", "csel87");
    model.component("comp1").geom("geom1").feature("wp29").geom().feature("ic29").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp29").geom().feature("ic29")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/34/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp29").geom().feature("ic29").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp29").geom().create("csol29", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp29").geom().feature("csol29")
         .label("fascicle28_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp29").geom().feature("csol29").selection("input")
         .named("csel87");
    model.component("comp1").geom("geom1").create("ext29", "Extrude");
    model.component("comp1").geom("geom1").feature("ext29").label("fascicle28_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext29").set("contributeto", "csel86");
    model.component("comp1").geom("geom1").feature("ext29").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext29").selection("input").named("csel85");

    model.param()
         .set("fascicle29", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/35/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel88", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel88").label("fascicle29_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel89", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel89").label("fascicle29_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp30", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp30").label("fascicle29_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp30").set("contributeto", "csel88");
    model.component("comp1").geom("geom1").feature("wp30").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp30").geom().selection()
         .create("csel90", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp30").geom().selection("csel90").label("fascicle29_IC");
    model.component("comp1").geom("geom1").feature("wp30").geom().create("ic30", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp30").geom().feature("ic30")
         .label("fascicle29_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp30").geom().feature("ic30").set("contributeto", "csel90");
    model.component("comp1").geom("geom1").feature("wp30").geom().feature("ic30").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp30").geom().feature("ic30")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/35/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp30").geom().feature("ic30").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp30").geom().create("csol30", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp30").geom().feature("csol30")
         .label("fascicle29_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp30").geom().feature("csol30").selection("input")
         .named("csel90");
    model.component("comp1").geom("geom1").create("ext30", "Extrude");
    model.component("comp1").geom("geom1").feature("ext30").label("fascicle29_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext30").set("contributeto", "csel89");
    model.component("comp1").geom("geom1").feature("ext30").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext30").selection("input").named("csel88");

    model.param()
         .set("fascicle30", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/36/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel91", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel91").label("fascicle30_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel92", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel92").label("fascicle30_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp31", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp31").label("fascicle30_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp31").set("contributeto", "csel91");
    model.component("comp1").geom("geom1").feature("wp31").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp31").geom().selection()
         .create("csel93", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp31").geom().selection("csel93").label("fascicle30_IC");
    model.component("comp1").geom("geom1").feature("wp31").geom().create("ic31", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp31").geom().feature("ic31")
         .label("fascicle30_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp31").geom().feature("ic31").set("contributeto", "csel93");
    model.component("comp1").geom("geom1").feature("wp31").geom().feature("ic31").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp31").geom().feature("ic31")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/36/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp31").geom().feature("ic31").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp31").geom().create("csol31", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp31").geom().feature("csol31")
         .label("fascicle30_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp31").geom().feature("csol31").selection("input")
         .named("csel93");
    model.component("comp1").geom("geom1").create("ext31", "Extrude");
    model.component("comp1").geom("geom1").feature("ext31").label("fascicle30_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext31").set("contributeto", "csel92");
    model.component("comp1").geom("geom1").feature("ext31").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext31").selection("input").named("csel91");

    model.param()
         .set("fascicle31", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/37/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel94", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel94").label("fascicle31_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel95", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel95").label("fascicle31_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp32", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp32").label("fascicle31_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp32").set("contributeto", "csel94");
    model.component("comp1").geom("geom1").feature("wp32").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp32").geom().selection()
         .create("csel96", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp32").geom().selection("csel96").label("fascicle31_IC");
    model.component("comp1").geom("geom1").feature("wp32").geom().create("ic32", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp32").geom().feature("ic32")
         .label("fascicle31_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp32").geom().feature("ic32").set("contributeto", "csel96");
    model.component("comp1").geom("geom1").feature("wp32").geom().feature("ic32").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp32").geom().feature("ic32")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/37/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp32").geom().feature("ic32").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp32").geom().create("csol32", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp32").geom().feature("csol32")
         .label("fascicle31_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp32").geom().feature("csol32").selection("input")
         .named("csel96");
    model.component("comp1").geom("geom1").create("ext32", "Extrude");
    model.component("comp1").geom("geom1").feature("ext32").label("fascicle31_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext32").set("contributeto", "csel95");
    model.component("comp1").geom("geom1").feature("ext32").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext32").selection("input").named("csel94");

    model.param()
         .set("fascicle32", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/38/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel97", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel97").label("fascicle32_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel98", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel98").label("fascicle32_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp33", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp33").label("fascicle32_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp33").set("contributeto", "csel97");
    model.component("comp1").geom("geom1").feature("wp33").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp33").geom().selection()
         .create("csel99", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp33").geom().selection("csel99").label("fascicle32_IC");
    model.component("comp1").geom("geom1").feature("wp33").geom().create("ic33", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp33").geom().feature("ic33")
         .label("fascicle32_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp33").geom().feature("ic33").set("contributeto", "csel99");
    model.component("comp1").geom("geom1").feature("wp33").geom().feature("ic33").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp33").geom().feature("ic33")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/38/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp33").geom().feature("ic33").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp33").geom().create("csol33", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp33").geom().feature("csol33")
         .label("fascicle32_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp33").geom().feature("csol33").selection("input")
         .named("csel99");
    model.component("comp1").geom("geom1").create("ext33", "Extrude");
    model.component("comp1").geom("geom1").feature("ext33").label("fascicle32_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext33").set("contributeto", "csel98");
    model.component("comp1").geom("geom1").feature("ext33").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext33").selection("input").named("csel97");

    model.param()
         .set("fascicle33", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/39/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel100", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel100").label("fascicle33_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel101", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel101").label("fascicle33_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp34", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp34").label("fascicle33_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp34").set("contributeto", "csel100");
    model.component("comp1").geom("geom1").feature("wp34").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp34").geom().selection()
         .create("csel102", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp34").geom().selection("csel102").label("fascicle33_IC");
    model.component("comp1").geom("geom1").feature("wp34").geom().create("ic34", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp34").geom().feature("ic34")
         .label("fascicle33_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp34").geom().feature("ic34").set("contributeto", "csel102");
    model.component("comp1").geom("geom1").feature("wp34").geom().feature("ic34").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp34").geom().feature("ic34")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/39/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp34").geom().feature("ic34").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp34").geom().create("csol34", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp34").geom().feature("csol34")
         .label("fascicle33_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp34").geom().feature("csol34").selection("input")
         .named("csel102");
    model.component("comp1").geom("geom1").create("ext34", "Extrude");
    model.component("comp1").geom("geom1").feature("ext34").label("fascicle33_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext34").set("contributeto", "csel101");
    model.component("comp1").geom("geom1").feature("ext34").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext34").selection("input").named("csel100");

    model.param()
         .set("fascicle34", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/4/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel103", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel103").label("fascicle34_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel104", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel104").label("fascicle34_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp35", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp35").label("fascicle34_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp35").set("contributeto", "csel103");
    model.component("comp1").geom("geom1").feature("wp35").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp35").geom().selection()
         .create("csel105", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp35").geom().selection("csel105").label("fascicle34_IC");
    model.component("comp1").geom("geom1").feature("wp35").geom().create("ic35", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp35").geom().feature("ic35")
         .label("fascicle34_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp35").geom().feature("ic35").set("contributeto", "csel105");
    model.component("comp1").geom("geom1").feature("wp35").geom().feature("ic35").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp35").geom().feature("ic35")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/4/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp35").geom().feature("ic35").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp35").geom().create("csol35", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp35").geom().feature("csol35")
         .label("fascicle34_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp35").geom().feature("csol35").selection("input")
         .named("csel105");
    model.component("comp1").geom("geom1").create("ext35", "Extrude");
    model.component("comp1").geom("geom1").feature("ext35").label("fascicle34_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext35").set("contributeto", "csel104");
    model.component("comp1").geom("geom1").feature("ext35").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext35").selection("input").named("csel103");

    model.param()
         .set("fascicle35", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/40/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel106", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel106").label("fascicle35_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel107", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel107").label("fascicle35_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp36", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp36").label("fascicle35_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp36").set("contributeto", "csel106");
    model.component("comp1").geom("geom1").feature("wp36").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp36").geom().selection()
         .create("csel108", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp36").geom().selection("csel108").label("fascicle35_IC");
    model.component("comp1").geom("geom1").feature("wp36").geom().create("ic36", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp36").geom().feature("ic36")
         .label("fascicle35_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp36").geom().feature("ic36").set("contributeto", "csel108");
    model.component("comp1").geom("geom1").feature("wp36").geom().feature("ic36").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp36").geom().feature("ic36")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/40/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp36").geom().feature("ic36").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp36").geom().create("csol36", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp36").geom().feature("csol36")
         .label("fascicle35_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp36").geom().feature("csol36").selection("input")
         .named("csel108");
    model.component("comp1").geom("geom1").create("ext36", "Extrude");
    model.component("comp1").geom("geom1").feature("ext36").label("fascicle35_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext36").set("contributeto", "csel107");
    model.component("comp1").geom("geom1").feature("ext36").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext36").selection("input").named("csel106");

    model.param()
         .set("fascicle36", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/41/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel109", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel109").label("fascicle36_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel110", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel110").label("fascicle36_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp37", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp37").label("fascicle36_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp37").set("contributeto", "csel109");
    model.component("comp1").geom("geom1").feature("wp37").set("unite", true);

    return model;
  }

  public static Model run5(Model model) {
    model.component("comp1").geom("geom1").feature("wp37").geom().selection()
         .create("csel111", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp37").geom().selection("csel111").label("fascicle36_IC");
    model.component("comp1").geom("geom1").feature("wp37").geom().create("ic37", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp37").geom().feature("ic37")
         .label("fascicle36_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp37").geom().feature("ic37").set("contributeto", "csel111");
    model.component("comp1").geom("geom1").feature("wp37").geom().feature("ic37").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp37").geom().feature("ic37")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/41/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp37").geom().feature("ic37").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp37").geom().create("csol37", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp37").geom().feature("csol37")
         .label("fascicle36_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp37").geom().feature("csol37").selection("input")
         .named("csel111");
    model.component("comp1").geom("geom1").create("ext37", "Extrude");
    model.component("comp1").geom("geom1").feature("ext37").label("fascicle36_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext37").set("contributeto", "csel110");
    model.component("comp1").geom("geom1").feature("ext37").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext37").selection("input").named("csel109");

    model.param()
         .set("fascicle37", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/42/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel112", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel112").label("fascicle37_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel113", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel113").label("fascicle37_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp38", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp38").label("fascicle37_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp38").set("contributeto", "csel112");
    model.component("comp1").geom("geom1").feature("wp38").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp38").geom().selection()
         .create("csel114", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp38").geom().selection("csel114").label("fascicle37_IC");
    model.component("comp1").geom("geom1").feature("wp38").geom().create("ic38", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp38").geom().feature("ic38")
         .label("fascicle37_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp38").geom().feature("ic38").set("contributeto", "csel114");
    model.component("comp1").geom("geom1").feature("wp38").geom().feature("ic38").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp38").geom().feature("ic38")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/42/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp38").geom().feature("ic38").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp38").geom().create("csol38", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp38").geom().feature("csol38")
         .label("fascicle37_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp38").geom().feature("csol38").selection("input")
         .named("csel114");
    model.component("comp1").geom("geom1").create("ext38", "Extrude");
    model.component("comp1").geom("geom1").feature("ext38").label("fascicle37_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext38").set("contributeto", "csel113");
    model.component("comp1").geom("geom1").feature("ext38").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext38").selection("input").named("csel112");

    model.param()
         .set("fascicle38", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/43/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel115", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel115").label("fascicle38_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel116", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel116").label("fascicle38_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp39", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp39").label("fascicle38_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp39").set("contributeto", "csel115");
    model.component("comp1").geom("geom1").feature("wp39").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp39").geom().selection()
         .create("csel117", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp39").geom().selection("csel117").label("fascicle38_IC");
    model.component("comp1").geom("geom1").feature("wp39").geom().create("ic39", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp39").geom().feature("ic39")
         .label("fascicle38_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp39").geom().feature("ic39").set("contributeto", "csel117");
    model.component("comp1").geom("geom1").feature("wp39").geom().feature("ic39").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp39").geom().feature("ic39")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/43/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp39").geom().feature("ic39").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp39").geom().create("csol39", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp39").geom().feature("csol39")
         .label("fascicle38_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp39").geom().feature("csol39").selection("input")
         .named("csel117");
    model.component("comp1").geom("geom1").create("ext39", "Extrude");
    model.component("comp1").geom("geom1").feature("ext39").label("fascicle38_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext39").set("contributeto", "csel116");
    model.component("comp1").geom("geom1").feature("ext39").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext39").selection("input").named("csel115");

    model.param()
         .set("fascicle39", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/44/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel118", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel118").label("fascicle39_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel119", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel119").label("fascicle39_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp40", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp40").label("fascicle39_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp40").set("contributeto", "csel118");
    model.component("comp1").geom("geom1").feature("wp40").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp40").geom().selection()
         .create("csel120", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp40").geom().selection("csel120").label("fascicle39_IC");
    model.component("comp1").geom("geom1").feature("wp40").geom().create("ic40", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp40").geom().feature("ic40")
         .label("fascicle39_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp40").geom().feature("ic40").set("contributeto", "csel120");
    model.component("comp1").geom("geom1").feature("wp40").geom().feature("ic40").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp40").geom().feature("ic40")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/44/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp40").geom().feature("ic40").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp40").geom().create("csol40", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp40").geom().feature("csol40")
         .label("fascicle39_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp40").geom().feature("csol40").selection("input")
         .named("csel120");
    model.component("comp1").geom("geom1").create("ext40", "Extrude");
    model.component("comp1").geom("geom1").feature("ext40").label("fascicle39_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext40").set("contributeto", "csel119");
    model.component("comp1").geom("geom1").feature("ext40").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext40").selection("input").named("csel118");

    model.param()
         .set("fascicle40", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/45/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel121", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel121").label("fascicle40_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel122", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel122").label("fascicle40_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp41", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp41").label("fascicle40_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp41").set("contributeto", "csel121");
    model.component("comp1").geom("geom1").feature("wp41").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp41").geom().selection()
         .create("csel123", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp41").geom().selection("csel123").label("fascicle40_IC");
    model.component("comp1").geom("geom1").feature("wp41").geom().create("ic41", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp41").geom().feature("ic41")
         .label("fascicle40_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp41").geom().feature("ic41").set("contributeto", "csel123");
    model.component("comp1").geom("geom1").feature("wp41").geom().feature("ic41").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp41").geom().feature("ic41")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/45/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp41").geom().feature("ic41").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp41").geom().create("csol41", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp41").geom().feature("csol41")
         .label("fascicle40_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp41").geom().feature("csol41").selection("input")
         .named("csel123");
    model.component("comp1").geom("geom1").create("ext41", "Extrude");
    model.component("comp1").geom("geom1").feature("ext41").label("fascicle40_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext41").set("contributeto", "csel122");
    model.component("comp1").geom("geom1").feature("ext41").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext41").selection("input").named("csel121");

    model.param()
         .set("fascicle41", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/46/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel124", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel124").label("fascicle41_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel125", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel125").label("fascicle41_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp42", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp42").label("fascicle41_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp42").set("contributeto", "csel124");
    model.component("comp1").geom("geom1").feature("wp42").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp42").geom().selection()
         .create("csel126", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp42").geom().selection("csel126").label("fascicle41_IC");
    model.component("comp1").geom("geom1").feature("wp42").geom().create("ic42", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp42").geom().feature("ic42")
         .label("fascicle41_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp42").geom().feature("ic42").set("contributeto", "csel126");
    model.component("comp1").geom("geom1").feature("wp42").geom().feature("ic42").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp42").geom().feature("ic42")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/46/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp42").geom().feature("ic42").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp42").geom().create("csol42", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp42").geom().feature("csol42")
         .label("fascicle41_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp42").geom().feature("csol42").selection("input")
         .named("csel126");
    model.component("comp1").geom("geom1").create("ext42", "Extrude");
    model.component("comp1").geom("geom1").feature("ext42").label("fascicle41_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext42").set("contributeto", "csel125");
    model.component("comp1").geom("geom1").feature("ext42").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext42").selection("input").named("csel124");

    model.param()
         .set("fascicle42", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/47/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel127", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel127").label("fascicle42_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel128", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel128").label("fascicle42_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp43", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp43").label("fascicle42_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp43").set("contributeto", "csel127");
    model.component("comp1").geom("geom1").feature("wp43").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp43").geom().selection()
         .create("csel129", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp43").geom().selection("csel129").label("fascicle42_IC");
    model.component("comp1").geom("geom1").feature("wp43").geom().create("ic43", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp43").geom().feature("ic43")
         .label("fascicle42_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp43").geom().feature("ic43").set("contributeto", "csel129");
    model.component("comp1").geom("geom1").feature("wp43").geom().feature("ic43").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp43").geom().feature("ic43")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/47/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp43").geom().feature("ic43").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp43").geom().create("csol43", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp43").geom().feature("csol43")
         .label("fascicle42_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp43").geom().feature("csol43").selection("input")
         .named("csel129");
    model.component("comp1").geom("geom1").create("ext43", "Extrude");
    model.component("comp1").geom("geom1").feature("ext43").label("fascicle42_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext43").set("contributeto", "csel128");
    model.component("comp1").geom("geom1").feature("ext43").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext43").selection("input").named("csel127");

    model.param()
         .set("fascicle43", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/48/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel130", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel130").label("fascicle43_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel131", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel131").label("fascicle43_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp44", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp44").label("fascicle43_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp44").set("contributeto", "csel130");
    model.component("comp1").geom("geom1").feature("wp44").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp44").geom().selection()
         .create("csel132", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp44").geom().selection("csel132").label("fascicle43_IC");
    model.component("comp1").geom("geom1").feature("wp44").geom().create("ic44", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp44").geom().feature("ic44")
         .label("fascicle43_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp44").geom().feature("ic44").set("contributeto", "csel132");
    model.component("comp1").geom("geom1").feature("wp44").geom().feature("ic44").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp44").geom().feature("ic44")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/48/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp44").geom().feature("ic44").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp44").geom().create("csol44", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp44").geom().feature("csol44")
         .label("fascicle43_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp44").geom().feature("csol44").selection("input")
         .named("csel132");
    model.component("comp1").geom("geom1").create("ext44", "Extrude");
    model.component("comp1").geom("geom1").feature("ext44").label("fascicle43_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext44").set("contributeto", "csel131");
    model.component("comp1").geom("geom1").feature("ext44").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext44").selection("input").named("csel130");

    model.param()
         .set("fascicle44", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/49/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel133", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel133").label("fascicle44_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel134", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel134").label("fascicle44_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp45", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp45").label("fascicle44_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp45").set("contributeto", "csel133");
    model.component("comp1").geom("geom1").feature("wp45").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp45").geom().selection()
         .create("csel135", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp45").geom().selection("csel135").label("fascicle44_IC");
    model.component("comp1").geom("geom1").feature("wp45").geom().create("ic45", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp45").geom().feature("ic45")
         .label("fascicle44_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp45").geom().feature("ic45").set("contributeto", "csel135");
    model.component("comp1").geom("geom1").feature("wp45").geom().feature("ic45").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp45").geom().feature("ic45")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/49/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp45").geom().feature("ic45").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp45").geom().create("csol45", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp45").geom().feature("csol45")
         .label("fascicle44_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp45").geom().feature("csol45").selection("input")
         .named("csel135");
    model.component("comp1").geom("geom1").create("ext45", "Extrude");
    model.component("comp1").geom("geom1").feature("ext45").label("fascicle44_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext45").set("contributeto", "csel134");
    model.component("comp1").geom("geom1").feature("ext45").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext45").selection("input").named("csel133");

    model.param()
         .set("fascicle45", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/5/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel136", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel136").label("fascicle45_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel137", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel137").label("fascicle45_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp46", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp46").label("fascicle45_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp46").set("contributeto", "csel136");
    model.component("comp1").geom("geom1").feature("wp46").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp46").geom().selection()
         .create("csel138", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp46").geom().selection("csel138").label("fascicle45_IC");
    model.component("comp1").geom("geom1").feature("wp46").geom().create("ic46", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp46").geom().feature("ic46")
         .label("fascicle45_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp46").geom().feature("ic46").set("contributeto", "csel138");
    model.component("comp1").geom("geom1").feature("wp46").geom().feature("ic46").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp46").geom().feature("ic46")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/5/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp46").geom().feature("ic46").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp46").geom().create("csol46", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp46").geom().feature("csol46")
         .label("fascicle45_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp46").geom().feature("csol46").selection("input")
         .named("csel138");
    model.component("comp1").geom("geom1").create("ext46", "Extrude");
    model.component("comp1").geom("geom1").feature("ext46").label("fascicle45_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext46").set("contributeto", "csel137");
    model.component("comp1").geom("geom1").feature("ext46").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext46").selection("input").named("csel136");

    model.param()
         .set("fascicle46", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/50/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel139", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel139").label("fascicle46_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel140", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel140").label("fascicle46_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp47", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp47").label("fascicle46_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp47").set("contributeto", "csel139");
    model.component("comp1").geom("geom1").feature("wp47").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp47").geom().selection()
         .create("csel141", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp47").geom().selection("csel141").label("fascicle46_IC");
    model.component("comp1").geom("geom1").feature("wp47").geom().create("ic47", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp47").geom().feature("ic47")
         .label("fascicle46_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp47").geom().feature("ic47").set("contributeto", "csel141");
    model.component("comp1").geom("geom1").feature("wp47").geom().feature("ic47").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp47").geom().feature("ic47")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/50/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp47").geom().feature("ic47").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp47").geom().create("csol47", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp47").geom().feature("csol47")
         .label("fascicle46_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp47").geom().feature("csol47").selection("input")
         .named("csel141");
    model.component("comp1").geom("geom1").create("ext47", "Extrude");
    model.component("comp1").geom("geom1").feature("ext47").label("fascicle46_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext47").set("contributeto", "csel140");
    model.component("comp1").geom("geom1").feature("ext47").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext47").selection("input").named("csel139");

    model.param()
         .set("fascicle47", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/51/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel142", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel142").label("fascicle47_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel143", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel143").label("fascicle47_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp48", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp48").label("fascicle47_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp48").set("contributeto", "csel142");
    model.component("comp1").geom("geom1").feature("wp48").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp48").geom().selection()
         .create("csel144", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp48").geom().selection("csel144").label("fascicle47_IC");
    model.component("comp1").geom("geom1").feature("wp48").geom().create("ic48", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp48").geom().feature("ic48")
         .label("fascicle47_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp48").geom().feature("ic48").set("contributeto", "csel144");
    model.component("comp1").geom("geom1").feature("wp48").geom().feature("ic48").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp48").geom().feature("ic48")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/51/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp48").geom().feature("ic48").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp48").geom().create("csol48", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp48").geom().feature("csol48")
         .label("fascicle47_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp48").geom().feature("csol48").selection("input")
         .named("csel144");
    model.component("comp1").geom("geom1").create("ext48", "Extrude");
    model.component("comp1").geom("geom1").feature("ext48").label("fascicle47_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext48").set("contributeto", "csel143");
    model.component("comp1").geom("geom1").feature("ext48").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext48").selection("input").named("csel142");

    model.param()
         .set("fascicle48", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/52/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel145", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel145").label("fascicle48_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel146", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel146").label("fascicle48_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp49", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp49").label("fascicle48_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp49").set("contributeto", "csel145");
    model.component("comp1").geom("geom1").feature("wp49").set("unite", true);

    return model;
  }

  public static Model run6(Model model) {
    model.component("comp1").geom("geom1").feature("wp49").geom().selection()
         .create("csel147", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp49").geom().selection("csel147").label("fascicle48_IC");
    model.component("comp1").geom("geom1").feature("wp49").geom().create("ic49", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp49").geom().feature("ic49")
         .label("fascicle48_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp49").geom().feature("ic49").set("contributeto", "csel147");
    model.component("comp1").geom("geom1").feature("wp49").geom().feature("ic49").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp49").geom().feature("ic49")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/52/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp49").geom().feature("ic49").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp49").geom().create("csol49", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp49").geom().feature("csol49")
         .label("fascicle48_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp49").geom().feature("csol49").selection("input")
         .named("csel147");
    model.component("comp1").geom("geom1").create("ext49", "Extrude");
    model.component("comp1").geom("geom1").feature("ext49").label("fascicle48_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext49").set("contributeto", "csel146");
    model.component("comp1").geom("geom1").feature("ext49").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext49").selection("input").named("csel145");

    model.param()
         .set("fascicle49", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/53/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel148", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel148").label("fascicle49_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel149", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel149").label("fascicle49_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp50", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp50").label("fascicle49_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp50").set("contributeto", "csel148");
    model.component("comp1").geom("geom1").feature("wp50").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp50").geom().selection()
         .create("csel150", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp50").geom().selection("csel150").label("fascicle49_IC");
    model.component("comp1").geom("geom1").feature("wp50").geom().create("ic50", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp50").geom().feature("ic50")
         .label("fascicle49_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp50").geom().feature("ic50").set("contributeto", "csel150");
    model.component("comp1").geom("geom1").feature("wp50").geom().feature("ic50").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp50").geom().feature("ic50")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/53/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp50").geom().feature("ic50").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp50").geom().create("csol50", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp50").geom().feature("csol50")
         .label("fascicle49_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp50").geom().feature("csol50").selection("input")
         .named("csel150");
    model.component("comp1").geom("geom1").create("ext50", "Extrude");
    model.component("comp1").geom("geom1").feature("ext50").label("fascicle49_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext50").set("contributeto", "csel149");
    model.component("comp1").geom("geom1").feature("ext50").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext50").selection("input").named("csel148");

    model.param()
         .set("fascicle50", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/54/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel151", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel151").label("fascicle50_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel152", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel152").label("fascicle50_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp51", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp51").label("fascicle50_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp51").set("contributeto", "csel151");
    model.component("comp1").geom("geom1").feature("wp51").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp51").geom().selection()
         .create("csel153", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp51").geom().selection("csel153").label("fascicle50_IC");
    model.component("comp1").geom("geom1").feature("wp51").geom().create("ic51", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp51").geom().feature("ic51")
         .label("fascicle50_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp51").geom().feature("ic51").set("contributeto", "csel153");
    model.component("comp1").geom("geom1").feature("wp51").geom().feature("ic51").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp51").geom().feature("ic51")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/54/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp51").geom().feature("ic51").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp51").geom().create("csol51", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp51").geom().feature("csol51")
         .label("fascicle50_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp51").geom().feature("csol51").selection("input")
         .named("csel153");
    model.component("comp1").geom("geom1").create("ext51", "Extrude");
    model.component("comp1").geom("geom1").feature("ext51").label("fascicle50_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext51").set("contributeto", "csel152");
    model.component("comp1").geom("geom1").feature("ext51").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext51").selection("input").named("csel151");

    model.param()
         .set("fascicle51", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/55/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel154", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel154").label("fascicle51_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel155", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel155").label("fascicle51_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp52", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp52").label("fascicle51_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp52").set("contributeto", "csel154");
    model.component("comp1").geom("geom1").feature("wp52").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp52").geom().selection()
         .create("csel156", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp52").geom().selection("csel156").label("fascicle51_IC");
    model.component("comp1").geom("geom1").feature("wp52").geom().create("ic52", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp52").geom().feature("ic52")
         .label("fascicle51_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp52").geom().feature("ic52").set("contributeto", "csel156");
    model.component("comp1").geom("geom1").feature("wp52").geom().feature("ic52").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp52").geom().feature("ic52")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/55/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp52").geom().feature("ic52").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp52").geom().create("csol52", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp52").geom().feature("csol52")
         .label("fascicle51_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp52").geom().feature("csol52").selection("input")
         .named("csel156");
    model.component("comp1").geom("geom1").create("ext52", "Extrude");
    model.component("comp1").geom("geom1").feature("ext52").label("fascicle51_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext52").set("contributeto", "csel155");
    model.component("comp1").geom("geom1").feature("ext52").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext52").selection("input").named("csel154");

    model.param()
         .set("fascicle52", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/56/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel157", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel157").label("fascicle52_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel158", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel158").label("fascicle52_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp53", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp53").label("fascicle52_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp53").set("contributeto", "csel157");
    model.component("comp1").geom("geom1").feature("wp53").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp53").geom().selection()
         .create("csel159", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp53").geom().selection("csel159").label("fascicle52_IC");
    model.component("comp1").geom("geom1").feature("wp53").geom().create("ic53", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp53").geom().feature("ic53")
         .label("fascicle52_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp53").geom().feature("ic53").set("contributeto", "csel159");
    model.component("comp1").geom("geom1").feature("wp53").geom().feature("ic53").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp53").geom().feature("ic53")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/56/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp53").geom().feature("ic53").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp53").geom().create("csol53", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp53").geom().feature("csol53")
         .label("fascicle52_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp53").geom().feature("csol53").selection("input")
         .named("csel159");
    model.component("comp1").geom("geom1").create("ext53", "Extrude");
    model.component("comp1").geom("geom1").feature("ext53").label("fascicle52_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext53").set("contributeto", "csel158");
    model.component("comp1").geom("geom1").feature("ext53").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext53").selection("input").named("csel157");

    model.param()
         .set("fascicle53", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/57/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel160", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel160").label("fascicle53_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel161", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel161").label("fascicle53_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp54", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp54").label("fascicle53_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp54").set("contributeto", "csel160");
    model.component("comp1").geom("geom1").feature("wp54").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp54").geom().selection()
         .create("csel162", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp54").geom().selection("csel162").label("fascicle53_IC");
    model.component("comp1").geom("geom1").feature("wp54").geom().create("ic54", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp54").geom().feature("ic54")
         .label("fascicle53_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp54").geom().feature("ic54").set("contributeto", "csel162");
    model.component("comp1").geom("geom1").feature("wp54").geom().feature("ic54").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp54").geom().feature("ic54")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/57/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp54").geom().feature("ic54").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp54").geom().create("csol54", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp54").geom().feature("csol54")
         .label("fascicle53_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp54").geom().feature("csol54").selection("input")
         .named("csel162");
    model.component("comp1").geom("geom1").create("ext54", "Extrude");
    model.component("comp1").geom("geom1").feature("ext54").label("fascicle53_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext54").set("contributeto", "csel161");
    model.component("comp1").geom("geom1").feature("ext54").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext54").selection("input").named("csel160");

    model.param()
         .set("fascicle54", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/58/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel163", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel163").label("fascicle54_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel164", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel164").label("fascicle54_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp55", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp55").label("fascicle54_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp55").set("contributeto", "csel163");
    model.component("comp1").geom("geom1").feature("wp55").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp55").geom().selection()
         .create("csel165", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp55").geom().selection("csel165").label("fascicle54_IC");
    model.component("comp1").geom("geom1").feature("wp55").geom().create("ic55", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp55").geom().feature("ic55")
         .label("fascicle54_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp55").geom().feature("ic55").set("contributeto", "csel165");
    model.component("comp1").geom("geom1").feature("wp55").geom().feature("ic55").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp55").geom().feature("ic55")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/58/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp55").geom().feature("ic55").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp55").geom().create("csol55", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp55").geom().feature("csol55")
         .label("fascicle54_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp55").geom().feature("csol55").selection("input")
         .named("csel165");
    model.component("comp1").geom("geom1").create("ext55", "Extrude");
    model.component("comp1").geom("geom1").feature("ext55").label("fascicle54_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext55").set("contributeto", "csel164");
    model.component("comp1").geom("geom1").feature("ext55").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext55").selection("input").named("csel163");

    model.param()
         .set("fascicle55", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/6/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel166", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel166").label("fascicle55_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel167", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel167").label("fascicle55_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp56", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp56").label("fascicle55_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp56").set("contributeto", "csel166");
    model.component("comp1").geom("geom1").feature("wp56").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp56").geom().selection()
         .create("csel168", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp56").geom().selection("csel168").label("fascicle55_IC");
    model.component("comp1").geom("geom1").feature("wp56").geom().create("ic56", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp56").geom().feature("ic56")
         .label("fascicle55_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp56").geom().feature("ic56").set("contributeto", "csel168");
    model.component("comp1").geom("geom1").feature("wp56").geom().feature("ic56").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp56").geom().feature("ic56")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/6/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp56").geom().feature("ic56").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp56").geom().create("csol56", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp56").geom().feature("csol56")
         .label("fascicle55_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp56").geom().feature("csol56").selection("input")
         .named("csel168");
    model.component("comp1").geom("geom1").create("ext56", "Extrude");
    model.component("comp1").geom("geom1").feature("ext56").label("fascicle55_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext56").set("contributeto", "csel167");
    model.component("comp1").geom("geom1").feature("ext56").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext56").selection("input").named("csel166");

    model.param()
         .set("fascicle56", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/7/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel169", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel169").label("fascicle56_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel170", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel170").label("fascicle56_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp57", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp57").label("fascicle56_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp57").set("contributeto", "csel169");
    model.component("comp1").geom("geom1").feature("wp57").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp57").geom().selection()
         .create("csel171", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp57").geom().selection("csel171").label("fascicle56_IC");
    model.component("comp1").geom("geom1").feature("wp57").geom().create("ic57", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp57").geom().feature("ic57")
         .label("fascicle56_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp57").geom().feature("ic57").set("contributeto", "csel171");
    model.component("comp1").geom("geom1").feature("wp57").geom().feature("ic57").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp57").geom().feature("ic57")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/7/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp57").geom().feature("ic57").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp57").geom().create("csol57", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp57").geom().feature("csol57")
         .label("fascicle56_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp57").geom().feature("csol57").selection("input")
         .named("csel171");
    model.component("comp1").geom("geom1").create("ext57", "Extrude");
    model.component("comp1").geom("geom1").feature("ext57").label("fascicle56_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext57").set("contributeto", "csel170");
    model.component("comp1").geom("geom1").feature("ext57").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext57").selection("input").named("csel169");

    model.param()
         .set("fascicle57", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/8/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel172", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel172").label("fascicle57_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel173", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel173").label("fascicle57_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp58", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp58").label("fascicle57_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp58").set("contributeto", "csel172");
    model.component("comp1").geom("geom1").feature("wp58").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp58").geom().selection()
         .create("csel174", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp58").geom().selection("csel174").label("fascicle57_IC");
    model.component("comp1").geom("geom1").feature("wp58").geom().create("ic58", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp58").geom().feature("ic58")
         .label("fascicle57_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp58").geom().feature("ic58").set("contributeto", "csel174");
    model.component("comp1").geom("geom1").feature("wp58").geom().feature("ic58").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp58").geom().feature("ic58")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/8/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp58").geom().feature("ic58").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp58").geom().create("csol58", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp58").geom().feature("csol58")
         .label("fascicle57_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp58").geom().feature("csol58").selection("input")
         .named("csel174");
    model.component("comp1").geom("geom1").create("ext58", "Extrude");
    model.component("comp1").geom("geom1").feature("ext58").label("fascicle57_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext58").set("contributeto", "csel173");
    model.component("comp1").geom("geom1").feature("ext58").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext58").selection("input").named("csel172");

    model.param()
         .set("fascicle58", "NaN", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/9/inners/0.txt");

    model.component("comp1").geom("geom1").selection().create("csel175", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel175").label("fascicle58_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel176", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel176").label("fascicle58_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp59", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp59").label("fascicle58_Fascicle Cross Section");
    model.component("comp1").geom("geom1").feature("wp59").set("contributeto", "csel175");
    model.component("comp1").geom("geom1").feature("wp59").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp59").geom().selection()
         .create("csel177", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp59").geom().selection("csel177").label("fascicle58_IC");
    model.component("comp1").geom("geom1").feature("wp59").geom().create("ic59", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp59").geom().feature("ic59")
         .label("fascicle58_InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp59").geom().feature("ic59").set("contributeto", "csel177");
    model.component("comp1").geom("geom1").feature("wp59").geom().feature("ic59").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp59").geom().feature("ic59")
         .set("filename", "D:\\Documents\\access/data/samples/Pig13-1/0/0/sectionwise2d/fascicles/9/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp59").geom().feature("ic59").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp59").geom().create("csol59", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp59").geom().feature("csol59")
         .label("fascicle58_Convert to Trace to Cross Section");
    model.component("comp1").geom("geom1").feature("wp59").geom().feature("csol59").selection("input")
         .named("csel177");
    model.component("comp1").geom("geom1").create("ext59", "Extrude");
    model.component("comp1").geom("geom1").feature("ext59").label("fascicle58_Make Fascicle");
    model.component("comp1").geom("geom1").feature("ext59").set("contributeto", "csel176");
    model.component("comp1").geom("geom1").feature("ext59").setIndex("distance", "Length_EM", 0);
    model.component("comp1").geom("geom1").feature("ext59").selection("input").named("csel175");
    model.component("comp1").geom("geom1").create("uni1", "Union");
    model.component("comp1").geom("geom1").feature("uni1").selection("input")
         .set("ext1", "ext10", "ext14", "ext2", "ext24", "ext4", "ext46");
    model.component("comp1").geom("geom1").feature("uni1").label("Fascicles Union");
    model.component("comp1").geom("geom1").selection().create("csel178", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel178").label("FASCICLES");
    model.component("comp1").geom("geom1").feature("uni1").set("contributeto", "csel178");
    model.component("comp1").geom("geom1").run("fin");

    model.component("comp1").mesh("mesh1").create("swe1", "Sweep");
    model.component("comp1").mesh("mesh1").feature("swe1").selection().geom("geom1", 3);
    model.component("comp1").mesh("mesh1").feature("swe1").selection().named("geom1_csel178_dom");

    model.component("comp1").physics("ec").feature("pcs1").set("Qjp", 0.001);

    model.label("parts_test.mph");

    model.component("comp1").view("view1").set("transparency", true);

    model.component("comp1").geom("geom1").runPre("uni1");

    model.component("comp1").material().create("matlnk6", "Link");
    model.component("comp1").material("matlnk6").selection().named("geom1_csel178_dom");

    return model;
  }

  public static void main(String[] args) {
    Model model = run();
    model = run2(model);
    model = run3(model);
    model = run4(model);
    model = run5(model);
    run6(model);
  }

}

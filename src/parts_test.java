/*
 * parts_test.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Nov 15 2019, 16:24 by COMSOL 5.4.0.388. */
public class parts_test {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model.modelPath("D:\\Documents\\access\\src");

    model.component().create("comp1", true);

    model.component("comp1").geom().create("geom1", 3);
    model.component("comp1").geom("geom1").lengthUnit("\u00b5m");

    model.component("comp1").physics().create("ec", "ConductiveMedia", "geom1");

    model.component("comp1").mesh().create("mesh1");

    model.param().set("a_nerve", "2000414.0499361656 [micrometer^2]");
    model.param().set("r_nerve", "sqrt(a_nerve/pi)");
    model.param().set("rho_peri", "1149 [ohm*m]");
    model.param().set("z_nerve", 50000);
    model.param().set("r_ground", 10000);

    model.geom().create("part1", "Part", 3);
    model.geom("part1").label("Medium_Primitive");
    model.geom("part1").lengthUnit("\u00b5m");
    model.geom("part1").inputParam().set("radius", "10 [mm]");
    model.geom("part1").inputParam().set("length", "100 [mm]");
    model.geom("part1").selection().create("csel1", "CumulativeSelection");
    model.geom("part1").selection("csel1").label("MEDIUM");
    model.geom("part1").create("cyl1", "Cylinder");
    model.geom("part1").feature("cyl1").label("Medium");
    model.geom("part1").feature("cyl1").set("r", "radius");
    model.geom("part1").feature("cyl1").set("h", "length");
    model.geom("part1").feature("cyl1").set("contributeto", "csel1");

    model.material().create("mat1", "Common", "");
    model.material("mat1").label("fat");
    model.material("mat1").propertyGroup("def").set("electricconductivity", new String[]{"1/30"});
    model.material().create("mat2", "Common", "");
    model.material("mat2").label("perineurium_DC");
    model.material("mat2").propertyGroup("def").set("electricconductivity", new String[]{"1/1149"});
    model.material().create("mat3", "Common", "");
    model.material("mat3").label("endoneurium");
    model.material("mat3").propertyGroup("def").set("electricconductivity", new String[]{"{1/6, 1/6, 1/1.75}"});
    model.material().create("mat4", "Common", "");
    model.material("mat4").label("epineurium");
    model.material("mat4").propertyGroup("def").set("electricconductivity", new String[]{"1/6.3"});

    model.component("comp1").geom("geom1").create("pi1", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi1").label("Medium");
    model.component("comp1").geom("geom1").feature("pi1").set("part", "part1");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("inputexpr", "radius", 10000);
    model.component("comp1").geom("geom1").feature("pi1").setEntry("inputexpr", "length", 50000);
    model.component("comp1").geom("geom1").feature("pi1").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi1").setEntry("selkeepdom", "pi1_csel1.dom", "on");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("selkeepbnd", "pi1_csel1.bnd", "on");

    model.component("comp1").physics("ec").create("gnd1", "Ground", 2);
    model.component("comp1").physics("ec").feature("gnd1").label("Ground");
    model.component("comp1").physics("ec").feature("gnd1").selection().named("geom1_pi1_csel1_bnd");

    model.component("comp1").material().create("matlnk1", "Link");
    model.component("comp1").material("matlnk1").label("Medium/MEDIUM/fat");
    model.component("comp1").material("matlnk1").set("link", "mat1");
    model.component("comp1").material("matlnk1").selection().named("geom1_pi1_csel1_dom");

    model.param().group().create("par1");
    model.param("par1").label("CorTec");
    model.param("par1").set("N_holes_CT", "0", "");
    model.param("par1").set("Theta_CT", "percent_circ_cuff_CT*360 [deg]", "");
    model.param("par1").set("Center_CT", "z_nerve/2", "");
    model.param("par1").set("R_in_CT", "max(r_nerve+thk_medium_gap_internal_CT,r_cuff_in_pre_CT)", "");
    model.param("par1").set("R_out_CT", "R_in_CT+thk_cuff_CT", "");
    model.param("par1").set("L_CT", "2 [mm]", "");
    model.param("par1").set("Rot_def_CT", "-(theta_cuff_CT-theta_contact_CT)/2", "");
    model.param("par1").set("D_hole_CT", "NaN", "");
    model.param("par1").set("Buffer_hole_CT", "NaN", "");
    model.param("par1").set("L_holecenter_cuffseam_CT", "NaN", "");
    model.param("par1").set("Pitch_holecenter_holecenter_CT", "NaN", "");
    model.param("par1").set("percent_circ_cuff_CT", "percent_circ_cuff_pre_CT*(r_cuff_in_pre_CT/R_in_CT)", "");
    model.param("par1").set("z_nerve_CT", "20 [mm]", "");
    model.param("par1").set("thk_medium_gap_internal_CT", "20 [um]", "");
    model.param("par1").set("r_cuff_in_pre_CT", "150 [um]", "");
    model.param("par1").set("recess_CT", "0", "");
    model.param("par1").set("Thk_elec_CT", "0.025 [mm]", "");
    model.param("par1").set("B_CT", "0.6 [mm]", "");
    model.param("par1").set("percent_circ_cuff_pre_CT", "1", "");
    model.param("par1").set("theta_contact_CT", "360*(B_CT/(2*pi*(R_in_CT+recess_CT))) [deg]", "");
    model.param("par1").set("theta_cuff_CT", "percent_circ_cuff_CT*360 [deg]", "");
    model.param("par1").set("thk_cuff_CT", "0.65 [mm]", "");
    model.param("par1").set("L_elec_CT", "0.3 [mm]", "");
    model.param("par1").set("Recess_CT", "0 [mm]", "");
    model.param("par1").set("Theta_contact_CT", "360*(B_CT/(2*pi*(R_in_CT+Recess_CT))) [deg]", "");
    model.param("par1").set("Rot_def_contact_CT", "0", "");
    model.param("par1").set("Pitch_CT", "1.5 [mm]", "");
    model.param("par1").set("Thk_fill_CT", "100 [um]", "");

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

    model.material().create("mat5", "Common", "");
    model.material("mat5").label("saline");
    model.material("mat5").propertyGroup("def").set("electricconductivity", new String[]{"1.76"});
    model.material().create("mat6", "Common", "");
    model.material("mat6").label("silicone");
    model.material("mat6").propertyGroup("def").set("electricconductivity", new String[]{"10^(-12)"});
    model.material().create("mat7", "Common", "");
    model.material("mat7").label("platinum");
    model.material("mat7").propertyGroup("def").set("electricconductivity", new String[]{"9.43*10^6"});

    model.component("comp1").geom("geom1").create("pi2", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi2").label("CorTec Cuff Fill");
    model.component("comp1").geom("geom1").feature("pi2").set("part", "part2");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "Radius", "R_out_CT+Thk_fill_CT");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "Thk", "Thk_fill_CT");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "L", "L_CT+2*Thk_fill_CT");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "z_center", "Center_CT");
    model.component("comp1").geom("geom1").feature("pi2").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi2").setEntry("selkeepdom", "pi2_csel1.dom", "on");

    model.component("comp1").material().create("matlnk2", "Link");
    model.component("comp1").material("matlnk2").label("CorTec Cuff Fill/CUFF FILL FINAL/saline");
    model.component("comp1").material("matlnk2").set("link", "mat5");
    model.component("comp1").material("matlnk2").selection().named("geom1_pi2_csel1_dom");

    model.component("comp1").geom("geom1").create("pi3", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi3").label("CorTec Cuff");
    model.component("comp1").geom("geom1").feature("pi3").set("part", "part3");
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
    model.component("comp1").material("matlnk3").label("CorTec Cuff/CUFF FINAL/silicone");
    model.component("comp1").material("matlnk3").set("link", "mat6");
    model.component("comp1").material("matlnk3").selection().named("geom1_pi3_csel3_dom");

    model.component("comp1").geom("geom1").create("pi4", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi4").label("CorTec Contact 1");
    model.component("comp1").geom("geom1").feature("pi4").set("part", "part4");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "Thk_elec", "Thk_elec_CT");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "L_elec", "L_elec_CT");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "R_in", "R_in_CT");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "Recess", "Recess_CT");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "Center", "Center_CT+(Pitch_CT/2)");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "Theta_contact", "Theta_contact_CT");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "Rot_def", "Rot_def_contact_CT");
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
    model.component("comp1").physics("ec").feature("pcs1").label("CorTec Contact 1 Current Source");

    model.component("comp1").material().create("matlnk4", "Link");
    model.component("comp1").material("matlnk4").label("CorTec Contact 1/CONTACT FINAL/platinum");
    model.component("comp1").material("matlnk4").set("link", "mat7");

    return model;
  }

  public static Model run2(Model model) {
    model.component("comp1").material("matlnk4").selection().named("geom1_pi4_csel4_dom");
    model.component("comp1").material().create("matlnk5", "Link");
    model.component("comp1").material("matlnk5").label("CorTec Contact 1/RECESS FINAL/saline");
    model.component("comp1").material("matlnk5").set("link", "mat5");
    model.component("comp1").material("matlnk5").selection().named("geom1_pi4_csel5_dom");

    model.component("comp1").geom("geom1").create("pi5", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi5").label("CorTec Contact 2");
    model.component("comp1").geom("geom1").feature("pi5").set("part", "part4");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "Thk_elec", "Thk_elec_CT");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "L_elec", "L_elec_CT");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "R_in", "R_in_CT");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "Recess", "Recess_CT");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "Center", "Center_CT-(Pitch_CT/2)");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "Theta_contact", "Theta_contact_CT");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("inputexpr", "Rot_def", "Rot_def_contact_CT");
    model.component("comp1").geom("geom1").feature("pi5").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepdom", "pi5_csel2.dom", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepdom", "pi5_csel3.dom", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepdom", "pi5_csel4.dom", "on");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepdom", "pi5_csel5.dom", "on");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeeppnt", "pi5_csel2.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeeppnt", "pi5_csel3.pnt", "on");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeeppnt", "pi5_csel4.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeeppnt", "pi5_csel5.pnt", "off");

    model.component("comp1").physics("ec").create("pcs2", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs2").selection().named("geom1_pi5_csel3_pnt");
    model.component("comp1").physics("ec").feature("pcs2").set("Qjp", 0.001);
    model.component("comp1").physics("ec").feature("pcs2").label("CorTec Contact 2 Current Source");

    model.component("comp1").material().create("matlnk6", "Link");
    model.component("comp1").material("matlnk6").label("CorTec Contact 2/CONTACT FINAL/platinum");
    model.component("comp1").material("matlnk6").set("link", "mat7");
    model.component("comp1").material("matlnk6").selection().named("geom1_pi5_csel4_dom");
    model.component("comp1").material().create("matlnk7", "Link");
    model.component("comp1").material("matlnk7").label("CorTec Contact 2/RECESS FINAL/saline");
    model.component("comp1").material("matlnk7").set("link", "mat5");
    model.component("comp1").material("matlnk7").selection().named("geom1_pi5_csel5_dom");

    model.component("comp1").geom("geom1").selection().create("csel1", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel1").label("EPINEURIUM");
    model.component("comp1").geom("geom1").selection().create("csel2", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel2").label("EPIXS");

    model.param().set("a_nerve", "2000414.0499361656 [micrometer^2]");
    model.param().set("r_nerve", "sqrt(a_nerve/pi)");

    model.component("comp1").geom("geom1").create("wp1", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp1").label("Epineurium Cross Section");
    model.component("comp1").geom("geom1").feature("wp1").set("contributeto", "csel2");
    model.component("comp1").geom("geom1").feature("wp1").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp1").geom().create("e1", "Ellipse");
    model.component("comp1").geom("geom1").feature("wp1").geom().feature("e1")
         .set("semiaxes", new String[]{"r_nerve", "r_nerve"});
    model.component("comp1").geom("geom1").create("ext1", "Extrude");
    model.component("comp1").geom("geom1").feature("ext1").label("Make Epineurium");
    model.component("comp1").geom("geom1").feature("ext1").set("contributeto", "csel1");
    model.component("comp1").geom("geom1").feature("ext1").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext1").selection("input").named("csel2");
    model.component("comp1").geom("geom1").selection().create("csel3", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel3").label("outer0_INNERS");
    model.component("comp1").geom("geom1").selection().create("csel4", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel4").label("outer0_OUTER");
    model.component("comp1").geom("geom1").selection().create("csel5", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel5").label("outer0_PERINEURIUM");
    model.component("comp1").geom("geom1").selection().create("csel6", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel6").label("outer0_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp2", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp2").set("contributeto", "csel3");
    model.component("comp1").geom("geom1").feature("wp2").set("selresult", true);
    model.component("comp1").geom("geom1").feature("wp2").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp2").label("outer0 Inners Geometry");
    model.component("comp1").geom("geom1").feature("wp2").geom().selection().create("csel7", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp2").geom().selection("csel7").label("outer0 inners_all");
    model.component("comp1").geom("geom1").feature("wp2").geom().selection().create("csel8", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp2").geom().selection("csel8").label("outer0 IC0");
    model.component("comp1").geom("geom1").feature("wp2").geom().create("ic1", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic1").label("outer0 Inner Trace 0");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic1").set("contributeto", "csel8");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic1").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic1")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/0/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic1").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp2").geom().create("csol1", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("csol1").label("outer0 Inner Surface 0");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("csol1").set("contributeto", "csel7");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("csol1").set("keep", false);
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("csol1").selection("input").named("csel8");
    model.component("comp1").geom("geom1").feature("wp2").geom().selection().create("csel9", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp2").geom().selection("csel9").label("outer0 IC1");
    model.component("comp1").geom("geom1").feature("wp2").geom().create("ic2", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic2").label("outer0 Inner Trace 1");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic2").set("contributeto", "csel9");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic2").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic2")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/0/inners/1.txt");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("ic2").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp2").geom().create("csol2", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("csol2").label("outer0 Inner Surface 1");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("csol2").set("contributeto", "csel7");
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("csol2").set("keep", false);
    model.component("comp1").geom("geom1").feature("wp2").geom().feature("csol2").selection("input").named("csel9");
    model.component("comp1").geom("geom1").create("wp3", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp3").label("outer0 Outer Geometry");
    model.component("comp1").geom("geom1").feature("wp3").set("contributeto", "csel4");
    model.component("comp1").geom("geom1").feature("wp3").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp3").geom().selection().create("csel10", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp3").geom().selection("csel10").label("outer0 OC");
    model.component("comp1").geom("geom1").feature("wp3").geom().selection().create("csel11", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp3").geom().selection("csel11").label("outer0 sel");
    model.component("comp1").geom("geom1").feature("wp3").geom().create("ic3", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("ic3").label("outer0 Outer Trace");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("ic3").set("contributeto", "csel10");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("ic3").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("ic3")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/0/outer/0.txt");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("ic3").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp3").geom().create("csol3", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("csol3").set("keep", false);
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("csol3").selection("input").named("csel10");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("csol3").set("contributeto", "csel11");
    model.component("comp1").geom("geom1").feature("wp3").geom().feature("csol3").label("outer0 Outer Surface");
    model.component("comp1").geom("geom1").create("ext2", "Extrude");
    model.component("comp1").geom("geom1").feature("ext2").label("outer0 Make Perineurium");
    model.component("comp1").geom("geom1").feature("ext2").set("contributeto", "csel5");
    model.component("comp1").geom("geom1").feature("ext2").set("workplane", "wp3");
    model.component("comp1").geom("geom1").feature("ext2").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext2").selection("input").named("csel4");
    model.component("comp1").geom("geom1").create("ext3", "Extrude");
    model.component("comp1").geom("geom1").feature("ext3").label("outer0 Make Endoneurium");
    model.component("comp1").geom("geom1").feature("ext3").set("contributeto", "csel6");
    model.component("comp1").geom("geom1").feature("ext3").set("workplane", "wp2");
    model.component("comp1").geom("geom1").feature("ext3").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext3").selection("input").named("csel3");
    model.component("comp1").geom("geom1").selection().create("csel12", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel12").label("outer1_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel13", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel13").label("outer1_ENDONEURIUM");

    model.param()
         .set("outer1_area", "45021.16724612822[um^2]", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/1/inners/0.txt");

    model.component("comp1").geom("geom1").create("wp4", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp4").label("outer1 Inner Geometry");
    model.component("comp1").geom("geom1").feature("wp4").set("contributeto", "csel12");
    model.component("comp1").geom("geom1").feature("wp4").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp4").geom().selection().create("csel14", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp4").geom().selection("csel14").label("outer1_IC");
    model.component("comp1").geom("geom1").feature("wp4").geom().create("ic4", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp4").geom().feature("ic4").label("outer1 Inner Trace 0");
    model.component("comp1").geom("geom1").feature("wp4").geom().feature("ic4").set("contributeto", "csel14");
    model.component("comp1").geom("geom1").feature("wp4").geom().feature("ic4").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp4").geom().feature("ic4")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/1/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp4").geom().feature("ic4").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp4").geom().create("csol4", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp4").geom().feature("csol4").label("outer1 Inner Surface 0");
    model.component("comp1").geom("geom1").feature("wp4").geom().feature("csol4").selection("input").named("csel14");
    model.component("comp1").geom("geom1").create("ext4", "Extrude");
    model.component("comp1").geom("geom1").feature("ext4").label("outer1 Make Endoneurium");
    model.component("comp1").geom("geom1").feature("ext4").set("contributeto", "csel13");
    model.component("comp1").geom("geom1").feature("ext4").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext4").selection("input").named("csel12");

    model.component("comp1").physics("ec").create("ci1", "ContactImpedance", 2);
    model.component("comp1").physics("ec").feature("ci1").label("outer1 ContactImpedance");
    model.component("comp1").physics("ec").feature("ci1").selection().named("geom1_csel13_bnd");
    model.component("comp1").physics("ec").feature("ci1").set("spec_type", "surfimp");
    model.component("comp1").physics("ec").feature("ci1").set("rhos", "rho_peri*0.03*2*sqrt(outer1_area/pi)");

    model.component("comp1").geom("geom1").selection().create("csel15", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel15").label("outer10_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel16", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel16").label("outer10_ENDONEURIUM");

    model.param()
         .set("outer10_area", "2378.2448550828967[um^2]", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/10/inners/0.txt");

    model.component("comp1").geom("geom1").create("wp5", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp5").label("outer10 Inner Geometry");
    model.component("comp1").geom("geom1").feature("wp5").set("contributeto", "csel15");
    model.component("comp1").geom("geom1").feature("wp5").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp5").geom().selection().create("csel17", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp5").geom().selection("csel17").label("outer10_IC");
    model.component("comp1").geom("geom1").feature("wp5").geom().create("ic5", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp5").geom().feature("ic5").label("outer10 Inner Trace 0");
    model.component("comp1").geom("geom1").feature("wp5").geom().feature("ic5").set("contributeto", "csel17");
    model.component("comp1").geom("geom1").feature("wp5").geom().feature("ic5").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp5").geom().feature("ic5")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/10/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp5").geom().feature("ic5").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp5").geom().create("csol5", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp5").geom().feature("csol5").label("outer10 Inner Surface 0");
    model.component("comp1").geom("geom1").feature("wp5").geom().feature("csol5").selection("input").named("csel17");
    model.component("comp1").geom("geom1").create("ext5", "Extrude");
    model.component("comp1").geom("geom1").feature("ext5").label("outer10 Make Endoneurium");
    model.component("comp1").geom("geom1").feature("ext5").set("contributeto", "csel16");
    model.component("comp1").geom("geom1").feature("ext5").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext5").selection("input").named("csel15");

    model.component("comp1").physics("ec").create("ci2", "ContactImpedance", 2);
    model.component("comp1").physics("ec").feature("ci2").label("outer10 ContactImpedance");
    model.component("comp1").physics("ec").feature("ci2").selection().named("geom1_csel16_bnd");
    model.component("comp1").physics("ec").feature("ci2").set("spec_type", "surfimp");
    model.component("comp1").physics("ec").feature("ci2").set("rhos", "rho_peri*0.03*2*sqrt(outer10_area/pi)");

    model.component("comp1").geom("geom1").selection().create("csel18", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel18").label("outer2_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel19", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel19").label("outer2_ENDONEURIUM");

    model.param()
         .set("outer2_area", "13084.777616821213[um^2]", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/2/inners/0.txt");

    model.component("comp1").geom("geom1").create("wp6", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp6").label("outer2 Inner Geometry");
    model.component("comp1").geom("geom1").feature("wp6").set("contributeto", "csel18");
    model.component("comp1").geom("geom1").feature("wp6").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp6").geom().selection().create("csel20", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp6").geom().selection("csel20").label("outer2_IC");
    model.component("comp1").geom("geom1").feature("wp6").geom().create("ic6", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp6").geom().feature("ic6").label("outer2 Inner Trace 0");
    model.component("comp1").geom("geom1").feature("wp6").geom().feature("ic6").set("contributeto", "csel20");
    model.component("comp1").geom("geom1").feature("wp6").geom().feature("ic6").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp6").geom().feature("ic6")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/2/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp6").geom().feature("ic6").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp6").geom().create("csol6", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp6").geom().feature("csol6").label("outer2 Inner Surface 0");
    model.component("comp1").geom("geom1").feature("wp6").geom().feature("csol6").selection("input").named("csel20");
    model.component("comp1").geom("geom1").create("ext6", "Extrude");
    model.component("comp1").geom("geom1").feature("ext6").label("outer2 Make Endoneurium");
    model.component("comp1").geom("geom1").feature("ext6").set("contributeto", "csel19");
    model.component("comp1").geom("geom1").feature("ext6").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext6").selection("input").named("csel18");

    model.component("comp1").physics("ec").create("ci3", "ContactImpedance", 2);
    model.component("comp1").physics("ec").feature("ci3").label("outer2 ContactImpedance");
    model.component("comp1").physics("ec").feature("ci3").selection().named("geom1_csel19_bnd");
    model.component("comp1").physics("ec").feature("ci3").set("spec_type", "surfimp");
    model.component("comp1").physics("ec").feature("ci3").set("rhos", "rho_peri*0.03*2*sqrt(outer2_area/pi)");

    model.component("comp1").geom("geom1").selection().create("csel21", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel21").label("outer3_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel22", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel22").label("outer3_ENDONEURIUM");

    model.param()
         .set("outer3_area", "34405.46821862812[um^2]", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/3/inners/0.txt");

    model.component("comp1").geom("geom1").create("wp7", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp7").label("outer3 Inner Geometry");
    model.component("comp1").geom("geom1").feature("wp7").set("contributeto", "csel21");
    model.component("comp1").geom("geom1").feature("wp7").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp7").geom().selection().create("csel23", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp7").geom().selection("csel23").label("outer3_IC");
    model.component("comp1").geom("geom1").feature("wp7").geom().create("ic7", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp7").geom().feature("ic7").label("outer3 Inner Trace 0");
    model.component("comp1").geom("geom1").feature("wp7").geom().feature("ic7").set("contributeto", "csel23");
    model.component("comp1").geom("geom1").feature("wp7").geom().feature("ic7").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp7").geom().feature("ic7")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/3/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp7").geom().feature("ic7").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp7").geom().create("csol7", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp7").geom().feature("csol7").label("outer3 Inner Surface 0");
    model.component("comp1").geom("geom1").feature("wp7").geom().feature("csol7").selection("input").named("csel23");
    model.component("comp1").geom("geom1").create("ext7", "Extrude");
    model.component("comp1").geom("geom1").feature("ext7").label("outer3 Make Endoneurium");
    model.component("comp1").geom("geom1").feature("ext7").set("contributeto", "csel22");
    model.component("comp1").geom("geom1").feature("ext7").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext7").selection("input").named("csel21");

    model.component("comp1").physics("ec").create("ci4", "ContactImpedance", 2);
    model.component("comp1").physics("ec").feature("ci4").label("outer3 ContactImpedance");
    model.component("comp1").physics("ec").feature("ci4").selection().named("geom1_csel22_bnd");
    model.component("comp1").physics("ec").feature("ci4").set("spec_type", "surfimp");
    model.component("comp1").physics("ec").feature("ci4").set("rhos", "rho_peri*0.03*2*sqrt(outer3_area/pi)");

    model.component("comp1").geom("geom1").selection().create("csel24", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel24").label("outer4_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel25", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel25").label("outer4_ENDONEURIUM");

    model.param()
         .set("outer4_area", "65718.73650457627[um^2]", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/4/inners/0.txt");

    model.component("comp1").geom("geom1").create("wp8", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp8").label("outer4 Inner Geometry");
    model.component("comp1").geom("geom1").feature("wp8").set("contributeto", "csel24");
    model.component("comp1").geom("geom1").feature("wp8").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp8").geom().selection().create("csel26", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp8").geom().selection("csel26").label("outer4_IC");
    model.component("comp1").geom("geom1").feature("wp8").geom().create("ic8", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp8").geom().feature("ic8").label("outer4 Inner Trace 0");
    model.component("comp1").geom("geom1").feature("wp8").geom().feature("ic8").set("contributeto", "csel26");
    model.component("comp1").geom("geom1").feature("wp8").geom().feature("ic8").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp8").geom().feature("ic8")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/4/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp8").geom().feature("ic8").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp8").geom().create("csol8", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp8").geom().feature("csol8").label("outer4 Inner Surface 0");
    model.component("comp1").geom("geom1").feature("wp8").geom().feature("csol8").selection("input").named("csel26");
    model.component("comp1").geom("geom1").create("ext8", "Extrude");
    model.component("comp1").geom("geom1").feature("ext8").label("outer4 Make Endoneurium");
    model.component("comp1").geom("geom1").feature("ext8").set("contributeto", "csel25");
    model.component("comp1").geom("geom1").feature("ext8").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext8").selection("input").named("csel24");

    model.component("comp1").physics("ec").create("ci5", "ContactImpedance", 2);
    model.component("comp1").physics("ec").feature("ci5").label("outer4 ContactImpedance");
    model.component("comp1").physics("ec").feature("ci5").selection().named("geom1_csel25_bnd");
    model.component("comp1").physics("ec").feature("ci5").set("spec_type", "surfimp");
    model.component("comp1").physics("ec").feature("ci5").set("rhos", "rho_peri*0.03*2*sqrt(outer4_area/pi)");

    model.component("comp1").geom("geom1").selection().create("csel27", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel27").label("outer5_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel28", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel28").label("outer5_ENDONEURIUM");

    model.param()
         .set("outer5_area", "205464.65463220465[um^2]", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/5/inners/0.txt");

    model.component("comp1").geom("geom1").create("wp9", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp9").label("outer5 Inner Geometry");
    model.component("comp1").geom("geom1").feature("wp9").set("contributeto", "csel27");
    model.component("comp1").geom("geom1").feature("wp9").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp9").geom().selection().create("csel29", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp9").geom().selection("csel29").label("outer5_IC");
    model.component("comp1").geom("geom1").feature("wp9").geom().create("ic9", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp9").geom().feature("ic9").label("outer5 Inner Trace 0");
    model.component("comp1").geom("geom1").feature("wp9").geom().feature("ic9").set("contributeto", "csel29");
    model.component("comp1").geom("geom1").feature("wp9").geom().feature("ic9").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp9").geom().feature("ic9")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/5/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp9").geom().feature("ic9").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp9").geom().create("csol9", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp9").geom().feature("csol9").label("outer5 Inner Surface 0");
    model.component("comp1").geom("geom1").feature("wp9").geom().feature("csol9").selection("input").named("csel29");
    model.component("comp1").geom("geom1").create("ext9", "Extrude");
    model.component("comp1").geom("geom1").feature("ext9").label("outer5 Make Endoneurium");
    model.component("comp1").geom("geom1").feature("ext9").set("contributeto", "csel28");
    model.component("comp1").geom("geom1").feature("ext9").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext9").selection("input").named("csel27");

    model.component("comp1").physics("ec").create("ci6", "ContactImpedance", 2);
    model.component("comp1").physics("ec").feature("ci6").label("outer5 ContactImpedance");
    model.component("comp1").physics("ec").feature("ci6").selection().named("geom1_csel28_bnd");
    model.component("comp1").physics("ec").feature("ci6").set("spec_type", "surfimp");
    model.component("comp1").physics("ec").feature("ci6").set("rhos", "rho_peri*0.03*2*sqrt(outer5_area/pi)");

    model.component("comp1").geom("geom1").selection().create("csel30", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel30").label("outer6_INNERS");
    model.component("comp1").geom("geom1").selection().create("csel31", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel31").label("outer6_OUTER");
    model.component("comp1").geom("geom1").selection().create("csel32", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel32").label("outer6_PERINEURIUM");
    model.component("comp1").geom("geom1").selection().create("csel33", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel33").label("outer6_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp10", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp10").set("contributeto", "csel30");
    model.component("comp1").geom("geom1").feature("wp10").set("selresult", true);
    model.component("comp1").geom("geom1").feature("wp10").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp10").label("outer6 Inners Geometry");
    model.component("comp1").geom("geom1").feature("wp10").geom().selection()
         .create("csel34", "CumulativeSelection");

    return model;
  }

  public static Model run3(Model model) {
    model.component("comp1").geom("geom1").feature("wp10").geom().selection("csel34").label("outer6 inners_all");
    model.component("comp1").geom("geom1").feature("wp10").geom().selection()
         .create("csel35", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp10").geom().selection("csel35").label("outer6 IC0");
    model.component("comp1").geom("geom1").feature("wp10").geom().create("ic10", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic10").label("outer6 Inner Trace 0");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic10").set("contributeto", "csel35");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic10").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic10")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/6/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic10").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp10").geom().create("csol10", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("csol10").label("outer6 Inner Surface 0");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("csol10").set("contributeto", "csel34");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("csol10").set("keep", false);
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("csol10").selection("input")
         .named("csel35");
    model.component("comp1").geom("geom1").feature("wp10").geom().selection()
         .create("csel36", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp10").geom().selection("csel36").label("outer6 IC1");
    model.component("comp1").geom("geom1").feature("wp10").geom().create("ic11", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic11").label("outer6 Inner Trace 1");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic11").set("contributeto", "csel36");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic11").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic11")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/6/inners/1.txt");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("ic11").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp10").geom().create("csol11", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("csol11").label("outer6 Inner Surface 1");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("csol11").set("contributeto", "csel34");
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("csol11").set("keep", false);
    model.component("comp1").geom("geom1").feature("wp10").geom().feature("csol11").selection("input")
         .named("csel36");
    model.component("comp1").geom("geom1").create("wp11", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp11").label("outer6 Outer Geometry");
    model.component("comp1").geom("geom1").feature("wp11").set("contributeto", "csel31");
    model.component("comp1").geom("geom1").feature("wp11").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp11").geom().selection()
         .create("csel37", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp11").geom().selection("csel37").label("outer6 OC");
    model.component("comp1").geom("geom1").feature("wp11").geom().selection()
         .create("csel38", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp11").geom().selection("csel38").label("outer6 sel");
    model.component("comp1").geom("geom1").feature("wp11").geom().create("ic12", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("ic12").label("outer6 Outer Trace");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("ic12").set("contributeto", "csel37");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("ic12").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("ic12")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/6/outer/0.txt");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("ic12").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp11").geom().create("csol12", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("csol12").set("keep", false);
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("csol12").selection("input")
         .named("csel37");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("csol12").set("contributeto", "csel38");
    model.component("comp1").geom("geom1").feature("wp11").geom().feature("csol12").label("outer6 Outer Surface");
    model.component("comp1").geom("geom1").create("ext10", "Extrude");
    model.component("comp1").geom("geom1").feature("ext10").label("outer6 Make Perineurium");
    model.component("comp1").geom("geom1").feature("ext10").set("contributeto", "csel32");
    model.component("comp1").geom("geom1").feature("ext10").set("workplane", "wp11");
    model.component("comp1").geom("geom1").feature("ext10").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext10").selection("input").named("csel31");
    model.component("comp1").geom("geom1").create("ext11", "Extrude");
    model.component("comp1").geom("geom1").feature("ext11").label("outer6 Make Endoneurium");
    model.component("comp1").geom("geom1").feature("ext11").set("contributeto", "csel33");
    model.component("comp1").geom("geom1").feature("ext11").set("workplane", "wp10");
    model.component("comp1").geom("geom1").feature("ext11").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext11").selection("input").named("csel30");
    model.component("comp1").geom("geom1").selection().create("csel39", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel39").label("outer7_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel40", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel40").label("outer7_ENDONEURIUM");

    model.param()
         .set("outer7_area", "23526.70776143062[um^2]", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/7/inners/0.txt");

    model.component("comp1").geom("geom1").create("wp12", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp12").label("outer7 Inner Geometry");
    model.component("comp1").geom("geom1").feature("wp12").set("contributeto", "csel39");
    model.component("comp1").geom("geom1").feature("wp12").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp12").geom().selection()
         .create("csel41", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp12").geom().selection("csel41").label("outer7_IC");
    model.component("comp1").geom("geom1").feature("wp12").geom().create("ic13", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp12").geom().feature("ic13").label("outer7 Inner Trace 0");
    model.component("comp1").geom("geom1").feature("wp12").geom().feature("ic13").set("contributeto", "csel41");
    model.component("comp1").geom("geom1").feature("wp12").geom().feature("ic13").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp12").geom().feature("ic13")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/7/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp12").geom().feature("ic13").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp12").geom().create("csol13", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp12").geom().feature("csol13").label("outer7 Inner Surface 0");
    model.component("comp1").geom("geom1").feature("wp12").geom().feature("csol13").selection("input")
         .named("csel41");
    model.component("comp1").geom("geom1").create("ext12", "Extrude");
    model.component("comp1").geom("geom1").feature("ext12").label("outer7 Make Endoneurium");
    model.component("comp1").geom("geom1").feature("ext12").set("contributeto", "csel40");
    model.component("comp1").geom("geom1").feature("ext12").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext12").selection("input").named("csel39");

    model.component("comp1").physics("ec").create("ci7", "ContactImpedance", 2);
    model.component("comp1").physics("ec").feature("ci7").label("outer7 ContactImpedance");
    model.component("comp1").physics("ec").feature("ci7").selection().named("geom1_csel40_bnd");
    model.component("comp1").physics("ec").feature("ci7").set("spec_type", "surfimp");
    model.component("comp1").physics("ec").feature("ci7").set("rhos", "rho_peri*0.03*2*sqrt(outer7_area/pi)");

    model.component("comp1").geom("geom1").selection().create("csel42", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel42").label("outer8_INNERS_CI");
    model.component("comp1").geom("geom1").selection().create("csel43", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel43").label("outer8_ENDONEURIUM");

    model.param()
         .set("outer8_area", "34598.116647553456[um^2]", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/8/inners/0.txt");

    model.component("comp1").geom("geom1").create("wp13", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp13").label("outer8 Inner Geometry");
    model.component("comp1").geom("geom1").feature("wp13").set("contributeto", "csel42");
    model.component("comp1").geom("geom1").feature("wp13").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp13").geom().selection()
         .create("csel44", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp13").geom().selection("csel44").label("outer8_IC");
    model.component("comp1").geom("geom1").feature("wp13").geom().create("ic14", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp13").geom().feature("ic14").label("outer8 Inner Trace 0");
    model.component("comp1").geom("geom1").feature("wp13").geom().feature("ic14").set("contributeto", "csel44");
    model.component("comp1").geom("geom1").feature("wp13").geom().feature("ic14").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp13").geom().feature("ic14")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/8/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp13").geom().feature("ic14").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp13").geom().create("csol14", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp13").geom().feature("csol14").label("outer8 Inner Surface 0");
    model.component("comp1").geom("geom1").feature("wp13").geom().feature("csol14").selection("input")
         .named("csel44");
    model.component("comp1").geom("geom1").create("ext13", "Extrude");
    model.component("comp1").geom("geom1").feature("ext13").label("outer8 Make Endoneurium");
    model.component("comp1").geom("geom1").feature("ext13").set("contributeto", "csel43");
    model.component("comp1").geom("geom1").feature("ext13").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext13").selection("input").named("csel42");

    model.component("comp1").physics("ec").create("ci8", "ContactImpedance", 2);
    model.component("comp1").physics("ec").feature("ci8").label("outer8 ContactImpedance");
    model.component("comp1").physics("ec").feature("ci8").selection().named("geom1_csel43_bnd");
    model.component("comp1").physics("ec").feature("ci8").set("spec_type", "surfimp");
    model.component("comp1").physics("ec").feature("ci8").set("rhos", "rho_peri*0.03*2*sqrt(outer8_area/pi)");

    model.component("comp1").geom("geom1").selection().create("csel45", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel45").label("outer9_INNERS");
    model.component("comp1").geom("geom1").selection().create("csel46", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel46").label("outer9_OUTER");
    model.component("comp1").geom("geom1").selection().create("csel47", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel47").label("outer9_PERINEURIUM");
    model.component("comp1").geom("geom1").selection().create("csel48", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel48").label("outer9_ENDONEURIUM");
    model.component("comp1").geom("geom1").create("wp14", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp14").set("contributeto", "csel45");
    model.component("comp1").geom("geom1").feature("wp14").set("selresult", true);
    model.component("comp1").geom("geom1").feature("wp14").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp14").label("outer9 Inners Geometry");
    model.component("comp1").geom("geom1").feature("wp14").geom().selection()
         .create("csel49", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp14").geom().selection("csel49").label("outer9 inners_all");
    model.component("comp1").geom("geom1").feature("wp14").geom().selection()
         .create("csel50", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp14").geom().selection("csel50").label("outer9 IC0");
    model.component("comp1").geom("geom1").feature("wp14").geom().create("ic15", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic15").label("outer9 Inner Trace 0");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic15").set("contributeto", "csel50");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic15").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic15")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/9/inners/0.txt");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic15").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp14").geom().create("csol15", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("csol15").label("outer9 Inner Surface 0");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("csol15").set("contributeto", "csel49");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("csol15").set("keep", false);
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("csol15").selection("input")
         .named("csel50");
    model.component("comp1").geom("geom1").feature("wp14").geom().selection()
         .create("csel51", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp14").geom().selection("csel51").label("outer9 IC1");
    model.component("comp1").geom("geom1").feature("wp14").geom().create("ic16", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic16").label("outer9 Inner Trace 1");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic16").set("contributeto", "csel51");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic16").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic16")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/9/inners/1.txt");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic16").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp14").geom().create("csol16", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("csol16").label("outer9 Inner Surface 1");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("csol16").set("contributeto", "csel49");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("csol16").set("keep", false);
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("csol16").selection("input")
         .named("csel51");
    model.component("comp1").geom("geom1").feature("wp14").geom().selection()
         .create("csel52", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp14").geom().selection("csel52").label("outer9 IC2");
    model.component("comp1").geom("geom1").feature("wp14").geom().create("ic17", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic17").label("outer9 Inner Trace 2");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic17").set("contributeto", "csel52");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic17").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic17")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/9/inners/2.txt");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("ic17").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp14").geom().create("csol17", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("csol17").label("outer9 Inner Surface 2");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("csol17").set("contributeto", "csel49");
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("csol17").set("keep", false);
    model.component("comp1").geom("geom1").feature("wp14").geom().feature("csol17").selection("input")
         .named("csel52");
    model.component("comp1").geom("geom1").create("wp15", "WorkPlane");
    model.component("comp1").geom("geom1").feature("wp15").label("outer9 Outer Geometry");
    model.component("comp1").geom("geom1").feature("wp15").set("contributeto", "csel46");
    model.component("comp1").geom("geom1").feature("wp15").set("unite", true);
    model.component("comp1").geom("geom1").feature("wp15").geom().selection()
         .create("csel53", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp15").geom().selection("csel53").label("outer9 OC");
    model.component("comp1").geom("geom1").feature("wp15").geom().selection()
         .create("csel54", "CumulativeSelection");
    model.component("comp1").geom("geom1").feature("wp15").geom().selection("csel54").label("outer9 sel");
    model.component("comp1").geom("geom1").feature("wp15").geom().create("ic18", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("ic18").label("outer9 Outer Trace");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("ic18").set("contributeto", "csel53");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("ic18").set("source", "file");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("ic18")
         .set("filename", "D:\\Documents\\access/data/samples/Cadaver50-2/0/0/sectionwise2d/fascicles/9/outer/0.txt");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("ic18").set("rtol", 0.02);
    model.component("comp1").geom("geom1").feature("wp15").geom().create("csol18", "ConvertToSolid");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("csol18").set("keep", false);
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("csol18").selection("input")
         .named("csel53");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("csol18").set("contributeto", "csel54");
    model.component("comp1").geom("geom1").feature("wp15").geom().feature("csol18").label("outer9 Outer Surface");
    model.component("comp1").geom("geom1").create("ext14", "Extrude");
    model.component("comp1").geom("geom1").feature("ext14").label("outer9 Make Perineurium");
    model.component("comp1").geom("geom1").feature("ext14").set("contributeto", "csel47");
    model.component("comp1").geom("geom1").feature("ext14").set("workplane", "wp15");
    model.component("comp1").geom("geom1").feature("ext14").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext14").selection("input").named("csel46");
    model.component("comp1").geom("geom1").create("ext15", "Extrude");
    model.component("comp1").geom("geom1").feature("ext15").label("outer9 Make Endoneurium");
    model.component("comp1").geom("geom1").feature("ext15").set("contributeto", "csel48");
    model.component("comp1").geom("geom1").feature("ext15").set("workplane", "wp14");
    model.component("comp1").geom("geom1").feature("ext15").setIndex("distance", "z_nerve", 0);
    model.component("comp1").geom("geom1").feature("ext15").selection("input").named("csel45");
    model.component("comp1").geom("geom1").create("uni1", "Union");
    model.component("comp1").geom("geom1").feature("uni1").set("keep", true);
    model.component("comp1").geom("geom1").feature("uni1").selection("input")
         .set("ext3", "ext4", "ext5", "ext6", "ext7", "ext8", "ext9", "ext11", "ext12", "ext13", "ext15");
    model.component("comp1").geom("geom1").feature("uni1").label("endoUnion");
    model.component("comp1").geom("geom1").selection().create("csel55", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel55").label("endoUnionCsel");
    model.component("comp1").geom("geom1").feature("uni1").set("contributeto", "csel55");
    model.component("comp1").geom("geom1").create("uni2", "Union");
    model.component("comp1").geom("geom1").feature("uni2").set("keep", true);
    model.component("comp1").geom("geom1").feature("uni2").selection("input")
         .set("ext1", "ext2", "ext3", "ext4", "ext5", "ext6", "ext7", "ext8", "ext9", "ext10", "ext11", "ext12", "ext13", "ext14", "ext15");
    model.component("comp1").geom("geom1").feature("uni2").label("allNervePartsUnion");
    model.component("comp1").geom("geom1").selection().create("csel56", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel56").label("allNervePartsUnionCsel");
    model.component("comp1").geom("geom1").feature("uni2").set("contributeto", "csel56");
    model.component("comp1").geom("geom1").create("uni3", "Union");
    model.component("comp1").geom("geom1").feature("uni3").set("keep", true);
    model.component("comp1").geom("geom1").feature("uni3").selection("input").set("ext2", "ext10", "ext14");
    model.component("comp1").geom("geom1").feature("uni3").label("periUnion");
    model.component("comp1").geom("geom1").selection().create("csel57", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel57").label("periUnionCsel");
    model.component("comp1").geom("geom1").feature("uni3").set("contributeto", "csel57");

    model.component("comp1").material().create("matlnk8", "Link");
    model.component("comp1").material("matlnk8").selection().named("geom1_csel1_dom");
    model.component("comp1").material("matlnk8").label("epineurium material");
    model.component("comp1").material("matlnk8").set("link", "mat4");
    model.component("comp1").material().create("matlnk9", "Link");
    model.component("comp1").material("matlnk9").selection().named("geom1_csel57_dom");
    model.component("comp1").material("matlnk9").label("perineurium_DC material");
    model.component("comp1").material("matlnk9").set("link", "mat2");
    model.component("comp1").material().create("matlnk10", "Link");
    model.component("comp1").material("matlnk10").selection().named("geom1_csel55_dom");
    model.component("comp1").material("matlnk10").label("endoneurium material");
    model.component("comp1").material("matlnk10").set("link", "mat3");

    model.component("comp1").geom("geom1").run("fin");

    model.component("comp1").mesh("mesh1").create("swe1", "Sweep");
    model.component("comp1").mesh("mesh1").feature("swe1").selection().geom("geom1", 3);
    model.component("comp1").mesh("mesh1").feature("swe1").selection().named("geom1_csel56_dom");
    model.component("comp1").mesh("mesh1").feature("swe1").set("facemethod", "tri");
    model.component("comp1").mesh("mesh1").feature("size").set("hauto", 1);
    model.component("comp1").mesh("mesh1").run("swe1");
    model.component("comp1").mesh("mesh1").create("ftet1", "FreeTet");
    model.component("comp1").mesh("mesh1").feature("ftet1").create("size1", "Size");
    model.component("comp1").mesh("mesh1").feature("ftet1").feature("size1").set("hauto", 1);
    model.component("comp1").mesh("mesh1").run("ftet1");

    model.study().create("std1");
    model.study("std1").setGenConv(true);
    model.study("std1").create("stat", "Stationary");
    model.study("std1").feature("stat").activate("ec", true);

    model.component("comp1").physics("ec").feature("pcs1").set("Qjp", 0.001);
    model.component("comp1").physics("ec").feature("pcs2").set("Qjp", 0.001);

    model.label("parts_test.mph");

    model.sol().create("sol1");
    model.sol("sol1").study("std1");

    model.study("std1").feature("stat").set("notlistsolnum", 1);
    model.study("std1").feature("stat").set("notsolnum", "1");
    model.study("std1").feature("stat").set("listsolnum", 1);
    model.study("std1").feature("stat").set("solnum", "1");

    model.sol("sol1").create("st1", "StudyStep");
    model.sol("sol1").feature("st1").set("study", "std1");
    model.sol("sol1").feature("st1").set("studystep", "stat");
    model.sol("sol1").create("v1", "Variables");
    model.sol("sol1").feature("v1").set("control", "stat");
    model.sol("sol1").create("s1", "Stationary");
    model.sol("sol1").feature("s1").create("fc1", "FullyCoupled");
    model.sol("sol1").feature("s1").create("i1", "Iterative");
    model.sol("sol1").feature("s1").feature("i1").set("linsolver", "cg");
    model.sol("sol1").feature("s1").feature("i1").create("mg1", "Multigrid");
    model.sol("sol1").feature("s1").feature("i1").feature("mg1").set("prefun", "amg");
    model.sol("sol1").feature("s1").feature("fc1").set("linsolver", "i1");
    model.sol("sol1").feature("s1").feature().remove("fcDef");
    model.sol("sol1").attach("std1");

    model.result().create("pg1", "PlotGroup3D");
    model.result("pg1").label("Electric Potential (ec)");
    model.result("pg1").set("frametype", "spatial");
    model.result("pg1").set("data", "dset1");
    model.result("pg1").feature().create("mslc1", "Multislice");
    model.result("pg1").feature("mslc1").set("colortable", "RainbowLight");
    model.result("pg1").feature("mslc1").set("data", "parent");
    model.result().remove("pg1");

    return model;
  }

  public static void main(String[] args) {
    Model model = run();
    model = run2(model);
    run3(model);
  }

}

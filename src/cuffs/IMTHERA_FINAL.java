/*
 * IMTHERA_FINAL.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Aug 20 2019, 16:06 by COMSOL 5.4.0.388. */
public class IMTHERA_FINAL {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model.modelPath("D:\\Documents\\ModularCuffs");

    model.label("IMTHERA_FINAL.mph");

    model.param()
         .set("ang_cuffseam_contactcenter", "ang_cuffseam_contactcenter_pre*(r_cuff_in_pre/r_cuff_in)", "Source: Deriv B-B. Angle from the cuff seam (where the two ends of the inner cuff come together beneath the furl) to the first contacts (1 and 6) in the manufactured state (AFTER deformation/uncoiling).");
    model.param()
         .set("ang_contactcenter_contactcenter_pre", "51 [deg]", "Source: B-B. Angle from contact center to contact center contacts (1 to 2, 2 to 3, 3 to 4, 4 to 5, 5 to 6) in the manufactured state (BEFORE deformation/uncoiling).");
    model.param()
         .set("length_contactcenter_contactcenter", "0.108 [inch]", "Source: Detail A. Length (along the z-direction, the trajectory of the nerve) between contacts (from center to center).");
    model.param()
         .set("z_nerve", "20 [mm]", "Source: Internal. Length of the nerve. This will have to be long enough so that it does not influence the thresholds of the model.");
    model.param()
         .set("r_nerve", "1.6 [mm]", "Source: Internal. Radius of the nerve. This depends on the sample being used.");
    model.param()
         .set("r_cuff_in", "max(r_nerve+thk_medium_gap_internal,r_cuff_in_pre)", "Source: Deriv B-B. Radius of the inner cuff (center to inner surface of the cuff) after deformation (uncoiling of the cuff from contents opening up the cuff).");
    model.param()
         .set("thk_medium_gap_internal", "0 [inch]", "Source: Internal. This parameter can be used to force a medium between the nerve and the inner diameter of the cuff (example would be scar tissue or saline). This volume would need to be able to hold the cuff open to a deformed (uncoiled) state.");
    model.param()
         .set("r_cuff_in_pre", "(0.118/2) [inch]", "Source: B-B. Radius of the inner cuff (center to inner surface of the cuff) as manufactured (before deformation from contents of the cuff being larger than manufactured inner diam)");
    model.param()
         .set("L_cuff", "0.354 [inch]", "Source Detail A. Length of the cuff in the z-direction (path of nerve travel through the cuff).");
    model.param()
         .set("ang_cuffseam_contactcenter_pre", "53 [deg]", "Source: B-B. Angle from the cuff seam (where the two ends of the inner cuff come together beneath the furl) to the first contacts (1 and 6) in the manufactured state (BEFORE deformation/uncoiling).");
    model.param()
         .set("thk_inner_cuff", "r_cuff_out_pre-r_cuff_in_pre", "Source: B-B. Thickness of the inner cuff (not the furl) measured as the difference in radial distance from from the center to the inner and outer diameter of the inner cuff.");
    model.param()
         .set("recess_depth", "0 [inch]", "Source: Jason spreadsheet. If we want to add recessed contacts in the future, make this not 0. This value is the difference in radial distance from the center to the inner diameter of the cuff and face of the electrode.");
    model.param()
         .set("ang_contactcenter_contactcenter", "ang_contactcenter_contactcenter_pre*(r_cuff_in_pre/r_cuff_in)", "Source: Deriv B-B. Angle from contact center to contact center contacts (1 to 2, 2 to 3, 3 to 4, 4 to 5, 5 to 6) in the manufactured state (AFTER deformation/uncoiling).");
    model.param()
         .set("diam_inner_cuff_hole", "0.02 [inch]", "Source: Cable Electrode Diag. Diameter of the hole for silicone suture in the inner cuff.");
    model.param()
         .set("shift_x", "0 [um]", "Source: Internal. Distance in the x-direction to shift the cuff. This would likely be used when moving the nerve within the cuff.");
    model.param()
         .set("shift_y", "0 [um]", "Source: Internal. Distance in the y-direction to shift the cuff. This would likely be used when moving the nerve within the cuff.");
    model.param()
         .set("thk_furl", "r_furl_out_pre-r_furl_in_pre", "Source: B-B. Thickness of the furl (not the inner cuff) measured as the difference in radial distance from from the center to the inner and outer diameter of the furl.");
    model.param()
         .set("thk_gap_cuff_furl", "0 [inch]", "Source: Internal. Thickness of the gap between the outer diameter of the inner cuff and the inner diameter of the furl.");
    model.param()
         .set("theta_cuff", "theta_cuff_pre*(r_cuff_in_pre/r_cuff_in)", "Source: Deriv B-B. Rotational angle of the inner cuff insulator after the cuff has deformed. This preserves the arc length of the material.");
    model.param()
         .set("theta_cuff_pre", "360 [deg]", "Source: B-B. Rotational angle of the inner cuff as manufactured (before deformation/uncoiling).");
    model.param()
         .set("length_furlholecenter_cuffend", "0.077 [inch]", "Source: Cable Electrode Diag. Length from the center of the furls to the end of the cuff (either extend in the nearest z-direction along the trajectory of where the nerve passes).");
    model.param()
         .set("diam_furl_hole", "0.02 [inch]", "Source: Cable Electrode Diag. Diameter of the holes for silicone suture in the furl.");
    model.param()
         .set("length_furlholecenter_cuffseam", "0.03 [inch]", "Source: Cable Electrode Diag. Arc length from the center of the furl hole to the seam of the cuff (where the cuff comes together beneath the furl).");
    model.param()
         .set("b_ellipse_contact", "(r_cuff_in+recess_depth)*cos((pi/2) - 2*pi*(((diam_contact/2) + recess_depth)/(pi*(2*r_cuff_in+2*recess_depth))))", "Source: Internal. To make a bent circle electrode contact, you need the ellipse params for looking at it head-on so that you can extrude the ellipse into a cylinder and cut out a circular electrode face. Pretty cool.");
    model.param()
         .set("diam_contact", "2 [mm]", "Source: Jason spreadsheet. Diameter of the exposed circular contacts in the cuff (in a plane, before deformation to the curvature of the cuff).");
    model.param()
         .set("contact_depth", "0.05 [mm]", "Source: Jason spreadsheet. Depth of the contacts. Parameter made for this, but its value should not influence the steady state solution of the model since the only surface non-insulated is the contact face.");
    model.param()
         .set("length_innerholecenter_cuffseam", "0.03 [inch]", "Source: Jason spreadsheet. Arc length from the center of the inner hole to the seam of the cuff (where the cuff comes together beneath the furl).");
    model.param()
         .set("hole_length_buffer", "150 [um]", "Source: Internal. Parameter used as a building tool - since the cuff has cuvature, must create the cylinders a little long for diffs to cut the holes.");
    model.param()
         .set("theta_furl", "theta_furl_pre*((r_cuff_in_pre+thk_inner_cuff+thk_gap_cuff_furl)/(r_cuff_in+thk_inner_cuff+thk_gap_cuff_furl))", "Source: Deriv B-B. Rotational angle of the furl after deformation.");
    model.param()
         .set("theta_furl_pre", "250 [deg]", "Source: B-B. Rotational angle of the furl as manufactured (without deformation/uncoil from contents of the cuff being larger than 3 mm)");
    model.param().set("r_cuff_out_pre", "(0.178/2) [inch]", "Source: B-B.");
    model.param().set("r_cuff_out", "r_cuff_out_pre*(r_cuff_in_pre/r_cuff_in)", "Source: Deriv B-B.");
    model.param().set("r_furl_out_pre", "(0.218/2) [inch]", "Source: B-B.");
    model.param().set("r_furl_out", "r_cuff_in+thk_inner_cuff+thk_gap_cuff_furl+thk_furl", "Source: Deriv B-B.");
    model.param().set("r_furl_in_pre", "(0.178/2) [inch]", "Source: B-B.");
    model.param().set("r_furl_in", "r_cuff_in+thk_inner_cuff+thk_gap_cuff_furl", "Source: Deriv B-B.");
    model.param().set("thk_saline", "1 [mm]", "Source: Internal.");
    model.param().set("r_ground", "5 [mm]", "Source: Need convergence tests.");
    model.param()
         .set("z_center_cuff", "z_nerve/2", "Source: Internal. Move the cuff along the length of the nerve. This will be changed when using multiple cuffs on the nerves. z_nerve/2 puts the cuff at the center.");
    model.param().set("zw_rot", "0 [deg]", "Source: Internal.");

    model.component().create("comp1", true);

    model.component("comp1").geom().create("geom1", 3);

    model.component("comp1").label("ImThera Cuff");

    model.component("comp1").mesh().create("mesh1");

    model.geom().create("part1", "Part", 3);
    model.geom().create("part3", "Part", 3);
    model.geom().create("part2", "Part", 3);
    model.geom().create("part4", "Part", 3);
    model.geom().create("part5", "Part", 3);
    model.geom("part1").label("ImThera - Inner Cuff");
    model.geom("part1").lengthUnit("\u00b5m");
    model.geom("part1").inputParam().set("z_center", "0");
    model.geom("part1").selection().create("csel1", "CumulativeSelection");
    model.geom("part1").selection("csel1").label("INNER CUFF SURFACE");
    model.geom("part1").selection().create("csel2", "CumulativeSelection");
    model.geom("part1").selection("csel2").label("OUTER CUFF SURFACE");
    model.geom("part1").selection().create("csel3", "CumulativeSelection");
    model.geom("part1").selection("csel3").label("INNER CUFF PRE CUT GAP");
    model.geom("part1").selection().create("csel4", "CumulativeSelection");
    model.geom("part1").selection("csel4").label("INNER CUFF CUT CROSS SECTION");
    model.geom("part1").selection().create("csel5", "CumulativeSelection");
    model.geom("part1").selection("csel5").label("INNER CUFF CUT");
    model.geom("part1").selection().create("csel6", "CumulativeSelection");
    model.geom("part1").selection("csel6").label("INNER CUFF GAP CUT CROSS SECTION");
    model.geom("part1").selection().create("csel7", "CumulativeSelection");
    model.geom("part1").selection("csel7").label("INNER HOLE");
    model.geom("part1").selection().create("csel8", "CumulativeSelection");
    model.geom("part1").selection("csel8").label("INNER CUFF");
    model.geom("part1").selection().create("csel9", "CumulativeSelection");
    model.geom("part1").selection("csel9").label("INNER CUFF FINAL");
    model.geom("part1").create("cyl1", "Cylinder");
    model.geom("part1").feature("cyl1").label("Inner Cuff Surface");
    model.geom("part1").feature("cyl1").set("contributeto", "csel1");
    model.geom("part1").feature("cyl1").set("pos", new String[]{"0", "0", "z_center-(L_cuff/2)"});
    model.geom("part1").feature("cyl1").set("r", "r_cuff_in");
    model.geom("part1").feature("cyl1").set("h", "L_cuff");
    model.geom("part1").create("cyl2", "Cylinder");
    model.geom("part1").feature("cyl2").label("Outer Cuff Surface");
    model.geom("part1").feature("cyl2").set("contributeto", "csel2");
    model.geom("part1").feature("cyl2").set("pos", new String[]{"0", "0", "z_center-(L_cuff/2)"});
    model.geom("part1").feature("cyl2").set("r", "r_cuff_in+thk_inner_cuff");
    model.geom("part1").feature("cyl2").set("h", "L_cuff");
    model.geom("part1").create("dif1", "Difference");
    model.geom("part1").feature("dif1").label("Inner Cuff Pre Cut Gap");
    model.geom("part1").feature("dif1").set("contributeto", "csel3");
    model.geom("part1").feature("dif1").selection("input").named("csel2");
    model.geom("part1").feature("dif1").selection("input2").named("csel1");
    model.geom("part1").create("if1", "If");
    model.geom("part1").feature("if1").set("condition", "theta_cuff<theta_cuff_pre");
    model.geom("part1").create("wp1", "WorkPlane");
    model.geom("part1").feature("wp1").label("Inner Cuff Gap Cut Cross Section");
    model.geom("part1").feature("wp1").set("contributeto", "csel6");
    model.geom("part1").feature("wp1").set("quickplane", "xz");
    model.geom("part1").feature("wp1").set("unite", true);
    model.geom("part1").feature("wp1").geom().create("r1", "Rectangle");
    model.geom("part1").feature("wp1").geom().feature("r1").label("Inner Cuff Gap Cut Cross Section");
    model.geom("part1").feature("wp1").geom().feature("r1")
         .set("pos", new String[]{"r_cuff_in+(thk_inner_cuff/2)", "z_center"});
    model.geom("part1").feature("wp1").geom().feature("r1").set("base", "center");
    model.geom("part1").feature("wp1").geom().feature("r1").set("size", new String[]{"thk_inner_cuff", "L_cuff"});
    model.geom("part1").create("rev1", "Revolve");
    model.geom("part1").feature("rev1").label("Inner Cuff Cut");
    model.geom("part1").feature("rev1").set("contributeto", "csel5");
    model.geom("part1").feature("rev1").set("angle1", "theta_cuff");
    model.geom("part1").feature("rev1").selection("input").set("wp1");
    model.geom("part1").create("dif2", "Difference");
    model.geom("part1").feature("dif2").label("Remove Inner Cuff Gap");
    model.geom("part1").feature("dif2").set("contributeto", "csel8");
    model.geom("part1").feature("dif2").selection("input").named("csel3");
    model.geom("part1").feature("dif2").selection("input2").named("csel5");
    model.geom("part1").create("econ2", "ECone");
    model.geom("part1").feature("econ2").label("Inner Cuff Hole Cutter 1");
    model.geom("part1").feature("econ2").set("contributeto", "csel7");
    model.geom("part1").feature("econ2").set("pos", new String[]{"r_cuff_in-hole_length_buffer/2", "0", "z_center"});
    model.geom("part1").feature("econ2").set("axis", new int[]{1, 0, 0});
    model.geom("part1").feature("econ2")
         .set("semiaxes", new String[]{"diam_inner_cuff_hole/2", "diam_inner_cuff_hole/2"});
    model.geom("part1").feature("econ2").set("h", "thk_inner_cuff+hole_length_buffer");
    model.geom("part1").feature("econ2").set("rat", "r_cuff_out/r_cuff_in");
    model.geom("part1").create("rot2", "Rotate");
    model.geom("part1").feature("rot2").label("Position Inner Hole 1");
    model.geom("part1").feature("rot2").set("rot", "(360*length_innerholecenter_cuffseam)/(pi*2*r_cuff_in)");
    model.geom("part1").feature("rot2").selection("input").named("csel7");
    model.geom("part1").create("dif4", "Difference");
    model.geom("part1").feature("dif4").label("Punch Inner Cuff Hole 1");
    model.geom("part1").feature("dif4").set("contributeto", "csel9");
    model.geom("part1").feature("dif4").selection("input").named("csel8");
    model.geom("part1").feature("dif4").selection("input2").named("csel7");
    model.geom("part1").create("endif1", "EndIf");
    model.geom("part1").create("if2", "If");
    model.geom("part1").feature("if2").set("condition", "theta_cuff>=theta_cuff_pre");
    model.geom("part1").create("econ1", "ECone");
    model.geom("part1").feature("econ1").label("Inner Cuff Hole Cutter");
    model.geom("part1").feature("econ1").set("contributeto", "csel7");
    model.geom("part1").feature("econ1").set("pos", new String[]{"r_cuff_in-hole_length_buffer/2", "0", "z_center"});
    model.geom("part1").feature("econ1").set("axis", new int[]{1, 0, 0});
    model.geom("part1").feature("econ1")
         .set("semiaxes", new String[]{"diam_inner_cuff_hole/2", "diam_inner_cuff_hole/2"});
    model.geom("part1").feature("econ1").set("h", "thk_inner_cuff+hole_length_buffer");
    model.geom("part1").feature("econ1").set("rat", "r_cuff_out/r_cuff_in");
    model.geom("part1").create("rot1", "Rotate");
    model.geom("part1").feature("rot1").label("Position Inner Hole");
    model.geom("part1").feature("rot1").set("rot", "(360*length_innerholecenter_cuffseam)/(pi*2*r_cuff_in)");
    model.geom("part1").feature("rot1").selection("input").named("csel7");
    model.geom("part1").create("dif3", "Difference");
    model.geom("part1").feature("dif3").label("Punch Inner Cuff Hole");
    model.geom("part1").feature("dif3").set("contributeto", "csel9");
    model.geom("part1").feature("dif3").selection("input").named("csel3");
    model.geom("part1").feature("dif3").selection("input2").named("csel7");
    model.geom("part1").create("endif2", "EndIf");
    model.geom("part1").run();
    model.geom("part3").label("ImThera - Furl");
    model.geom("part3").lengthUnit("\u00b5m");
    model.geom("part3").inputParam().set("z_center", "0");
    model.geom("part3").selection().create("csel1", "CumulativeSelection");
    model.geom("part3").selection("csel1").label("INNER FURL SURFACE");
    model.geom("part3").selection().create("csel2", "CumulativeSelection");
    model.geom("part3").selection("csel2").label("OUTER FURL SURFACE");
    model.geom("part3").selection().create("csel3", "CumulativeSelection");
    model.geom("part3").selection("csel3").label("FURL GAP CUT CROSS SECTION");
    model.geom("part3").selection().create("csel4", "CumulativeSelection");
    model.geom("part3").selection("csel4").label("FURL CUT");
    model.geom("part3").selection().create("csel5", "CumulativeSelection");
    model.geom("part3").selection("csel5").label("FURL PRE CUT GAP");
    model.geom("part3").selection().create("csel6", "CumulativeSelection");
    model.geom("part3").selection("csel6").label("FURL HOLES");
    model.geom("part3").selection().create("csel7", "CumulativeSelection");
    model.geom("part3").selection("csel7").label("FURL PRE HOLES");
    model.geom("part3").selection().create("csel8", "CumulativeSelection");
    model.geom("part3").selection("csel8").label("FURL FINAL");
    model.geom("part3").create("cyl1", "Cylinder");
    model.geom("part3").feature("cyl1").label("Inner Furl Surface");
    model.geom("part3").feature("cyl1").set("contributeto", "csel1");
    model.geom("part3").feature("cyl1").set("pos", new String[]{"0", "0", "z_center-(L_cuff/2)"});
    model.geom("part3").feature("cyl1").set("r", "r_cuff_in+thk_inner_cuff+thk_gap_cuff_furl");
    model.geom("part3").feature("cyl1").set("h", "L_cuff");
    model.geom("part3").create("cyl2", "Cylinder");
    model.geom("part3").feature("cyl2").label("Outer Furl Surface");
    model.geom("part3").feature("cyl2").set("contributeto", "csel2");
    model.geom("part3").feature("cyl2").set("pos", new String[]{"0", "0", "z_center-(L_cuff/2)"});
    model.geom("part3").feature("cyl2").set("r", "r_cuff_in+thk_inner_cuff+thk_gap_cuff_furl+thk_furl");
    model.geom("part3").feature("cyl2").set("h", "L_cuff");
    model.geom("part3").create("dif1", "Difference");
    model.geom("part3").feature("dif1").label("Furl Pre Cut Gap");
    model.geom("part3").feature("dif1").set("contributeto", "csel5");
    model.geom("part3").feature("dif1").selection("input").named("csel2");
    model.geom("part3").feature("dif1").selection("input2").named("csel1");
    model.geom("part3").create("wp1", "WorkPlane");
    model.geom("part3").feature("wp1").label("Furl Gap Cut Cross Section");
    model.geom("part3").feature("wp1").set("contributeto", "csel3");
    model.geom("part3").feature("wp1").set("quickplane", "xz");
    model.geom("part3").feature("wp1").set("unite", true);
    model.geom("part3").feature("wp1").geom().create("r1", "Rectangle");
    model.geom("part3").feature("wp1").geom().feature("r1").label("Furl Gap Cut Cross Section");
    model.geom("part3").feature("wp1").geom().feature("r1")
         .set("pos", new String[]{"r_cuff_in+thk_inner_cuff+thk_gap_cuff_furl+(thk_furl/2)", "z_center"});
    model.geom("part3").feature("wp1").geom().feature("r1").set("base", "center");
    model.geom("part3").feature("wp1").geom().feature("r1").set("size", new String[]{"thk_furl", "L_cuff"});
    model.geom("part3").create("rev1", "Revolve");
    model.geom("part3").feature("rev1").set("contributeto", "csel4");
    model.geom("part3").feature("rev1").set("angle1", "(-(360-theta_cuff)/2)-(theta_furl/2)");
    model.geom("part3").feature("rev1").set("angle2", "(-(360-theta_cuff)/2)-(theta_furl/2)-(360-theta_furl)");
    model.geom("part3").feature("rev1").selection("input").set("wp1");
    model.geom("part3").create("dif2", "Difference");
    model.geom("part3").feature("dif2").set("contributeto", "csel7");
    model.geom("part3").feature("dif2").selection("input").named("csel5");
    model.geom("part3").feature("dif2").selection("input2").named("csel4");
    model.geom("part3").create("econ1", "ECone");
    model.geom("part3").feature("econ1").label("Furl Hole 1");
    model.geom("part3").feature("econ1").set("contributeto", "csel6");
    model.geom("part3").feature("econ1")
         .set("pos", new String[]{"r_cuff_in+thk_inner_cuff+thk_gap_cuff_furl-hole_length_buffer/2", "0", "z_center-((L_cuff/2)-length_furlholecenter_cuffend)"});
    model.geom("part3").feature("econ1").set("axis", new int[]{1, 0, 0});
    model.geom("part3").feature("econ1").set("semiaxes", new String[]{"diam_furl_hole/2", "diam_furl_hole/2"});
    model.geom("part3").feature("econ1").set("h", "thk_furl+hole_length_buffer");
    model.geom("part3").feature("econ1").set("rat", "r_furl_out/r_furl_in");
    model.geom("part3").create("econ2", "ECone");
    model.geom("part3").feature("econ2").label("Furl Hole 2");
    model.geom("part3").feature("econ2").set("contributeto", "csel6");
    model.geom("part3").feature("econ2")
         .set("pos", new String[]{"r_cuff_in+thk_inner_cuff+thk_gap_cuff_furl-hole_length_buffer/2", "0", "z_center+((L_cuff/2)-length_furlholecenter_cuffend)"});
    model.geom("part3").feature("econ2").set("axis", new int[]{1, 0, 0});
    model.geom("part3").feature("econ2").set("semiaxes", new String[]{"diam_furl_hole/2", "diam_furl_hole/2"});
    model.geom("part3").feature("econ2").set("h", "thk_furl+hole_length_buffer");
    model.geom("part3").feature("econ2").set("rat", "r_furl_out/r_furl_in");
    model.geom("part3").create("rot1", "Rotate");
    model.geom("part3").feature("rot1").label("Position Furl Holes");
    model.geom("part3").feature("rot1")
         .set("rot", "(((theta_cuff-360)/2) + (theta_furl/2) - (length_furlholecenter_cuffseam*360)/(2*pi*(r_cuff_in+thk_inner_cuff+thk_gap_cuff_furl)))");
    model.geom("part3").feature("rot1").selection("input").named("csel6");
    model.geom("part3").create("dif3", "Difference");
    model.geom("part3").feature("dif3").label("Punch Furl Holes");
    model.geom("part3").feature("dif3").set("contributeto", "csel8");
    model.geom("part3").feature("dif3").selection("input").named("csel7");
    model.geom("part3").feature("dif3").selection("input2").named("csel6");
    model.geom("part3").run();
    model.geom("part2").label("ImThera - Recessed Contact (Circle if Flat)");
    model.geom("part2").lengthUnit("\u00b5m");
    model.geom("part2").inputParam().set("rotation_angle", "0 [deg]");
    model.geom("part2").inputParam().set("z_src", "0");
    model.geom("part2").selection().create("csel1", "CumulativeSelection");
    model.geom("part2").selection("csel1").label("BASE CONTACT PLANE (PRE ROTATION)");
    model.geom("part2").selection().create("csel2", "CumulativeSelection");
    model.geom("part2").selection("csel2").label("PLANE FOR RECESS");
    model.geom("part2").selection().create("csel3", "CumulativeSelection");
    model.geom("part2").selection("csel3").label("RECESS");
    model.geom("part2").selection().create("csel11", "CumulativeSelection");
    model.geom("part2").selection("csel11").label("SRC");
    model.geom("part2").selection().create("csel4", "CumulativeSelection");
    model.geom("part2").selection("csel4").label("RECESS CUTTER");
    model.geom("part2").selection().create("csel10", "CumulativeSelection");
    model.geom("part2").selection("csel10").label("CONTACT FINAL");
    model.geom("part2").selection().create("csel5", "CumulativeSelection");
    model.geom("part2").selection("csel5").label("PRE CUT RECESS");
    model.geom("part2").selection().create("csel6", "CumulativeSelection");
    model.geom("part2").selection("csel6").label("PLANE FOR CONTACT");
    model.geom("part2").selection().create("csel7", "CumulativeSelection");
    model.geom("part2").selection("csel7").label("PRE CUT CONTACT");
    model.geom("part2").selection().create("csel8", "CumulativeSelection");
    model.geom("part2").selection("csel8").label("CONTACT CUT");
    model.geom("part2").selection().create("csel9", "CumulativeSelection");
    model.geom("part2").selection("csel9").label("CONTACT CUTTER");
    model.geom("part2").selection().create("csel12", "CumulativeSelection");
    model.geom("part2").selection("csel12").label("RECESS FINAL");
    model.geom("part2").create("wp1", "WorkPlane");
    model.geom("part2").feature("wp1").label("base plane (pre rotation)");
    model.geom("part2").feature("wp1").set("contributeto", "csel1");
    model.geom("part2").feature("wp1").set("quickplane", "yz");
    model.geom("part2").feature("wp1").set("unite", true);
    model.geom("part2").create("wp2", "WorkPlane");
    model.geom("part2").feature("wp2").label("rotated plane for recess");
    model.geom("part2").feature("wp2").set("contributeto", "csel2");
    model.geom("part2").feature("wp2").set("planetype", "transformed");
    model.geom("part2").feature("wp2").set("workplane", "wp1");
    model.geom("part2").feature("wp2").set("transaxis", new int[]{0, 1, 0});
    model.geom("part2").feature("wp2").set("transrot", "rotation_angle");
    model.geom("part2").feature("wp2").set("unite", true);
    model.geom("part2").feature("wp2").geom().selection().create("csel1", "CumulativeSelection");
    model.geom("part2").feature("wp2").geom().selection("csel1").label("CONTACT OUTLINE SHAPE");
    model.geom("part2").feature("wp2").geom().create("e1", "Ellipse");
    model.geom("part2").feature("wp2").geom().feature("e1").label("Contact Outline");
    model.geom("part2").feature("wp2").geom().feature("e1").set("contributeto", "csel1");
    model.geom("part2").feature("wp2").geom().feature("e1").set("pos", new String[]{"0", "z_src"});
    model.geom("part2").feature("wp2").geom().feature("e1")
         .set("semiaxes", new String[]{"diam_contact/2", "b_ellipse_contact"});
    model.geom("part2").create("ext1", "Extrude");
    model.geom("part2").feature("ext1").label("Make Pre Cut Recess Domains");
    model.geom("part2").feature("ext1").set("contributeto", "csel5");
    model.geom("part2").feature("ext1").setIndex("distance", "r_cuff_in+recess_depth+contact_depth", 0);
    model.geom("part2").feature("ext1").selection("input").named("csel2");
    model.geom("part2").create("cyl1", "Cylinder");
    model.geom("part2").feature("cyl1").label("Recess Cut");
    model.geom("part2").feature("cyl1").set("contributeto", "csel4");
    model.geom("part2").feature("cyl1").set("pos", new String[]{"0", "0", "z_src-L_cuff/2"});
    model.geom("part2").feature("cyl1").set("r", "r_cuff_in");
    model.geom("part2").feature("cyl1").set("h", "L_cuff");
    model.geom("part2").create("dif1", "Difference");
    model.geom("part2").feature("dif1").label("Make Recess");
    model.geom("part2").feature("dif1").set("contributeto", "csel12");
    model.geom("part2").feature("dif1").selection("input").named("csel5");
    model.geom("part2").feature("dif1").selection("input2").named("csel4");
    model.geom("part2").create("wp3", "WorkPlane");
    model.geom("part2").feature("wp3").label("Rotated Plane for Contact");
    model.geom("part2").feature("wp3").set("contributeto", "csel6");
    model.geom("part2").feature("wp3").set("planetype", "transformed");
    model.geom("part2").feature("wp3").set("workplane", "wp1");
    model.geom("part2").feature("wp3").set("transaxis", new int[]{0, 1, 0});
    model.geom("part2").feature("wp3").set("transrot", "rotation_angle");
    model.geom("part2").feature("wp3").set("unite", true);
    model.geom("part2").feature("wp3").geom().selection().create("csel1", "CumulativeSelection");
    model.geom("part2").feature("wp3").geom().selection("csel1").label("CONTACT OUTLINE SHAPE");
    model.geom("part2").feature("wp3").geom().create("e1", "Ellipse");
    model.geom("part2").feature("wp3").geom().feature("e1").label("Contact Outline");
    model.geom("part2").feature("wp3").geom().feature("e1").set("contributeto", "csel1");
    model.geom("part2").feature("wp3").geom().feature("e1").set("pos", new String[]{"0", "z_src"});
    model.geom("part2").feature("wp3").geom().feature("e1")
         .set("semiaxes", new String[]{"diam_contact/2", "b_ellipse_contact"});
    model.geom("part2").create("ext2", "Extrude");
    model.geom("part2").feature("ext2").label("Make Contact Domain");
    model.geom("part2").feature("ext2").set("contributeto", "csel7");
    model.geom("part2").feature("ext2").setIndex("distance", "r_cuff_in+recess_depth+contact_depth", 0);
    model.geom("part2").feature("ext2").selection("input").named("csel6");
    model.geom("part2").create("cyl2", "Cylinder");
    model.geom("part2").feature("cyl2").label("Contact Cut");
    model.geom("part2").feature("cyl2").set("contributeto", "csel9");
    model.geom("part2").feature("cyl2").set("pos", new String[]{"0", "0", "z_src-L_cuff/2"});
    model.geom("part2").feature("cyl2").set("r", "r_cuff_in+recess_depth");
    model.geom("part2").feature("cyl2").set("h", "L_cuff");
    model.geom("part2").create("dif2", "Difference");
    model.geom("part2").feature("dif2").label("Make Contact");
    model.geom("part2").feature("dif2").set("contributeto", "csel10");
    model.geom("part2").feature("dif2").selection("input").named("csel7");
    model.geom("part2").feature("dif2").selection("input2").named("csel9");
    model.geom("part2").create("pt1", "Point");
    model.geom("part2").feature("pt1").label("src");
    model.geom("part2").feature("pt1").set("contributeto", "csel11");
    model.geom("part2").feature("pt1")
         .set("p", new String[]{"(r_cuff_in+recess_depth+contact_depth/2)*cos(rotation_angle)", "(r_cuff_in+recess_depth+contact_depth/2)*sin(rotation_angle)", "z_src"});
    model.geom("part2").run();
    model.geom("part4").label("Cuff Fill");
    model.geom("part4").selection().create("csel1", "CumulativeSelection");
    model.geom("part4").selection("csel1").label("SALINE FILL");
    model.geom("part4").selection().create("csel2", "CumulativeSelection");
    model.geom("part4").selection("csel2").label("CUFF FILL");
    model.geom("part4").create("cyl1", "Cylinder");
    model.geom("part4").feature("cyl1").label("Cuff Fill");
    model.geom("part4").feature("cyl1").set("contributeto", "csel2");
    model.geom("part4").feature("cyl1").set("pos", new String[]{"0", "0", "z_center_cuff-(L_cuff/2)-thk_saline"});
    model.geom("part4").feature("cyl1").set("r", "r_cuff_in+thk_inner_cuff+thk_gap_cuff_furl+thk_furl+thk_saline");
    model.geom("part4").feature("cyl1").set("h", "L_cuff+2*thk_saline");
    model.geom("part4").run();
    model.geom("part5").label("Distant Ground");
    model.geom("part5").lengthUnit("\u00b5m");
    model.geom("part5").selection().create("csel1", "CumulativeSelection");
    model.geom("part5").selection("csel1").label("DISTANT GROUND");
    model.geom("part5").create("cyl1", "Cylinder");
    model.geom("part5").feature("cyl1").set("contributeto", "csel1");
    model.geom("part5").feature("cyl1").set("pos", new int[]{0, 0, 0});
    model.geom("part5").feature("cyl1").set("r", "r_ground");
    model.geom("part5").feature("cyl1").set("h", "z_nerve");
    model.geom("part5").run();
    model.component("comp1").geom("geom1").lengthUnit("\u00b5m");
    model.component("comp1").geom("geom1").create("pi2", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi2").label("ImThera - Furl 1");
    model.component("comp1").geom("geom1").feature("pi2").set("part", "part3");
    model.component("comp1").geom("geom1").feature("pi2").setIndex("inputexpr", "z_center_cuff", 0);
    model.component("comp1").geom("geom1").feature("pi2").set("displ", new String[]{"shift_x", "shift_y", "0"});
    model.component("comp1").geom("geom1").feature("pi2").set("rot", "zw_rot");
    model.component("comp1").geom("geom1").feature("pi2").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").create("pi3", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi3").label("ImThera - Recessed Contact (Circle if Flat) 1");
    model.component("comp1").geom("geom1").feature("pi3").set("part", "part2");
    model.component("comp1").geom("geom1").feature("pi3")
         .setEntry("inputexpr", "rotation_angle", "ang_cuffseam_contactcenter [deg]");

    return model;
  }

  public static Model run2(Model model) {
    model.component("comp1").geom("geom1").feature("pi3")
         .setEntry("inputexpr", "z_src", "z_center_cuff-length_contactcenter_contactcenter");
    model.component("comp1").geom("geom1").feature("pi3").set("displ", new String[]{"shift_x", "shift_y", "0"});
    model.component("comp1").geom("geom1").feature("pi3").set("rot", "zw_rot");
    model.component("comp1").geom("geom1").feature("pi3").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepobj", "pi3_csel10", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepobj", "pi3_csel11", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepobj", "pi3_csel12", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel11.dom", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepbnd", "pi3_csel10.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepbnd", "pi3_csel11.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepbnd", "pi3_csel12.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepedg", "pi3_csel10.edg", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepedg", "pi3_csel11.edg", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepedg", "pi3_csel12.edg", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel10.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel12.pnt", "off");
    model.component("comp1").geom("geom1").create("pi4", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi4").label("ImThera - Recessed Contact (Circle if Flat) 2");
    model.component("comp1").geom("geom1").feature("pi4").set("part", "part2");
    model.component("comp1").geom("geom1").feature("pi4")
         .setEntry("inputexpr", "rotation_angle", "ang_cuffseam_contactcenter+ang_contactcenter_contactcenter [deg]");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("inputexpr", "z_src", "z_center_cuff");
    model.component("comp1").geom("geom1").feature("pi4").set("displ", new String[]{"shift_x", "shift_y", "0"});
    model.component("comp1").geom("geom1").feature("pi4").set("rot", "zw_rot");
    model.component("comp1").geom("geom1").feature("pi4").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepobj", "pi4_csel10", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepobj", "pi4_csel11", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepobj", "pi4_csel12", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepdom", "pi4_csel11.dom", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepbnd", "pi4_csel10.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepbnd", "pi4_csel11.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepbnd", "pi4_csel12.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepedg", "pi4_csel10.edg", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepedg", "pi4_csel11.edg", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepedg", "pi4_csel12.edg", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeeppnt", "pi4_csel10.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeeppnt", "pi4_csel12.pnt", "off");
    model.component("comp1").geom("geom1").create("pi5", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi5").label("ImThera - Recessed Contact (Circle if Flat) 3");
    model.component("comp1").geom("geom1").feature("pi5").set("part", "part2");
    model.component("comp1").geom("geom1").feature("pi5")
         .setEntry("inputexpr", "rotation_angle", "ang_cuffseam_contactcenter+2*ang_contactcenter_contactcenter [deg]");
    model.component("comp1").geom("geom1").feature("pi5")
         .setEntry("inputexpr", "z_src", "z_center_cuff+length_contactcenter_contactcenter");
    model.component("comp1").geom("geom1").feature("pi5").set("displ", new String[]{"shift_x", "shift_y", "0"});
    model.component("comp1").geom("geom1").feature("pi5").set("rot", "zw_rot");
    model.component("comp1").geom("geom1").feature("pi5").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepobj", "pi5_csel10", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepobj", "pi5_csel11", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepobj", "pi5_csel12", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepdom", "pi5_csel11.dom", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepbnd", "pi5_csel10.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepbnd", "pi5_csel11.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepbnd", "pi5_csel12.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepedg", "pi5_csel10.edg", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepedg", "pi5_csel11.edg", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepedg", "pi5_csel12.edg", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeeppnt", "pi5_csel10.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeeppnt", "pi5_csel12.pnt", "off");
    model.component("comp1").geom("geom1").create("pi6", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi6").label("ImThera - Recessed Contact (Circle if Flat) 4");
    model.component("comp1").geom("geom1").feature("pi6").set("part", "part2");
    model.component("comp1").geom("geom1").feature("pi6")
         .setEntry("inputexpr", "rotation_angle", "ang_cuffseam_contactcenter+3*ang_contactcenter_contactcenter [deg]");
    model.component("comp1").geom("geom1").feature("pi6")
         .setEntry("inputexpr", "z_src", "z_center_cuff-length_contactcenter_contactcenter");
    model.component("comp1").geom("geom1").feature("pi6").set("displ", new String[]{"shift_x", "shift_y", "0"});
    model.component("comp1").geom("geom1").feature("pi6").set("rot", "zw_rot");
    model.component("comp1").geom("geom1").feature("pi6").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi6").setEntry("selkeepobj", "pi6_csel10", "off");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("selkeepobj", "pi6_csel11", "off");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("selkeepobj", "pi6_csel12", "off");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("selkeepdom", "pi6_csel11.dom", "off");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("selkeepbnd", "pi6_csel10.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("selkeepbnd", "pi6_csel11.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("selkeepbnd", "pi6_csel12.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("selkeepedg", "pi6_csel10.edg", "off");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("selkeepedg", "pi6_csel11.edg", "off");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("selkeepedg", "pi6_csel12.edg", "off");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("selkeeppnt", "pi6_csel10.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi6").setEntry("selkeeppnt", "pi6_csel12.pnt", "off");
    model.component("comp1").geom("geom1").create("pi7", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi7").label("ImThera - Recessed Contact (Circle if Flat) 5");
    model.component("comp1").geom("geom1").feature("pi7").set("part", "part2");
    model.component("comp1").geom("geom1").feature("pi7")
         .setEntry("inputexpr", "rotation_angle", "ang_cuffseam_contactcenter+4*ang_contactcenter_contactcenter [deg]");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("inputexpr", "z_src", "z_center_cuff");
    model.component("comp1").geom("geom1").feature("pi7").set("displ", new String[]{"shift_x", "shift_y", "0"});
    model.component("comp1").geom("geom1").feature("pi7").set("rot", "zw_rot");
    model.component("comp1").geom("geom1").feature("pi7").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi7").setEntry("selkeepobj", "pi7_csel10", "off");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("selkeepobj", "pi7_csel11", "off");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("selkeepobj", "pi7_csel12", "off");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("selkeepdom", "pi7_csel11.dom", "off");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("selkeepbnd", "pi7_csel10.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("selkeepbnd", "pi7_csel11.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("selkeepbnd", "pi7_csel12.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("selkeepedg", "pi7_csel10.edg", "off");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("selkeepedg", "pi7_csel11.edg", "off");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("selkeepedg", "pi7_csel12.edg", "off");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("selkeeppnt", "pi7_csel10.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi7").setEntry("selkeeppnt", "pi7_csel12.pnt", "off");
    model.component("comp1").geom("geom1").create("pi8", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi8").label("ImThera - Recessed Contact (Circle if Flat) 6");
    model.component("comp1").geom("geom1").feature("pi8").set("part", "part2");
    model.component("comp1").geom("geom1").feature("pi8")
         .setEntry("inputexpr", "rotation_angle", "ang_cuffseam_contactcenter+5*ang_contactcenter_contactcenter [deg]");
    model.component("comp1").geom("geom1").feature("pi8")
         .setEntry("inputexpr", "z_src", "z_center_cuff+length_contactcenter_contactcenter");
    model.component("comp1").geom("geom1").feature("pi8").set("displ", new String[]{"shift_x", "shift_y", "0"});
    model.component("comp1").geom("geom1").feature("pi8").set("rot", "zw_rot");
    model.component("comp1").geom("geom1").feature("pi8").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi8").setEntry("selkeepobj", "pi8_csel10", "off");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("selkeepobj", "pi8_csel11", "off");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("selkeepobj", "pi8_csel12", "off");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("selkeepdom", "pi8_csel11.dom", "off");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("selkeepbnd", "pi8_csel10.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("selkeepbnd", "pi8_csel11.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("selkeepbnd", "pi8_csel12.bnd", "off");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("selkeepedg", "pi8_csel10.edg", "off");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("selkeepedg", "pi8_csel11.edg", "off");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("selkeepedg", "pi8_csel12.edg", "off");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("selkeeppnt", "pi8_csel10.pnt", "off");
    model.component("comp1").geom("geom1").feature("pi8").setEntry("selkeeppnt", "pi8_csel12.pnt", "off");
    model.component("comp1").geom("geom1").create("pi9", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi9").setIndex("inputexpr", "z_center_cuff", 0);
    model.component("comp1").geom("geom1").feature("pi9").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").create("pi10", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi10").label("Cuff Fill 1");
    model.component("comp1").geom("geom1").feature("pi10").set("part", "part4");
    model.component("comp1").geom("geom1").feature("pi10").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi10").setEntry("selkeepdom", "pi10_csel2.dom", "on");
    model.component("comp1").geom("geom1").create("pi11", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi11").label("Distant Ground 1");
    model.component("comp1").geom("geom1").feature("pi11").set("part", "part5");
    model.component("comp1").geom("geom1").feature("pi11").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi11").setEntry("selkeepdom", "pi11_csel1.dom", "on");
    model.component("comp1").geom("geom1").feature("pi11").setEntry("selkeepbnd", "pi11_csel1.bnd", "on");
    model.component("comp1").geom("geom1").run();
    model.component("comp1").geom("geom1").run("fin");

    model.view("view4").tag("view41");
    model.view("view3").tag("view4");
    model.view("view41").tag("view3");
    model.view("view10").tag("view101");
    model.view("view5").tag("view10");
    model.view("view11").tag("view111");
    model.view("view6").tag("view11");
    model.view("view7").tag("view5");
    model.view("view8").tag("view6");
    model.view("view9").tag("view7");
    model.view("view101").tag("view8");
    model.view("view111").tag("view9");

    model.component("comp1").material().create("matlnk16", "Link");
    model.component("comp1").material().create("matlnk10", "Link");
    model.component("comp1").material().create("matlnk2", "Link");
    model.material().create("mat2", "Common", "");
    model.material().create("mat6", "Common", "");
    model.component("comp1").material().create("matlnk1", "Link");
    model.component("comp1").material().create("matlnk3", "Link");
    model.component("comp1").material().create("matlnk11", "Link");
    model.component("comp1").material().create("matlnk12", "Link");
    model.component("comp1").material().create("matlnk13", "Link");
    model.component("comp1").material().create("matlnk14", "Link");
    model.component("comp1").material().create("matlnk15", "Link");
    model.component("comp1").material().create("matlnk4", "Link");
    model.material().create("mat4", "Common", "");
    model.component("comp1").material().create("matlnk5", "Link");
    model.component("comp1").material().create("matlnk6", "Link");
    model.component("comp1").material().create("matlnk7", "Link");
    model.component("comp1").material().create("matlnk8", "Link");
    model.component("comp1").material().create("matlnk9", "Link");
    model.material().create("mat5", "Common", "");
    model.component("comp1").material("matlnk16").selection().named("geom1_pi11_csel1_dom");
    model.component("comp1").material("matlnk10").selection().named("geom1_pi10_csel2_dom");
    model.component("comp1").material("matlnk2").selection().set(5);
    model.component("comp1").material("matlnk1").selection().set(3, 4, 6, 7, 8, 9);
    model.component("comp1").material("matlnk3").selection().named("geom1_pi3_csel12_dom");
    model.component("comp1").material("matlnk11").selection().named("geom1_pi4_csel12_dom");
    model.component("comp1").material("matlnk12").selection().named("geom1_pi5_csel12_dom");
    model.component("comp1").material("matlnk13").selection().named("geom1_pi6_csel12_dom");
    model.component("comp1").material("matlnk14").selection().named("geom1_pi7_csel12_dom");
    model.component("comp1").material("matlnk15").selection().named("geom1_pi8_csel12_dom");
    model.component("comp1").material("matlnk4").selection().named("geom1_pi3_csel10_dom");
    model.component("comp1").material("matlnk5").selection().named("geom1_pi4_csel10_dom");
    model.component("comp1").material("matlnk6").selection().named("geom1_pi5_csel12_dom");
    model.component("comp1").material("matlnk7").selection().named("geom1_pi6_csel10_dom");
    model.component("comp1").material("matlnk8").selection().named("geom1_pi7_csel12_dom");
    model.component("comp1").material("matlnk9").selection().named("geom1_pi8_csel12_dom");

    model.component("comp1").physics().create("ec", "ConductiveMedia", "geom1");
    model.component("comp1").physics("ec").create("pcs1", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs1").selection().named("geom1_pi3_csel11_pnt");
    model.component("comp1").physics("ec").create("pcs2", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs2").selection().named("geom1_pi4_csel11_pnt");
    model.component("comp1").physics("ec").create("pcs3", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs3").selection().named("geom1_pi5_csel11_pnt");
    model.component("comp1").physics("ec").create("pcs4", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs4").selection().named("geom1_pi6_csel11_pnt");
    model.component("comp1").physics("ec").create("pcs5", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs5").selection().named("geom1_pi7_csel11_pnt");
    model.component("comp1").physics("ec").create("pcs6", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs6").selection().named("geom1_pi8_csel11_pnt");
    model.component("comp1").physics("ec").create("gnd1", "Ground", 2);
    model.component("comp1").physics("ec").feature("gnd1").selection().named("geom1_pi11_csel1_bnd");

    model.component("comp1").mesh("mesh1").create("ftet1", "FreeTet");

    model.component("comp1").view("view1").set("renderwireframe", true);
    model.component("comp1").view("view1").set("transparency", true);
    model.view("view2").set("transparency", true);
    model.view("view3").label("View 3.1");
    model.view("view3").set("transparency", true);
    model.view("view4").label("View 4");
    model.view("view4").set("transparency", true);
    model.view("view5").label("View 5.1");
    model.view("view5").axis().set("xmin", -4449.15625);
    model.view("view5").axis().set("xmax", 4449.15625);
    model.view("view5").axis().set("ymin", -4720.59033203125);
    model.view("view5").axis().set("ymax", 4720.59033203125);
    model.view("view6").label("View 6.1");
    model.view("view6").axis().set("xmin", -6547.2890625);
    model.view("view6").axis().set("xmax", 6547.2890625);
    model.view("view6").axis().set("ymin", -4945.3798828125);
    model.view("view6").axis().set("ymax", 4945.3798828125);
    model.view("view7").label("View 7");
    model.view("view8").label("View 8");
    model.view("view8").axis().set("xmin", -1.4318937063217163);
    model.view("view8").axis().set("xmax", 1.4318937063217163);
    model.view("view9").label("View 9");
    model.view("view9").axis().set("xmin", -1.4318937063217163);
    model.view("view9").axis().set("xmax", 1.4318937063217163);
    model.view("view10").label("View 10");
    model.view("view11").label("View 11");

    model.component("comp1").material("matlnk16").label("Medium is Muscle");
    model.component("comp1").material("matlnk16").set("link", "mat5");
    model.component("comp1").material("matlnk10").label("Cuff Fill is Saline");
    model.component("comp1").material("matlnk10").set("link", "mat6");
    model.component("comp1").material("matlnk2").label("Furl is Silicone");
    model.component("comp1").material("matlnk2").set("link", "mat2");
    model.material("mat2").label("Silicone");
    model.material("mat2").propertyGroup("def")
         .set("electricconductivity", new String[]{"10^(-12)", "0", "0", "0", "10^(-12)", "0", "0", "0", "10^(-12)"});
    model.material("mat6").label("Saline");
    model.material("mat6").propertyGroup("def")
         .set("electricconductivity", new String[]{"1.76", "0", "0", "0", "1.76", "0", "0", "0", "1.76"});
    model.component("comp1").material("matlnk1").label("Inner Cuff is Silicone");
    model.component("comp1").material("matlnk3").label("Recess 1 is Saline");
    model.component("comp1").material("matlnk3").set("link", "mat6");
    model.component("comp1").material("matlnk11").label("Recess 2 is Saline");
    model.component("comp1").material("matlnk11").set("link", "mat6");
    model.component("comp1").material("matlnk12").label("Recess 3 is Saline");
    model.component("comp1").material("matlnk12").set("link", "mat6");
    model.component("comp1").material("matlnk13").label("Recess 4 is Saline");
    model.component("comp1").material("matlnk13").set("link", "mat6");
    model.component("comp1").material("matlnk14").label("Recess 5 is Saline");
    model.component("comp1").material("matlnk14").set("link", "mat6");
    model.component("comp1").material("matlnk15").label("Recess 6 is Saline");
    model.component("comp1").material("matlnk15").set("link", "mat6");
    model.component("comp1").material("matlnk4").label("Contact 1 is Platinum");
    model.component("comp1").material("matlnk4").set("link", "mat4");
    model.material("mat4").label("Platinum");
    model.material("mat4").propertyGroup("def")
         .set("electricconductivity", new String[]{"9.43*10^6", "0", "0", "0", "9.43*10^6", "0", "0", "0", "9.43*10^6"});
    model.component("comp1").material("matlnk5").label("Contact 2 is Platinum");
    model.component("comp1").material("matlnk5").set("link", "mat4");
    model.component("comp1").material("matlnk6").label("Contact 3 is Platinum");
    model.component("comp1").material("matlnk6").set("link", "mat4");
    model.component("comp1").material("matlnk7").label("Contact 4 is Platinum");
    model.component("comp1").material("matlnk7").set("link", "mat4");
    model.component("comp1").material("matlnk8").label("Contact 5 is Platinum");
    model.component("comp1").material("matlnk8").set("link", "mat4");
    model.component("comp1").material("matlnk9").label("Contact 6 is Platinum");
    model.component("comp1").material("matlnk9").set("link", "mat4");
    model.material("mat5").label("Muscle");
    model.material("mat5").propertyGroup("def")
         .set("electricconductivity", new String[]{"0.086", "0", "0", "0", "0.086", "0", "0", "0", "0.35"});

    model.component("comp1").physics("ec").feature("pcs1").set("Qjp", 0.001);
    model.component("comp1").physics("ec").feature("pcs2").set("Qjp", 0.001);
    model.component("comp1").physics("ec").feature("pcs3").set("Qjp", 0.001);
    model.component("comp1").physics("ec").feature("pcs4").set("Qjp", 0.001);
    model.component("comp1").physics("ec").feature("pcs5").set("Qjp", 0.001);
    model.component("comp1").physics("ec").feature("pcs6").set("Qjp", 0.001);

    model.component("comp1").mesh("mesh1").feature("size").set("hauto", 3);
    model.component("comp1").mesh("mesh1").run();

    model.study().create("std1");
    model.study("std1").create("stat", "Stationary");

    model.sol().create("sol1");
    model.sol("sol1").study("std1");
    model.sol("sol1").attach("std1");
    model.sol("sol1").create("st1", "StudyStep");
    model.sol("sol1").create("v1", "Variables");
    model.sol("sol1").create("s1", "Stationary");
    model.sol("sol1").feature("s1").create("fc1", "FullyCoupled");
    model.sol("sol1").feature("s1").create("i1", "Iterative");
    model.sol("sol1").feature("s1").feature("i1").create("mg1", "Multigrid");
    model.sol("sol1").feature("s1").feature().remove("fcDef");

    model.result().create("pg1", "PlotGroup3D");
    model.result("pg1").create("mslc1", "Multislice");

    model.sol("sol1").attach("std1");
    model.sol("sol1").feature("s1").feature("i1").set("linsolver", "cg");
    model.sol("sol1").feature("s1").feature("i1").feature("mg1").set("prefun", "amg");
    model.sol("sol1").runAll();

    model.result("pg1").label("Electric Potential (ec)");
    model.result("pg1").set("frametype", "spatial");
    model.result("pg1").feature("mslc1").set("colortable", "RainbowLight");
    model.result("pg1").feature("mslc1").set("resolution", "normal");

    model.component("comp1").geom("geom1").run("fin");

    return model;
  }

  public static void main(String[] args) {
    Model model = run();
    run2(model);
  }

}

package model;

import com.comsol.model.Model;
import org.eclipse.e4.ui.css.swt.properties.custom.CSSPropertyUnselectedTabsSWTHandler;

import java.util.HashMap;

class Part {
    public static boolean createPartPrimitive(String id, String psuedonym, Model model) {

        return createPartPrimitive(id, psuedonym, model, null);
    }

    public static boolean createPartInstance(String id, String psuedonym, Model model,
                                             HashMap<String, String> partPrimitives) {
        return createPartInstance(id, psuedonym, model, partPrimitives, null);
    }

    /**
     *
     * @param id
     * @param psuedonym
     * @param model
     * @param data
     * @return
     */
    public static boolean createPartPrimitive(String id, String psuedonym, Model model,
                                              HashMap<String, Object> data) {
        switch (psuedonym) {
            case "TubeCuff_Primitive":
                model.geom().create("part1", "Part", 3);
                model.geom("part1").label(psuedonym);
                model.geom("part1").lengthUnit("\u00b5m");

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
                break;
            case "RibbonContact_Primitive":
                model.geom().create("part2", "Part", 3);
                model.geom("part2").label("RibbonContact_Primitive");
                model.geom("part2").lengthUnit("\u00b5m");

                model.geom("part2").inputParam().set("Thk_elec", "0.1 [mm]");
                model.geom("part2").inputParam().set("L_elec", "3 [mm]");
                model.geom("part2").inputParam().set("R_in", "1 [mm]");
                model.geom("part2").inputParam().set("Recess", "0.1 [mm]");
                model.geom("part2").inputParam().set("Center", "10 [mm]");
                model.geom("part2").inputParam().set("Theta_contact", "100 [deg]");
                model.geom("part2").inputParam().set("Rot_def", "0 [deg]");

                model.geom("part2").selection().create("csel1", "CumulativeSelection");
                model.geom("part2").selection("csel1").label("CONTACT CROSS SECTION");
                model.geom("part2").selection().create("csel2", "CumulativeSelection");
                model.geom("part2").selection("csel2").label("RECESS CROSS SECTION");
                model.geom("part2").selection().create("csel3", "CumulativeSelection");
                model.geom("part2").selection("csel3").label("SRC");
                model.geom("part2").selection().create("csel4", "CumulativeSelection");
                model.geom("part2").selection("csel4").label("CONTACT FINAL");
                model.geom("part2").selection().create("csel5", "CumulativeSelection");
                model.geom("part2").selection("csel5").label("RECESS FINAL");

                model.geom("part2").create("wp1", "WorkPlane");
                model.geom("part2").feature("wp1").label("Contact Cross Section");
                model.geom("part2").feature("wp1").set("contributeto", "csel1");
                model.geom("part2").feature("wp1").set("quickplane", "xz");
                model.geom("part2").feature("wp1").set("unite", true);
                model.geom("part2").feature("wp1").geom().create("r1", "Rectangle");
                model.geom("part2").feature("wp1").geom().feature("r1").label("Contact Cross Section");
                model.geom("part2").feature("wp1").geom().feature("r1")
                        .set("pos", new String[]{"R_in+Recess+Thk_elec/2", "Center"});
                model.geom("part2").feature("wp1").geom().feature("r1").set("base", "center");
                model.geom("part2").feature("wp1").geom().feature("r1").set("size", new String[]{"Thk_elec", "L_elec"});
                model.geom("part2").create("rev1", "Revolve");
                model.geom("part2").feature("rev1").label("Make Contact");
                model.geom("part2").feature("rev1").set("contributeto", "csel4");
                model.geom("part2").feature("rev1").set("angle1", "Rot_def");
                model.geom("part2").feature("rev1").set("angle2", "Rot_def+Theta_contact");
                model.geom("part2").feature("rev1").selection("input").named("csel1");
                model.geom("part2").create("if1", "If");
                model.geom("part2").feature("if1").set("condition", "Recess>0");
                model.geom("part2").create("wp2", "WorkPlane");
                model.geom("part2").feature("wp2").label("Recess Cross Section 1");
                model.geom("part2").feature("wp2").set("contributeto", "csel2");
                model.geom("part2").feature("wp2").set("quickplane", "xz");
                model.geom("part2").feature("wp2").set("unite", true);
                model.geom("part2").feature("wp2").geom().selection().create("csel1", "CumulativeSelection");
                model.geom("part2").feature("wp2").geom().selection("csel1").label("Cumulative Selection 1");
                model.geom("part2").feature("wp2").geom().selection().create("csel2", "CumulativeSelection");
                model.geom("part2").feature("wp2").geom().selection("csel2").label("RECESS CROSS SECTION");
                model.geom("part2").feature("wp2").geom().create("r1", "Rectangle");
                model.geom("part2").feature("wp2").geom().feature("r1").label("Recess Cross Section");
                model.geom("part2").feature("wp2").geom().feature("r1").set("contributeto", "csel2");
                model.geom("part2").feature("wp2").geom().feature("r1").set("pos", new String[]{"R_in+Recess/2", "Center"});
                model.geom("part2").feature("wp2").geom().feature("r1").set("base", "center");
                model.geom("part2").feature("wp2").geom().feature("r1").set("size", new String[]{"Recess", "L_elec"});
                model.geom("part2").create("rev2", "Revolve");
                model.geom("part2").feature("rev2").label("Make Recess");
                model.geom("part2").feature("rev2").set("contributeto", "csel5");
                model.geom("part2").feature("rev2").set("angle1", "Rot_def");
                model.geom("part2").feature("rev2").set("angle2", "Rot_def+Theta_contact");
                model.geom("part2").feature("rev2").selection("input").named("csel2");
                model.geom("part2").create("endif1", "EndIf");
                model.geom("part2").create("pt1", "Point");
                model.geom("part2").feature("pt1").label("src");
                model.geom("part2").feature("pt1").set("contributeto", "csel3");
                model.geom("part2").feature("pt1")
                        .set("p", new String[]{"(R_in+Recess+Thk_elec/2)*cos(Rot_def+Theta_contact/2)", "(R_in+Recess+Thk_elec/2)*sin(Rot_def+Theta_contact/2)", "Center"});
                model.geom("part2").run();
                break;
            case "WireContact_Primitive":
                model.geom().create("part3", "Part", 3);
                model.geom("part3").label("WireContact_Primitive");
                model.geom("part3").lengthUnit("\u00b5m");

                model.geom("part3").inputParam().set("R_conductor", "r_conductor_P");
                model.geom("part3").inputParam().set("R_in", "R_in_P");
                model.geom("part3").inputParam().set("Center", "Center_P");
                model.geom("part3").inputParam().set("Pitch", "Pitch_P");
                model.geom("part3").inputParam().set("Sep_conductor", "sep_conductor_P");
                model.geom("part3").inputParam().set("Theta_conductor", "theta_conductor_P");

                model.geom("part3").selection().create("csel1", "CumulativeSelection");
                model.geom("part3").selection("csel1").label("CONTACT CROSS SECTION");
                model.geom("part3").selection().create("csel2", "CumulativeSelection");
                model.geom("part3").selection("csel2").label("CONTACT FINAL");
                model.geom("part3").selection().create("csel3", "CumulativeSelection");
                model.geom("part3").selection("csel3").label("SRC");

                model.geom("part3").create("wp1", "WorkPlane");
                model.geom("part3").feature("wp1").label("Contact Cross Section");
                model.geom("part3").feature("wp1").set("contributeto", "csel1");
                model.geom("part3").feature("wp1").set("quickplane", "zx");
                model.geom("part3").feature("wp1").set("unite", true);
                model.geom("part3").feature("wp1").geom().selection().create("csel1", "CumulativeSelection");
                model.geom("part3").feature("wp1").geom().selection("csel1").label("CONTACT CROSS SECTION");
                model.geom("part3").feature("wp1").geom().create("c1", "Circle");
                model.geom("part3").feature("wp1").geom().feature("c1").label("Contact Cross Section");
                model.geom("part3").feature("wp1").geom().feature("c1").set("contributeto", "csel1");
                model.geom("part3").feature("wp1").geom().feature("c1")
                        .set("pos", new String[]{"Center", "R_in-R_conductor-Sep_conductor"});
                model.geom("part3").feature("wp1").geom().feature("c1").set("r", "R_conductor");
                model.geom("part3").create("rev1", "Revolve");
                model.geom("part3").feature("rev1").label("Make Contact");
                model.geom("part3").feature("rev1").set("contributeto", "csel2");
                model.geom("part3").feature("rev1").set("angle2", "Theta_conductor");
                model.geom("part3").feature("rev1").set("axis", new int[]{1, 0});
                model.geom("part3").feature("rev1").selection("input").named("csel1");
                model.geom("part3").create("pt1", "Point");
                model.geom("part3").feature("pt1").label("Src");
                model.geom("part3").feature("pt1").set("contributeto", "csel3");
                model.geom("part3").feature("pt1")
                        .set("p", new String[]{"(R_in-R_conductor-Sep_conductor)*cos(Theta_conductor/2)", "(R_in-R_conductor-Sep_conductor)*sin(Theta_conductor/2)", "Center"});
                model.geom("part3").run();
                break;
            case "CircleContact_Primitive":
                model.geom().create("part4", "Part", 3);
                model.geom("part4").label("CircleContact_Primitive");
                model.geom("part4").lengthUnit("\u00b5m");

                model.geom("part4").inputParam().set("Recess", "Recess_ITC");
                model.geom("part4").inputParam().set("Rotation_angle", "0 [deg]");
                model.geom("part4").inputParam().set("Center", "Center_IT");
                model.geom("part4").inputParam().set("Round_def", "Round_def_ITC");
                model.geom("part4").inputParam().set("R_in", "R_in_ITI");
                model.geom("part4").inputParam().set("Contact_depth", "Contact_depth_ITC");
                model.geom("part4").inputParam().set("Overshoot", "Overshoot_ITC");
                model.geom("part4").inputParam().set("A_ellipse_contact", "a_ellipse_contact_ITC");
                model.geom("part4").inputParam().set("Diam_contact", "diam_contact_ITC");
                model.geom("part4").inputParam().set("L", "L_IT");

                model.geom("part4").selection().create("csel11", "CumulativeSelection");
                model.geom("part4").selection("csel11").label("CONTACT CUTTER IN");
                model.geom("part4").selection().create("csel10", "CumulativeSelection");
                model.geom("part4").selection("csel10").label("PRE CUT CONTACT");
                model.geom("part4").selection().create("csel7", "CumulativeSelection");
                model.geom("part4").selection("csel7").label("RECESS FINAL");
                model.geom("part4").selection().create("csel8", "CumulativeSelection");
                model.geom("part4").selection("csel8").label("RECESS OVERSHOOT");
                model.geom("part4").selection().create("csel14", "CumulativeSelection");
                model.geom("part4").selection("csel14").label("SRC");
                model.geom("part4").selection().create("csel9", "CumulativeSelection");
                model.geom("part4").selection("csel9").label("PLANE FOR CONTACT");
                model.geom("part4").selection().create("csel13", "CumulativeSelection");
                model.geom("part4").selection("csel13").label("CONTACT FINAL");
                model.geom("part4").selection().create("csel12", "CumulativeSelection");
                model.geom("part4").selection("csel12").label("CONTACT CUTTER OUT");
                model.geom("part4").selection().create("csel1", "CumulativeSelection");
                model.geom("part4").selection("csel1").label("BASE CONTACT PLANE (PRE ROTATION)");
                model.geom("part4").selection().create("csel2", "CumulativeSelection");
                model.geom("part4").selection("csel2").label("BASE PLANE (PRE ROTATION)");
                model.geom("part4").selection().create("csel3", "CumulativeSelection");
                model.geom("part4").selection("csel3").label("PLANE FOR RECESS");
                model.geom("part4").selection().create("csel4", "CumulativeSelection");
                model.geom("part4").selection("csel4").label("PRE CUT RECESS");
                model.geom("part4").selection().create("csel5", "CumulativeSelection");
                model.geom("part4").selection("csel5").label("RECESS CUTTER IN");
                model.geom("part4").selection().create("csel6", "CumulativeSelection");
                model.geom("part4").selection("csel6").label("RECESS CUTTER OUT");

                model.geom("part4").create("wp1", "WorkPlane");
                model.geom("part4").feature("wp1").label("Base Plane (Pre Rrotation)");
                model.geom("part4").feature("wp1").set("contributeto", "csel2");
                model.geom("part4").feature("wp1").set("quickplane", "yz");
                model.geom("part4").feature("wp1").set("unite", true);
                model.geom("part4").create("if1", "If");
                model.geom("part4").feature("if1").label("If Recess");
                model.geom("part4").feature("if1").set("condition", "Recess>0");
                model.geom("part4").create("wp2", "WorkPlane");
                model.geom("part4").feature("wp2").label("Rotated Plane for Recess");
                model.geom("part4").feature("wp2").set("contributeto", "csel3");
                model.geom("part4").feature("wp2").set("planetype", "transformed");
                model.geom("part4").feature("wp2").set("workplane", "wp1");
                model.geom("part4").feature("wp2").set("transaxis", new int[]{0, 1, 0});
                model.geom("part4").feature("wp2").set("transrot", "Rotation_angle");
                model.geom("part4").feature("wp2").set("unite", true);
                model.geom("part4").feature("wp2").geom().selection().create("csel1", "CumulativeSelection");
                model.geom("part4").feature("wp2").geom().selection("csel1").label("CONTACT OUTLINE SHAPE");
                model.geom("part4").feature("wp2").geom().create("if1", "If");
                model.geom("part4").feature("wp2").geom().feature("if1").label("If Contact Surface is Circle");
                model.geom("part4").feature("wp2").geom().feature("if1").set("condition", "Round_def_ITC==1");
                model.geom("part4").feature("wp2").geom().create("e1", "Ellipse");
                model.geom("part4").feature("wp2").geom().feature("e1").label("Contact Outline");
                model.geom("part4").feature("wp2").geom().feature("e1").set("contributeto", "csel1");
                model.geom("part4").feature("wp2").geom().feature("e1").set("pos", new String[]{"0", "Center"});
                model.geom("part4").feature("wp2").geom().feature("e1")
                        .set("semiaxes", new String[]{"A_ellipse_contact", "Diam_contact/2"});
                model.geom("part4").feature("wp2").geom().create("elseif1", "ElseIf");
                model.geom("part4").feature("wp2").geom().feature("elseif1").label("Else If Contact Outline is Circle");
                model.geom("part4").feature("wp2").geom().feature("elseif1").set("condition", "Round_def_ITC==2");
                model.geom("part4").feature("wp2").geom().create("e2", "Ellipse");
                model.geom("part4").feature("wp2").geom().feature("e2").label("Contact Outline 1");
                model.geom("part4").feature("wp2").geom().feature("e2").set("contributeto", "csel1");
                model.geom("part4").feature("wp2").geom().feature("e2").set("pos", new String[]{"0", "Center"});
                model.geom("part4").feature("wp2").geom().feature("e2")
                        .set("semiaxes", new String[]{"Diam_contact/2", "Diam_contact/2"});
                model.geom("part4").feature("wp2").geom().create("endif1", "EndIf");
                model.geom("part4").create("ext1", "Extrude");
                model.geom("part4").feature("ext1").label("Make Pre Cut Recess Domains");
                model.geom("part4").feature("ext1").set("contributeto", "csel4");
                model.geom("part4").feature("ext1").setIndex("distance", "R_in+Recess+Overshoot", 0);
                model.geom("part4").feature("ext1").selection("input").named("csel3");
                model.geom("part4").create("cyl1", "Cylinder");
                model.geom("part4").feature("cyl1").label("Recess Cut In");
                model.geom("part4").feature("cyl1").set("contributeto", "csel5");
                model.geom("part4").feature("cyl1").set("pos", new String[]{"0", "0", "Center-L/2"});
                model.geom("part4").feature("cyl1").set("r", "R_in");
                model.geom("part4").feature("cyl1").set("h", "L");
                model.geom("part4").create("cyl2", "Cylinder");
                model.geom("part4").feature("cyl2").label("Recess Cut Out");
                model.geom("part4").feature("cyl2").set("contributeto", "csel6");
                model.geom("part4").feature("cyl2").set("pos", new String[]{"0", "0", "Center-L/2"});
                model.geom("part4").feature("cyl2").set("r", "R_in+Recess");
                model.geom("part4").feature("cyl2").set("h", "L");
                model.geom("part4").create("dif1", "Difference");
                model.geom("part4").feature("dif1").label("Execute Recess Cut In");
                model.geom("part4").feature("dif1").set("contributeto", "csel7");
                model.geom("part4").feature("dif1").selection("input").named("csel4");
                model.geom("part4").feature("dif1").selection("input2").named("csel5");
                model.geom("part4").create("pard1", "PartitionDomains");
                model.geom("part4").feature("pard1").set("contributeto", "csel7");
                model.geom("part4").feature("pard1").set("partitionwith", "objects");
                model.geom("part4").feature("pard1").set("keepobject", false);
                model.geom("part4").feature("pard1").selection("domain").named("csel4");
                model.geom("part4").feature("pard1").selection("object").named("csel6");
                model.geom("part4").create("ballsel1", "BallSelection");
                model.geom("part4").feature("ballsel1").label("Select Overshoot");
                model.geom("part4").feature("ballsel1").set("posx", "(R_in+Recess+Overshoot/2)*cos(Rotation_angle)");
                model.geom("part4").feature("ballsel1").set("posy", "(R_in+Recess+Overshoot/2)*sin(Rotation_angle)");
                model.geom("part4").feature("ballsel1").set("posz", "Center");
                model.geom("part4").feature("ballsel1").set("r", 1);
                model.geom("part4").feature("ballsel1").set("contributeto", "csel8");
                model.geom("part4").create("del1", "Delete");
                model.geom("part4").feature("del1").label("Delete Recess Overshoot");
                model.geom("part4").feature("del1").selection("input").init(3);
                model.geom("part4").feature("del1").selection("input").named("csel8");
                model.geom("part4").create("endif1", "EndIf");
                model.geom("part4").create("wp3", "WorkPlane");
                model.geom("part4").feature("wp3").label("Rotated Plane for Contact");
                model.geom("part4").feature("wp3").set("contributeto", "csel9");
                model.geom("part4").feature("wp3").set("planetype", "transformed");
                model.geom("part4").feature("wp3").set("workplane", "wp1");
                model.geom("part4").feature("wp3").set("transaxis", new int[]{0, 1, 0});
                model.geom("part4").feature("wp3").set("transrot", "Rotation_angle");
                model.geom("part4").feature("wp3").set("unite", true);
                model.geom("part4").feature("wp3").geom().selection().create("csel1", "CumulativeSelection");
                model.geom("part4").feature("wp3").geom().selection("csel1").label("CONTACT OUTLINE SHAPE");
                model.geom("part4").feature("wp3").geom().create("if1", "If");
                model.geom("part4").feature("wp3").geom().feature("if1").label("If Contact Surface is Circle");
                model.geom("part4").feature("wp3").geom().feature("if1").set("condition", "Round_def_ITC==1");
                model.geom("part4").feature("wp3").geom().create("e1", "Ellipse");
                model.geom("part4").feature("wp3").geom().feature("e1").label("Contact Outline");
                model.geom("part4").feature("wp3").geom().feature("e1").set("contributeto", "csel1");
                model.geom("part4").feature("wp3").geom().feature("e1").set("pos", new String[]{"0", "Center"});
                model.geom("part4").feature("wp3").geom().feature("e1")
                        .set("semiaxes", new String[]{"A_ellipse_contact", "Diam_contact/2"});
                model.geom("part4").feature("wp3").geom().create("elseif1", "ElseIf");
                model.geom("part4").feature("wp3").geom().feature("elseif1").label("Else If Contact Outline is Circle");
                model.geom("part4").feature("wp3").geom().feature("elseif1").set("condition", "Round_def_ITC==2");
                model.geom("part4").feature("wp3").geom().create("e2", "Ellipse");
                model.geom("part4").feature("wp3").geom().feature("e2").label("Contact Outline 1");
                model.geom("part4").feature("wp3").geom().feature("e2").set("contributeto", "csel1");
                model.geom("part4").feature("wp3").geom().feature("e2").set("pos", new String[]{"0", "Center"});
                model.geom("part4").feature("wp3").geom().feature("e2")
                        .set("semiaxes", new String[]{"Diam_contact/2", "Diam_contact/2"});
                model.geom("part4").feature("wp3").geom().create("endif1", "EndIf");
                model.geom("part4").create("ext2", "Extrude");
                model.geom("part4").feature("ext2").label("Make Pre Cut Contact Domains");
                model.geom("part4").feature("ext2").set("contributeto", "csel10");
                model.geom("part4").feature("ext2").setIndex("distance", "R_in+Recess+Contact_depth+Overshoot", 0);
                model.geom("part4").feature("ext2").selection("input").named("csel9");
                model.geom("part4").create("cyl3", "Cylinder");
                model.geom("part4").feature("cyl3").label("Contact Cut In");
                model.geom("part4").feature("cyl3").set("contributeto", "csel11");
                model.geom("part4").feature("cyl3").set("pos", new String[]{"0", "0", "Center-L/2"});
                model.geom("part4").feature("cyl3").set("r", "R_in+Recess");
                model.geom("part4").feature("cyl3").set("h", "L");
                model.geom("part4").create("cyl4", "Cylinder");
                model.geom("part4").feature("cyl4").label("Contact Cut Out");
                model.geom("part4").feature("cyl4").set("contributeto", "csel12");
                model.geom("part4").feature("cyl4").set("pos", new String[]{"0", "0", "Center-L/2"});
                model.geom("part4").feature("cyl4").set("r", "R_in+Recess+Contact_depth");
                model.geom("part4").feature("cyl4").set("h", "L");
                model.geom("part4").create("dif2", "Difference");
                model.geom("part4").feature("dif2").label("Execute Contact Cut In");
                model.geom("part4").feature("dif2").set("contributeto", "csel13");
                model.geom("part4").feature("dif2").selection("input").named("csel10");
                model.geom("part4").feature("dif2").selection("input2").named("csel11");
                model.geom("part4").create("pard2", "PartitionDomains");
                model.geom("part4").feature("pard2").set("contributeto", "csel13");
                model.geom("part4").feature("pard2").set("partitionwith", "objects");
                model.geom("part4").feature("pard2").set("keepobject", false);
                model.geom("part4").feature("pard2").selection("domain").named("csel10");
                model.geom("part4").feature("pard2").selection("object").named("csel12");
                model.geom("part4").create("ballsel2", "BallSelection");
                model.geom("part4").feature("ballsel2").label("Select Overshoot 1");
                model.geom("part4").feature("ballsel2")
                        .set("posx", "(R_in+Recess+Contact_depth+Overshoot/2)*cos(Rotation_angle)");
                model.geom("part4").feature("ballsel2")
                        .set("posy", "(R_in+Recess+Contact_depth+Overshoot/2)*sin(Rotation_angle)");
                model.geom("part4").feature("ballsel2").set("posz", "Center");
                model.geom("part4").feature("ballsel2").set("r", 1);
                model.geom("part4").feature("ballsel2").set("contributeto", "csel8");
                model.geom("part4").create("del2", "Delete");
                model.geom("part4").feature("del2").label("Delete Recess Overshoot 1");
                model.geom("part4").feature("del2").selection("input").init(3);
                model.geom("part4").feature("del2").selection("input").named("csel8");
                model.geom("part4").create("pt1", "Point");
                model.geom("part4").feature("pt1").label("Src");
                model.geom("part4").feature("pt1").set("contributeto", "csel14");
                model.geom("part4").feature("pt1")
                        .set("p", new String[]{"(R_in+Recess+Contact_depth/2)*cos(Rotation_angle)", "(R_in+Recess+Contact_depth/2)*sin(Rotation_angle)", "Center"});
                model.geom("part4").run();
                break;
            case "HelicalCuffnContact_Primitive":
                model.geom().create("part5", "Part", 3);
                model.geom("part5").label("HelicalCuffnContact_Primitive");
                model.geom("part5").lengthUnit("\u00b5m");

                model.geom("part5").inputParam().set("Center", "Center_LN");

                model.geom("part5").selection().create("csel1", "CumulativeSelection");
                model.geom("part5").selection("csel1").label("PC1");
                model.geom("part5").selection().create("csel2", "CumulativeSelection");
                model.geom("part5").selection("csel2").label("Cuffp1");
                model.geom("part5").selection().create("csel3", "CumulativeSelection");
                model.geom("part5").selection("csel3").label("SEL END P1");
                model.geom("part5").selection().create("csel4", "CumulativeSelection");
                model.geom("part5").selection("csel4").label("PC2");
                model.geom("part5").selection().create("csel10", "CumulativeSelection");
                model.geom("part5").selection("csel10").label("SRC");
                model.geom("part5").selection().create("csel5", "CumulativeSelection");
                model.geom("part5").selection("csel5").label("Cuffp2");
                model.geom("part5").selection().create("csel6", "CumulativeSelection");
                model.geom("part5").selection("csel6").label("Conductorp2");
                model.geom("part5").selection().create("csel7", "CumulativeSelection");
                model.geom("part5").selection("csel7").label("SEL END P2");
                model.geom("part5").selection().create("csel8", "CumulativeSelection");
                model.geom("part5").selection("csel8").label("Cuffp3");
                model.geom("part5").selection().create("csel9", "CumulativeSelection");
                model.geom("part5").selection("csel9").label("PC3");

                model.geom("part5").create("wp1", "WorkPlane");
                model.geom("part5").feature("wp1").label("Helical Insulator Cross Section Part 1");
                model.geom("part5").feature("wp1").set("quickplane", "xz");
                model.geom("part5").feature("wp1").set("unite", true);
                model.geom("part5").feature("wp1").geom().selection().create("csel1", "CumulativeSelection");
                model.geom("part5").feature("wp1").geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION");
                model.geom("part5").feature("wp1").geom().selection().create("csel2", "CumulativeSelection");
                model.geom("part5").feature("wp1").geom().selection("csel2").label("HELICAL INSULATOR CROSS SECTION P1");
                model.geom("part5").feature("wp1").geom().create("r1", "Rectangle");
                model.geom("part5").feature("wp1").geom().feature("r1").label("Helical Insulator Cross Section Part 1");
                model.geom("part5").feature("wp1").geom().feature("r1").set("contributeto", "csel2");
                model.geom("part5").feature("wp1").geom().feature("r1")
                        .set("pos", new String[]{"r_cuff_in_LN+(thk_cuff_LN/2)", "Center-(L_cuff_LN/2)"});
                model.geom("part5").feature("wp1").geom().feature("r1").set("base", "center");
                model.geom("part5").feature("wp1").geom().feature("r1").set("size", new String[]{"thk_cuff_LN", "w_cuff_LN"});
                model.geom("part5").create("pc1", "ParametricCurve");
                model.geom("part5").feature("pc1").label("Parametric Curve Part 1");
                model.geom("part5").feature("pc1").set("contributeto", "csel1");
                model.geom("part5").feature("pc1").set("parmax", "rev_cuff_LN*(0.75/2.5)");
                model.geom("part5").feature("pc1")
                        .set("coord", new String[]{"cos(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "sin(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "Center+(L_cuff_LN)*(s/rev_cuff_LN)-(L_cuff_LN/2)"});
                model.geom("part5").create("swe1", "Sweep");
                model.geom("part5").feature("swe1").label("Make Cuff Part 1");
                model.geom("part5").feature("swe1").set("contributeto", "csel2");
                model.geom("part5").feature("swe1").set("crossfaces", true);
                model.geom("part5").feature("swe1").set("keep", false);
                model.geom("part5").feature("swe1").set("includefinal", false);
                model.geom("part5").feature("swe1").set("twistcomp", false);
                model.geom("part5").feature("swe1").selection("face").named("wp1_csel2");
                model.geom("part5").feature("swe1").selection("edge").named("csel1");
                model.geom("part5").feature("swe1").selection("diredge").set("pc1(1)", 1);
                model.geom("part5").create("ballsel1", "BallSelection");
                model.geom("part5").feature("ballsel1").set("entitydim", 2);
                model.geom("part5").feature("ballsel1").label("Select End Face Part 1");
                model.geom("part5").feature("ballsel1").set("posx", "cos(2*pi*rev_cuff_LN*((0.75)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                model.geom("part5").feature("ballsel1").set("posy", "sin(2*pi*rev_cuff_LN*((0.75)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                model.geom("part5").feature("ballsel1")
                        .set("posz", "Center+(L_cuff_LN)*(rev_cuff_LN*((0.75)/2.5)/rev_cuff_LN)-(L_cuff_LN/2)");
                model.geom("part5").feature("ballsel1").set("r", 1);
                model.geom("part5").feature("ballsel1").set("contributeto", "csel3");
                model.geom("part5").create("wp2", "WorkPlane");
                model.geom("part5").feature("wp2").label("Helical Insulator Cross Section Part 2");
                model.geom("part5").feature("wp2").set("planetype", "faceparallel");
                model.geom("part5").feature("wp2").set("unite", true);
                model.geom("part5").feature("wp2").selection("face").named("csel3");
                model.geom("part5").feature("wp2").geom().selection().create("csel1", "CumulativeSelection");
                model.geom("part5").feature("wp2").geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION P2");
                model.geom("part5").feature("wp2").geom().selection().create("csel2", "CumulativeSelection");
                model.geom("part5").feature("wp2").geom().selection("csel2").label("HELICAL CONDUCTOR CROSS SECTION P2");
                model.geom("part5").feature("wp2").geom().create("r1", "Rectangle");
                model.geom("part5").feature("wp2").geom().feature("r1").label("Helical Insulator Cross Section Part 2");
                model.geom("part5").feature("wp2").geom().feature("r1").set("contributeto", "csel1");
                model.geom("part5").feature("wp2").geom().feature("r1").set("base", "center");
                model.geom("part5").feature("wp2").geom().feature("r1").set("size", new String[]{"thk_cuff_LN", "w_cuff_LN"});
                model.geom("part5").create("wp3", "WorkPlane");
                model.geom("part5").feature("wp3").label("Helical Conductor Cross Section Part 2");
                model.geom("part5").feature("wp3").set("planetype", "faceparallel");
                model.geom("part5").feature("wp3").set("unite", true);
                model.geom("part5").feature("wp3").selection("face").named("csel3");
                model.geom("part5").feature("wp3").geom().selection().create("csel1", "CumulativeSelection");
                model.geom("part5").feature("wp3").geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION P2");
                model.geom("part5").feature("wp3").geom().selection().create("csel2", "CumulativeSelection");
                model.geom("part5").feature("wp3").geom().selection("csel2").label("HELICAL CONDUCTOR CROSS SECTION P2");
                model.geom("part5").feature("wp3").geom().create("r2", "Rectangle");
                model.geom("part5").feature("wp3").geom().feature("r2").label("Helical Conductor Cross Section Part 2");
                model.geom("part5").feature("wp3").geom().feature("r2").set("contributeto", "csel2");
                model.geom("part5").feature("wp3").geom().feature("r2").set("pos", new String[]{"(thk_elec_LN-thk_cuff_LN)/2", "0"});
                model.geom("part5").feature("wp3").geom().feature("r2").set("base", "center");
                model.geom("part5").feature("wp3").geom().feature("r2").set("size", new String[]{"thk_elec_LN", "w_elec_LN"});
                model.geom("part5").create("pc2", "ParametricCurve");
                model.geom("part5").feature("pc2").label("Parametric Curve Part 2");
                model.geom("part5").feature("pc2").set("contributeto", "csel4");
                model.geom("part5").feature("pc2").set("parmin", "rev_cuff_LN*(0.75/2.5)");
                model.geom("part5").feature("pc2").set("parmax", "rev_cuff_LN*((0.75+1)/2.5)");
                model.geom("part5").feature("pc2")
                        .set("coord", new String[]{"cos(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "sin(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "Center+(L_cuff_LN)*(s/rev_cuff_LN)-(L_cuff_LN/2)"});
                model.geom("part5").create("swe2", "Sweep");
                model.geom("part5").feature("swe2").label("Make Cuff Part 2");
                model.geom("part5").feature("swe2").set("contributeto", "csel5");
                model.geom("part5").feature("swe2").set("crossfaces", true);
                model.geom("part5").feature("swe2").set("includefinal", false);
                model.geom("part5").feature("swe2").set("twistcomp", false);
                model.geom("part5").feature("swe2").selection("face").named("wp2_csel1");
                model.geom("part5").feature("swe2").selection("edge").named("csel4");
                model.geom("part5").feature("swe2").selection("diredge").set("pc2(1)", 1);
                model.geom("part5").create("swe3", "Sweep");
                model.geom("part5").feature("swe3").label("Make Conductor Part 2");
                model.geom("part5").feature("swe3").set("contributeto", "csel6");
                model.geom("part5").feature("swe3").set("crossfaces", true);
                model.geom("part5").feature("swe3").set("keep", false);
                model.geom("part5").feature("swe3").set("includefinal", false);
                model.geom("part5").feature("swe3").set("twistcomp", false);
                model.geom("part5").feature("swe3").selection("face").named("wp3_csel2");
                model.geom("part5").feature("swe3").selection("edge").named("csel4");
                model.geom("part5").feature("swe3").selection("diredge").set("pc2(1)", 1);
                model.geom("part5").create("ballsel2", "BallSelection");
                model.geom("part5").feature("ballsel2").set("entitydim", 2);
                model.geom("part5").feature("ballsel2").label("Select End Face Part 2");
                model.geom("part5").feature("ballsel2")
                        .set("posx", "cos(2*pi*rev_cuff_LN*((0.75+1)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                model.geom("part5").feature("ballsel2")
                        .set("posy", "sin(2*pi*rev_cuff_LN*((0.75+1)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                model.geom("part5").feature("ballsel2")
                        .set("posz", "Center+(L_cuff_LN)*(rev_cuff_LN*((0.75+1)/2.5)/rev_cuff_LN)-(L_cuff_LN/2)");
                model.geom("part5").feature("ballsel2").set("r", 1);
                model.geom("part5").feature("ballsel2").set("contributeto", "csel7");
                model.geom("part5").create("wp4", "WorkPlane");
                model.geom("part5").feature("wp4").label("Helical Insulator Cross Section Part 3");
                model.geom("part5").feature("wp4").set("planetype", "faceparallel");
                model.geom("part5").feature("wp4").set("unite", true);
                model.geom("part5").feature("wp4").selection("face").named("csel7");
                model.geom("part5").feature("wp4").geom().selection().create("csel1", "CumulativeSelection");
                model.geom("part5").feature("wp4").geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION P3");
                model.geom("part5").feature("wp4").geom().create("r1", "Rectangle");
                model.geom("part5").feature("wp4").geom().feature("r1").label("Helical Insulator Cross Section Part 3");
                model.geom("part5").feature("wp4").geom().feature("r1").set("contributeto", "csel1");
                model.geom("part5").feature("wp4").geom().feature("r1").set("base", "center");
                model.geom("part5").feature("wp4").geom().feature("r1").set("size", new String[]{"thk_cuff_LN", "w_cuff_LN"});
                model.geom("part5").create("pc3", "ParametricCurve");
                model.geom("part5").feature("pc3").label("Parametric Curve Part 3");
                model.geom("part5").feature("pc3").set("contributeto", "csel9");
                model.geom("part5").feature("pc3").set("parmin", "rev_cuff_LN*((0.75+1)/2.5)");
                model.geom("part5").feature("pc3").set("parmax", "rev_cuff_LN");
                model.geom("part5").feature("pc3")
                        .set("coord", new String[]{"cos(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "sin(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "Center+(L_cuff_LN)*(s/rev_cuff_LN)-(L_cuff_LN/2)"});
                model.geom("part5").create("swe4", "Sweep");
                model.geom("part5").feature("swe4").label("Make Cuff Part 3");
                model.geom("part5").feature("swe4").set("contributeto", "csel8");
                model.geom("part5").feature("swe4").selection("face").named("wp4_csel1");
                model.geom("part5").feature("swe4").selection("edge").named("csel9");
                model.geom("part5").feature("swe4").set("keep", false);
                model.geom("part5").feature("swe4").set("twistcomp", false);
                model.geom("part5").create("pt1", "Point");
                model.geom("part5").feature("pt1").label("src");
                model.geom("part5").feature("pt1").set("contributeto", "csel10");
                model.geom("part5").feature("pt1")
                        .set("p", new String[]{"cos(2*pi*rev_cuff_LN*(1.25/2.5))*((thk_elec_LN/2)+r_cuff_in_LN)", "sin(2*pi*rev_cuff_LN*(1.25/2.5))*((thk_elec_LN/2)+r_cuff_in_LN)", "Center"});
                model.geom("part5").run();
                break;
            case "RectangleContact_Primitive":
                model.geom().create("part6", "Part", 3);
                model.geom("part6").label("RectangleContact_Primitive");
                model.geom("part6").lengthUnit("\u00b5m");

                model.geom("part6").inputParam().set("r_inner_contact", "r_cuff_in_Pitt+recess_Pitt");
                model.geom("part6").inputParam().set("r_outer_contact", "r_cuff_in_Pitt+recess_Pitt+thk_contact_Pitt");
                model.geom("part6").inputParam().set("z_center", "0 [mm]");
                model.geom("part6").inputParam().set("rotation_angle", "0 [deg]");

                model.geom("part6").selection().create("csel11", "CumulativeSelection");
                model.geom("part6").selection("csel11").label("OUTER CONTACT CUTTER");
                model.geom("part6").selection().create("csel22", "CumulativeSelection");
                model.geom("part6").selection("csel22").label("SEL INNER EXCESS CONTACT");
                model.geom("part6").selection().create("csel10", "CumulativeSelection");
                model.geom("part6").selection("csel10").label("INNER CONTACT CUTTER");
                model.geom("part6").selection().create("csel21", "CumulativeSelection");
                model.geom("part6").selection("csel21").label("SEL OUTER EXCESS RECESS");
                model.geom("part6").selection().create("csel20", "CumulativeSelection");
                model.geom("part6").selection("csel20").label("SEL INNER EXCESS RECESS");
                model.geom("part6").selection().create("csel7", "CumulativeSelection");
                model.geom("part6").selection("csel7").label("OUTER CUTTER");
                model.geom("part6").selection().create("csel15", "CumulativeSelection");
                model.geom("part6").selection("csel15").label("FINAL RECESS");
                model.geom("part6").selection().create("csel8", "CumulativeSelection");
                model.geom("part6").selection("csel8").label("RECESS CROSS SECTION");
                model.geom("part6").selection().create("csel14", "CumulativeSelection");
                model.geom("part6").selection("csel14").label("OUTER RECESS CUTTER");
                model.geom("part6").selection().create("csel9", "CumulativeSelection");
                model.geom("part6").selection("csel9").label("RECESS PRE CUTS");
                model.geom("part6").selection().create("csel13", "CumulativeSelection");
                model.geom("part6").selection("csel13").label("INNER RECESS CUTTER");
                model.geom("part6").selection().create("csel12", "CumulativeSelection");
                model.geom("part6").selection("csel12").label("FINAL CONTACT");
                model.geom("part6").selection().create("csel23", "CumulativeSelection");
                model.geom("part6").selection("csel23").label("SEL OUTER EXCESS CONTACT");
                model.geom("part6").selection().create("csel19", "CumulativeSelection");
                model.geom("part6").selection("csel19").label("SEL OUTER EXCESS");
                model.geom("part6").selection().create("csel18", "CumulativeSelection");
                model.geom("part6").selection("csel18").label("SEL INNER EXCESS");
                model.geom("part6").selection().create("csel17", "CumulativeSelection");
                model.geom("part6").selection("csel17").label("BASE CONTACT PLANE (PRE ROTATION)");
                model.geom("part6").selection().create("csel16", "CumulativeSelection");
                model.geom("part6").selection("csel16").label("SRC");
                model.geom("part6").selection().create("csel1", "CumulativeSelection");
                model.geom("part6").selection("csel1").label("CONTACT PRE CUTS");
                model.geom("part6").selection().create("csel2", "CumulativeSelection");
                model.geom("part6").selection("csel2").label("CONTACT CROSS SECTION");
                model.geom("part6").selection().create("csel3", "CumulativeSelection");
                model.geom("part6").selection("csel3").label("INNER CUFF CUTTER");
                model.geom("part6").selection().create("csel4", "CumulativeSelection");
                model.geom("part6").selection("csel4").label("OUTER CUFF CUTTER");
                model.geom("part6").selection().create("csel5", "CumulativeSelection");
                model.geom("part6").selection("csel5").label("FINAL");
                model.geom("part6").selection().create("csel6", "CumulativeSelection");
                model.geom("part6").selection("csel6").label("INNER CUTTER");

                model.geom("part6").create("wp3", "WorkPlane");
                model.geom("part6").feature("wp3").label("base plane (pre rotation)");
                model.geom("part6").feature("wp3").set("contributeto", "csel17");
                model.geom("part6").feature("wp3").set("quickplane", "yz");
                model.geom("part6").feature("wp3").set("unite", true);
                model.geom("part6").create("wp1", "WorkPlane");
                model.geom("part6").feature("wp1").label("Contact Cross Section");
                model.geom("part6").feature("wp1").set("contributeto", "csel2");
                model.geom("part6").feature("wp1").set("planetype", "transformed");
                model.geom("part6").feature("wp1").set("workplane", "wp3");
                model.geom("part6").feature("wp1").set("transaxis", new int[]{0, 1, 0});
                model.geom("part6").feature("wp1").set("transrot", "rotation_angle");
                model.geom("part6").feature("wp1").set("unite", true);
                model.geom("part6").feature("wp1").geom().selection().create("csel1", "CumulativeSelection");
                model.geom("part6").feature("wp1").geom().selection("csel1").label("CONTACT PRE FILLET");
                model.geom("part6").feature("wp1").geom().selection().create("csel2", "CumulativeSelection");
                model.geom("part6").feature("wp1").geom().selection("csel2").label("CONTACT FILLETED");
                model.geom("part6").feature("wp1").geom().create("r1", "Rectangle");
                model.geom("part6").feature("wp1").geom().feature("r1").label("Contact Pre Fillet Corners");
                model.geom("part6").feature("wp1").geom().feature("r1").set("contributeto", "csel1");
                model.geom("part6").feature("wp1").geom().feature("r1").set("pos", new int[]{0, 0});
                model.geom("part6").feature("wp1").geom().feature("r1").set("base", "center");
                model.geom("part6").feature("wp1").geom().feature("r1").set("size", new String[]{"w_contact_Pitt", "z_contact_Pitt"});
                model.geom("part6").feature("wp1").geom().create("fil1", "Fillet");
                model.geom("part6").feature("wp1").geom().feature("fil1").label("Fillet Corners");
                model.geom("part6").feature("wp1").geom().feature("fil1").set("contributeto", "csel2");
                model.geom("part6").feature("wp1").geom().feature("fil1").set("radius", "fillet_contact_Pitt");
                model.geom("part6").feature("wp1").geom().feature("fil1").selection("point").named("csel1");
                model.geom("part6").feature("wp1").geom().create("sca1", "Scale");
                model.geom("part6").feature("wp1").geom().feature("sca1").set("type", "anisotropic");
                model.geom("part6").feature("wp1").geom().feature("sca1")
                        .set("factor", new String[]{"1", "scale_morph_w_contact_Pitt"});
                model.geom("part6").feature("wp1").geom().feature("sca1").selection("input").named("csel2");
                model.geom("part6").feature("wp1").geom().create("mov1", "Move");
                model.geom("part6").feature("wp1").geom().feature("mov1").set("disply", "z_center");
                model.geom("part6").feature("wp1").geom().feature("mov1").selection("input").named("csel2");
                model.geom("part6").create("ext1", "Extrude");
                model.geom("part6").feature("ext1").label("Make Contact Pre Cuts");
                model.geom("part6").feature("ext1").set("contributeto", "csel1");
                model.geom("part6").feature("ext1").setIndex("distance", "2*r_cuff_in_Pitt", 0);
                model.geom("part6").feature("ext1").selection("input").named("csel2");
                model.geom("part6").create("cyl1", "Cylinder");
                model.geom("part6").feature("cyl1").label("Inner Contact Cutter");
                model.geom("part6").feature("cyl1").set("contributeto", "csel10");
                model.geom("part6").feature("cyl1").set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                model.geom("part6").feature("cyl1").set("r", "r_inner_contact");
                model.geom("part6").feature("cyl1").set("h", "L_cuff_Pitt");
                model.geom("part6").create("cyl2", "Cylinder");
                model.geom("part6").feature("cyl2").label("Outer Contact Cutter");
                model.geom("part6").feature("cyl2").set("contributeto", "csel11");
                model.geom("part6").feature("cyl2").set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                model.geom("part6").feature("cyl2").set("r", "r_outer_contact");
                model.geom("part6").feature("cyl2").set("h", "L_cuff_Pitt");
                model.geom("part6").create("par1", "Partition");
                model.geom("part6").feature("par1").set("contributeto", "csel12");
                model.geom("part6").feature("par1").selection("input").named("csel1");
                model.geom("part6").feature("par1").selection("tool").named("csel11");
                model.geom("part6").create("par2", "Partition");
                model.geom("part6").feature("par2").set("contributeto", "csel12");
                model.geom("part6").feature("par2").selection("input").named("csel1");
                model.geom("part6").feature("par2").selection("tool").named("csel10");
                model.geom("part6").create("ballsel1", "BallSelection");
                model.geom("part6").feature("ballsel1").label("sel inner excess");
                model.geom("part6").feature("ballsel1").set("posx", "(r_inner_contact/2)*cos(rotation_angle)");
                model.geom("part6").feature("ballsel1").set("posy", "(r_inner_contact/2)*sin(rotation_angle)");
                model.geom("part6").feature("ballsel1").set("posz", "z_center");
                model.geom("part6").feature("ballsel1").set("r", 1);
                model.geom("part6").feature("ballsel1").set("contributeto", "csel22");
                model.geom("part6").create("ballsel2", "BallSelection");
                model.geom("part6").feature("ballsel2").label("sel outer excess");
                model.geom("part6").feature("ballsel2").set("posx", "((r_outer_contact+2*r_cuff_in_Pitt)/2)*cos(rotation_angle)");
                model.geom("part6").feature("ballsel2").set("posy", "((r_outer_contact+2*r_cuff_in_Pitt)/2)*sin(rotation_angle)");
                model.geom("part6").feature("ballsel2").set("posz", "z_center");
                model.geom("part6").feature("ballsel2").set("r", 1);
                model.geom("part6").feature("ballsel2").set("contributeto", "csel23");
                model.geom("part6").create("del1", "Delete");
                model.geom("part6").feature("del1").label("Delete Inner Excess Contact");
                model.geom("part6").feature("del1").selection("input").init(3);
                model.geom("part6").feature("del1").selection("input").named("csel22");
                model.geom("part6").create("del3", "Delete");
                model.geom("part6").feature("del3").label("Delete Outer Excess Contact");
                model.geom("part6").feature("del3").selection("input").init(3);
                model.geom("part6").feature("del3").selection("input").named("csel23");
                model.geom("part6").create("if1", "If");
                model.geom("part6").feature("if1").set("condition", "recess_Pitt>0");
                model.geom("part6").create("wp2", "WorkPlane");
                model.geom("part6").feature("wp2").label("Recess Cross Section");
                model.geom("part6").feature("wp2").set("contributeto", "csel8");
                model.geom("part6").feature("wp2").set("planetype", "transformed");
                model.geom("part6").feature("wp2").set("workplane", "wp3");
                model.geom("part6").feature("wp2").set("transaxis", new int[]{0, 1, 0});
                model.geom("part6").feature("wp2").set("transrot", "rotation_angle");
                model.geom("part6").feature("wp2").set("unite", true);
                model.geom("part6").feature("wp2").geom().selection().create("csel1", "CumulativeSelection");
                model.geom("part6").feature("wp2").geom().selection("csel1").label("CONTACT PRE FILLET");
                model.geom("part6").feature("wp2").geom().selection().create("csel2", "CumulativeSelection");
                model.geom("part6").feature("wp2").geom().selection("csel2").label("CONTACT FILLETED");
                model.geom("part6").feature("wp2").geom().selection().create("csel3", "CumulativeSelection");
                model.geom("part6").feature("wp2").geom().selection("csel3").label("RECESS PRE FILLET");
                model.geom("part6").feature("wp2").geom().selection().create("csel4", "CumulativeSelection");
                model.geom("part6").feature("wp2").geom().selection("csel4").label("RECESS FILLETED");
                model.geom("part6").feature("wp2").geom().create("r1", "Rectangle");
                model.geom("part6").feature("wp2").geom().feature("r1").label("Recess Pre Fillet Corners");
                model.geom("part6").feature("wp2").geom().feature("r1").set("contributeto", "csel3");
                model.geom("part6").feature("wp2").geom().feature("r1").set("pos", new int[]{0, 0});
                model.geom("part6").feature("wp2").geom().feature("r1").set("base", "center");
                model.geom("part6").feature("wp2").geom().feature("r1").set("size", new String[]{"w_contact_Pitt", "z_contact_Pitt"});
                model.geom("part6").feature("wp2").geom().create("fil1", "Fillet");
                model.geom("part6").feature("wp2").geom().feature("fil1").label("Fillet Corners");
                model.geom("part6").feature("wp2").geom().feature("fil1").set("contributeto", "csel4");
                model.geom("part6").feature("wp2").geom().feature("fil1").set("radius", "fillet_contact_Pitt");
                model.geom("part6").feature("wp2").geom().feature("fil1").selection("point").named("csel3");
                model.geom("part6").feature("wp2").geom().create("sca1", "Scale");
                model.geom("part6").feature("wp2").geom().feature("sca1").set("type", "anisotropic");
                model.geom("part6").feature("wp2").geom().feature("sca1")
                        .set("factor", new String[]{"1", "scale_morph_w_contact_Pitt"});
                model.geom("part6").feature("wp2").geom().feature("sca1").selection("input").named("csel4");
                model.geom("part6").feature("wp2").geom().create("mov1", "Move");
                model.geom("part6").feature("wp2").geom().feature("mov1").set("disply", "z_center");
                model.geom("part6").feature("wp2").geom().feature("mov1").selection("input").named("csel4");
                model.geom("part6").create("ext2", "Extrude");
                model.geom("part6").feature("ext2").label("Make Recess Pre Cuts 1");
                model.geom("part6").feature("ext2").set("contributeto", "csel9");
                model.geom("part6").feature("ext2").setIndex("distance", "2*r_cuff_in_Pitt", 0);
                model.geom("part6").feature("ext2").selection("input").named("csel8");
                model.geom("part6").create("cyl3", "Cylinder");
                model.geom("part6").feature("cyl3").label("Inner Recess Cutter");
                model.geom("part6").feature("cyl3").set("contributeto", "csel13");
                model.geom("part6").feature("cyl3").set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                model.geom("part6").feature("cyl3").set("r", "r_cuff_in_Pitt");
                model.geom("part6").feature("cyl3").set("h", "L_cuff_Pitt");
                model.geom("part6").create("cyl4", "Cylinder");
                model.geom("part6").feature("cyl4").label("Outer Recess Cutter");
                model.geom("part6").feature("cyl4").set("contributeto", "csel14");
                model.geom("part6").feature("cyl4").set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                model.geom("part6").feature("cyl4").set("r", "r_inner_contact");
                model.geom("part6").feature("cyl4").set("h", "L_cuff_Pitt");
                model.geom("part6").create("par3", "Partition");
                model.geom("part6").feature("par3").set("contributeto", "csel15");
                model.geom("part6").feature("par3").selection("input").named("csel9");
                model.geom("part6").feature("par3").selection("tool").named("csel14");
                model.geom("part6").create("par4", "Partition");
                model.geom("part6").feature("par4").set("contributeto", "csel15");
                model.geom("part6").feature("par4").selection("input").named("csel9");
                model.geom("part6").feature("par4").selection("tool").named("csel13");
                model.geom("part6").create("ballsel3", "BallSelection");
                model.geom("part6").feature("ballsel3").label("sel inner excess 1");
                model.geom("part6").feature("ballsel3").set("posx", "((r_inner_contact+recess_Pitt)/2)*cos(rotation_angle)");
                model.geom("part6").feature("ballsel3").set("posy", "((r_inner_contact+recess_Pitt)/2)*sin(rotation_angle)");
                model.geom("part6").feature("ballsel3").set("posz", "z_center");
                model.geom("part6").feature("ballsel3").set("r", 1);
                model.geom("part6").feature("ballsel3").set("contributeto", "csel20");
                model.geom("part6").create("ballsel4", "BallSelection");
                model.geom("part6").feature("ballsel4").label("sel outer excess 1");
                model.geom("part6").feature("ballsel4").set("posx", "((r_cuff_in_Pitt+2*r_cuff_in_Pitt)/2)*cos(rotation_angle)");
                model.geom("part6").feature("ballsel4").set("posy", "((r_cuff_in_Pitt+2*r_cuff_in_Pitt)/2)*sin(rotation_angle)");
                model.geom("part6").feature("ballsel4").set("posz", "z_center");
                model.geom("part6").feature("ballsel4").set("r", 1);
                model.geom("part6").feature("ballsel4").set("contributeto", "csel21");
                model.geom("part6").create("del4", "Delete");
                model.geom("part6").feature("del4").label("Delete Inner Excess Recess");
                model.geom("part6").feature("del4").selection("input").init(3);
                model.geom("part6").feature("del4").selection("input").named("csel20");
                model.geom("part6").create("del5", "Delete");
                model.geom("part6").feature("del5").label("Delete Outer Excess Recess");
                model.geom("part6").feature("del5").selection("input").init(3);
                model.geom("part6").feature("del5").selection("input").named("csel21");
                model.geom("part6").create("endif1", "EndIf");
                model.geom("part6").create("pt1", "Point");
                model.geom("part6").feature("pt1").label("src");
                model.geom("part6").feature("pt1").set("contributeto", "csel16");
                model.geom("part6").feature("pt1")
                        .set("p", new String[]{"(r_cuff_in_Pitt+recess_Pitt+(thk_contact_Pitt/2))*cos(rotation_angle)", "(r_cuff_in_Pitt+recess_Pitt+(thk_contact_Pitt/2))*sin(rotation_angle)", "z_center"});
                model.geom("part6").run();
                break;
            default:
                throw new IllegalStateException("Unexpected value: " + psuedonym);
        }
        return true;
    }

    /**
     *
     * @param id
     * @param psuedonym
     * @param model
     * @param partPrimitives
     * @param data
     * @return
     */
    public static boolean createPartInstance(String id, String psuedonym, Model model,
                                             HashMap<String, String> partPrimitives, HashMap<String, Object> data) {

        model.component().create("comp1", true);
        model.component("comp1").geom().create("geom1", 3);
        model.component("comp1").mesh().create("mesh1");

        switch (psuedonym) {



        }

        return true;
    }
}

package model;

import com.comsol.model.Model;

import java.util.HashMap;

class Part {
    public static boolean createPartPrimitive(String id, String pseudonym, Model model) {

        return createPartPrimitive(id, pseudonym, model, null);
    }

    public static boolean createPartInstance(String id, String pseudonym, Model model,
                                             HashMap<String, String> partPrimitives) {
        return createPartInstance(id, pseudonym, model, partPrimitives, null);
    }

    /**
     *
     * @param id
     * @param pseudonym
     * @param model
     * @param data
     * @return
     */
    public static boolean createPartPrimitive(String id, String pseudonym, ModelWrapper2 mw,
                                              HashMap<String, Object> data) {
        Model model = mw.getModel();

        model.geom().create(id, "Part", 3);
        model.geom(id).label(pseudonym);
        model.geom(id).lengthUnit("\u00b5m");

        switch (pseudonym) {
            case "TubeCuff_Primitive":
                model.geom(id).inputParam().set("N_holes", "1");
                model.geom(id).inputParam().set("Theta", "340 [deg]");
                model.geom(id).inputParam().set("Center", "10 [mm]");
                model.geom(id).inputParam().set("R_in", "1 [mm]");
                model.geom(id).inputParam().set("R_out", "2 [mm]");
                model.geom(id).inputParam().set("L", "5 [mm]");
                model.geom(id).inputParam().set("Rot_def", "0 [deg]");
                model.geom(id).inputParam().set("D_hole", "0.3 [mm]");
                model.geom(id).inputParam().set("Buffer_hole", "0.1 [mm]");
                model.geom(id).inputParam().set("L_holecenter_cuffseam", "0.3 [mm]");
                model.geom(id).inputParam().set("Pitch_holecenter_holecenter", "0 [mm]");

                model.geom(id).selection().create(mw.nextID("csel", "INNER CUFF SURFACE"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("INNER CUFF SURFACE")).label("INNER CUFF SURFACE");
                model.geom(id).selection().create(mw.nextID("csel","OUTER CUFF SURFACE"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("OUTER CUFF SURFACE")).label("OUTER CUFF SURFACE");
                model.geom(id).selection().create(mw.nextID("csel","CUFF FINAL"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("CUFF FINAL")).label("CUFF FINAL");
                model.geom(id).selection().create(mw.nextID("csel","CUFF wGAP PRE HOLES"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("CUFF wGAP PRE HOLES")).label("CUFF wGAP PRE HOLES");
                model.geom(id).selection().create(mw.nextID("csel","CUFF PRE GAP"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("CUFF PRE GAP")).label("CUFF PRE GAP");
                model.geom(id).selection().create(mw.nextID("csel","CUFF PRE GAP PRE HOLES"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("CUFF PRE GAP PRE HOLES")).label("CUFF PRE GAP PRE HOLES");
                model.geom(id).selection().create(mw.nextID("csel","CUFF GAP CROSS SECTION"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("CUFF GAP CROSS SECTION")).label("CUFF GAP CROSS SECTION");
                model.geom(id).selection().create(mw.nextID("csel","CUFF GAP"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("CUFF GAP")).label("CUFF GAP");
                model.geom(id).selection().create(mw.nextID("csel","CUFF PRE HOLES"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("CUFF PRE HOLES")).label("CUFF PRE HOLES");
                model.geom(id).selection().create(mw.nextID("csel","HOLE 1"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("HOLE 1")).label("HOLE 1");
                model.geom(id).selection().create(mw.nextID("csel","HOLES"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("HOLES")).label("HOLES");

                model.geom(id).create(mw.nextID("cyl","Make Inner Cuff Surface"), "Cylinder");
                model.geom(id).feature(mw.getID("Make Inner Cuff Surface")).label("Make Inner Cuff Surface");
                model.geom(id).feature(mw.getID("Make Inner Cuff Surface")).set("contributeto", mw.getID("INNER CUFF SURFACE"));
                model.geom(id).feature(mw.getID("Make Inner Cuff Surface")).set("pos", new String[]{"0", "0", "Center-(L/2)"});
                model.geom(id).feature(mw.getID("Make Inner Cuff Surface")).set("r", "R_in");
                model.geom(id).feature(mw.getID("Make Inner Cuff Surface")).set("h", "L");

                model.geom(id).create(mw.nextID("cyl","Make Outer Cuff Surface"), "Cylinder");
                model.geom(id).feature(mw.getID("Make Outer Cuff Surface")).label("Make Outer Cuff Surface");
                model.geom(id).feature(mw.getID("Make Outer Cuff Surface")).set("contributeto", mw.getID("OUTER CUFF SURFACE"));
                model.geom(id).feature(mw.getID("Make Outer Cuff Surface")).set("pos", new String[]{"0", "0", "Center-(L/2)"});
                model.geom(id).feature(mw.getID("Make Outer Cuff Surface")).set("r", "R_out");
                model.geom(id).feature(mw.getID("Make Outer Cuff Surface")).set("h", "L");

                model.geom(id).create(mw.nextID("if", "If (No Gap AND No Holes)"), "If");
                model.geom(id).feature(mw.getID("If (No Gap AND No Holes)")).label("If (No Gap AND No Holes)");
                model.geom(id).feature(mw.getID("If (No Gap AND No Holes)")).set("condition", "(Theta==360) && (N_holes==0)");

                model.geom(id).create(mw.nextID("dif", "Remove Domain Within Inner Cuff Surface"), "Difference");
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface")).label("Remove Domain Within Inner Cuff Surface");
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface")).set("contributeto", "csel3");
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface")).selection("input").named(mw.getID("OUTER CUFF SURFACE"));
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface")).selection("input2").named(mw.getID("INNER CUFF SURFACE"));

                model.geom(id).create(mw.nextID("elseif","If (Gap       AND No Holes)"), "ElseIf");
                model.geom(id).feature(mw.getID("If (Gap       AND No Holes)")).label("If (Gap       AND No Holes)");
                model.geom(id).feature(mw.getID("If (Gap       AND No Holes)")).set("condition", "(Theta<360) && (N_holes==0)");

                model.geom(id).create(mw.nextID("dif","Remove Domain Within Inner Cuff Surface 1"), "Difference");
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface 1")).label("Remove Domain Within Inner Cuff Surface 1");
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface 1")).set("contributeto", "csel4");
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface 1")).selection("input").named(mw.getID("OUTER CUFF SURFACE"));
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface 1")).selection("input2").named(mw.getID("INNER CUFF SURFACE"));

                model.geom(id).create(mw.nextID("wp","Make Cuff Gap Cross Section"), "WorkPlane");
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section")).label("Make Cuff Gap Cross Section");
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section")).set("contributeto", mw.getID("CUFF GAP CROSS SECTION"));
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section")).set("quickplane", "xz");
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section")).set("unite", true);
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section")).geom().create("r1", "Rectangle");
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section")).geom().feature("r1").label("Cuff Gap Cross Section");
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section")).geom().feature("r1")
                        .set("pos", new String[]{"R_in+((R_out-R_in)/2)", "Center"});
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section")).geom().feature("r1").set("base", "center");
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section")).geom().feature("r1").set("size", new String[]{"R_out-R_in", "L"});

                model.geom(id).create(mw.nextID("rev","Make Cuff Gap"), "Revolve");
                model.geom(id).feature(mw.getID("Make Cuff Gap")).label("Make Cuff Gap");
                model.geom(id).feature(mw.getID("Make Cuff Gap")).set("contributeto", mw.getID("CUFF GAP"));
                model.geom(id).feature(mw.getID("Make Cuff Gap")).set("angle1", "Theta");
                model.geom(id).feature(mw.getID("Make Cuff Gap")).selection("input").set(mw.getID("Make Cuff Gap Cross Section"));

                model.geom(id).create(mw.nextID("dif","Remove Cuff Gap"), "Difference");
                model.geom(id).feature(mw.getID("Remove Cuff Gap")).label("Remove Cuff Gap");
                model.geom(id).feature(mw.getID("Remove Cuff Gap")).set("contributeto", mw.getID("CUFF FINAL"));
                model.geom(id).feature(mw.getID("Remove Cuff Gap")).selection("input").named(mw.getID("CUFF PRE GAP"));
                model.geom(id).feature(mw.getID("Remove Cuff Gap")).selection("input2").named(mw.getID("CUFF GAP"));

                model.geom(id).create(mw.nextID("rot","Rotate to Default Conformation 1"), "Rotate");
                model.geom(id).feature(mw.getID("Rotate to Default Conformation 1")).label("Rotate to Default Conformation 1");
                model.geom(id).feature(mw.getID("Rotate to Default Conformation 1")).set("rot", "Rot_def");
                model.geom(id).feature(mw.getID("Rotate to Default Conformation 1")).selection("input").named(mw.getID("CUFF FINAL"));

                model.geom(id).create(mw.nextID("elseif","If (No Gap AND       Holes)"), "ElseIf");
                model.geom(id).feature(mw.getID("If (No Gap AND       Holes)")).label("If (No Gap AND       Holes)");
                model.geom(id).feature(mw.getID("If (No Gap AND       Holes)")).set("condition", "(Theta==360) && (N_holes>0)");

                model.geom(id).create(mw.nextID("dif","Remove Domain Within Inner Cuff Surface 2"), "Difference");
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface 2")).label("Remove Domain Within Inner Cuff Surface 2");
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface 2")).set("contributeto", mw.getID("CUFF PRE HOLES"));
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface 2")).selection("input").named(mw.getID("OUTER CUFF SURFACE"));
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface 2")).selection("input2").named(mw.getID("INNER CUFF SURFACE"));

                model.geom(id).create(mw.nextID("econ","Make Hole Shape"), "ECone");
                model.geom(id).feature(mw.getID("Make Hole Shape")).label("Make Hole Shape");
                model.geom(id).feature(mw.getID("Make Hole Shape")).set("contributeto", mw.getID("HOLES"));
                model.geom(id).feature(mw.getID("Make Hole Shape"))
                        .set("pos", new String[]{"R_in-Buffer_hole/2", "0", "Center+Pitch_holecenter_holecenter/2"});
                model.geom(id).feature(mw.getID("Make Hole Shape")).set("axis", new int[]{1, 0, 0});
                model.geom(id).feature(mw.getID("Make Hole Shape")).set("semiaxes", new String[]{"D_hole/2", "D_hole/2"});
                model.geom(id).feature(mw.getID("Make Hole Shape")).set("h", "(R_out-R_in)+Buffer_hole");
                model.geom(id).feature(mw.getID("Make Hole Shape")).set("rat", "R_out/R_in");

                model.geom(id).create(mw.nextID("rot","Position Hole in Cuff"), "Rotate");
                model.geom(id).feature(mw.getID("Position Hole in Cuff")).label("Position Hole in Cuff");
                model.geom(id).feature(mw.getID("Position Hole in Cuff")).set("rot", "(360*L_holecenter_cuffseam)/(pi*2*R_in)");
                model.geom(id).feature(mw.getID("Position Hole in Cuff")).selection("input").named(mw.getID("HOLES"));

                model.geom(id).create(mw.nextID("dif","Make Inner Cuff Hole"), "Difference");
                model.geom(id).feature(mw.getID("Make Inner Cuff Hole")).label("Make Inner Cuff Hole");
                model.geom(id).feature(mw.getID("Make Inner Cuff Hole")).set("contributeto", mw.getID("CUFF FINAL"));
                model.geom(id).feature(mw.getID("Make Inner Cuff Hole")).selection("input").named(mw.getID("CUFF PRE HOLES"));
                model.geom(id).feature(mw.getID("Make Inner Cuff Hole")).selection("input2").named(mw.getID("HOLES"));

                model.geom(id).create(mw.nextID("elseif","If (      Gap AND       Holes)"), "ElseIf");
                model.geom(id).feature(mw.getID("If (      Gap AND       Holes)")).label("If (      Gap AND       Holes)");
                model.geom(id).feature(mw.getID("If (      Gap AND       Holes)")).set("condition", "(Theta<360) && (N_holes>0)");

                model.geom(id).create(mw.nextID("dif","Remove Domain Within Inner Cuff Surface 3"), "Difference");
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface 3")).label("Remove Domain Within Inner Cuff Surface 3");
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface 3")).set("contributeto", mw.getID("CUFF PRE GAP PRE HOLES"));
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface 3")).selection("input").named(mw.getID("OUTER CUFF SURFACE"));
                model.geom(id).feature(mw.getID("Remove Domain Within Inner Cuff Surface 3")).selection("input2").named(mw.getID("INNER CUFF SURFACE"));

                model.geom(id).create(mw.nextID("wp","Make Cuff Gap Cross Section 1"), "WorkPlane");
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section 1")).label("Make Cuff Gap Cross Section 1");
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section 1")).set("contributeto", mw.getID("CUFF GAP CROSS SECTION"));
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section 1")).set("quickplane", "xz");
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section 1")).set("unite", true);
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section 1")).geom().create("r1", "Rectangle");
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section 1")).geom().feature("r1").label("Cuff Gap Cross Section");
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section 1")).geom().feature("r1")
                        .set("pos", new String[]{"R_in+((R_out-R_in)/2)", "Center"});
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section 1")).geom().feature("r1").set("base", "center");
                model.geom(id).feature(mw.getID("Make Cuff Gap Cross Section 1")).geom().feature("r1").set("size", new String[]{"R_out-R_in", "L"});

                model.geom(id).create(mw.nextID("rev","Make Cuff Gap 1"), "Revolve");
                model.geom(id).feature(mw.getID("Make Cuff Gap 1")).label("Make Cuff Gap 1");
                model.geom(id).feature(mw.getID("Make Cuff Gap 1")).set("contributeto", mw.getID("CUFF GAP"));
                model.geom(id).feature(mw.getID("Make Cuff Gap 1")).set("angle1", "Theta");
                model.geom(id).feature(mw.getID("Make Cuff Gap 1")).selection("input").named(mw.getID("CUFF GAP CROSS SECTION"));

                model.geom(id).create(mw.nextID("dif","Remove Cuff Gap 1"), "Difference");
                model.geom(id).feature(mw.getID("Remove Cuff Gap 1")).label("Remove Cuff Gap 1");
                model.geom(id).feature(mw.getID("Remove Cuff Gap 1")).set("contributeto", mw.getID("CUFF wGAP PRE HOLES"));
                model.geom(id).feature(mw.getID("Remove Cuff Gap 1")).selection("input").named(mw.getID("CUFF PRE GAP PRE HOLES"));
                model.geom(id).feature(mw.getID("Remove Cuff Gap 1")).selection("input2").named(mw.getID("CUFF GAP"));

                model.geom(id).create(mw.nextID("econ","Make Hole Shape 1"), "ECone");
                model.geom(id).feature(mw.getID("Make Hole Shape 1")).label("Make Hole Shape 1");
                model.geom(id).feature(mw.getID("Make Hole Shape 1")).set("contributeto", mw.getID("HOLES"));
                model.geom(id).feature(mw.getID("Make Hole Shape 1"))
                        .set("pos", new String[]{"R_in-Buffer_hole/2", "0", "Center+Pitch_holecenter_holecenter/2"});
                model.geom(id).feature(mw.getID("Make Hole Shape 1")).set("axis", new int[]{1, 0, 0});
                model.geom(id).feature(mw.getID("Make Hole Shape 1")).set("semiaxes", new String[]{"D_hole/2", "D_hole/2"});
                model.geom(id).feature(mw.getID("Make Hole Shape 1")).set("h", "(R_out-R_in)+Buffer_hole");
                model.geom(id).feature(mw.getID("Make Hole Shape 1")).set("rat", "R_out/R_in");

                model.geom(id).create(mw.nextID("rot","Position Hole in Cuff 1"), "Rotate");
                model.geom(id).feature(mw.getID("Position Hole in Cuff 1")).label("Position Hole in Cuff 1");
                model.geom(id).feature(mw.getID("Position Hole in Cuff 1")).set("rot", "(360*L_holecenter_cuffseam)/(pi*2*R_in)");
                model.geom(id).feature(mw.getID("Position Hole in Cuff 1")).selection("input").named(mw.getID("HOLES"));

                model.geom(id).create(mw.nextID("dif","Make Inner Cuff Hole 1"), "Difference");
                model.geom(id).feature(mw.getID("Make Inner Cuff Hole 1")).label("Make Inner Cuff Hole 1");
                model.geom(id).feature(mw.getID("Make Inner Cuff Hole 1")).set("contributeto", mw.getID("CUFF FINAL"));
                model.geom(id).feature(mw.getID("Make Inner Cuff Hole 1")).selection("input").named(mw.getID("CUFF wGAP PRE HOLES"));
                model.geom(id).feature(mw.getID("Make Inner Cuff Hole 1")).selection("input2").named(mw.getID("HOLES"));

                model.geom(id).create(mw.nextID("rot","Rotate to Default Conformation"), "Rotate");
                model.geom(id).feature(mw.getID("Rotate to Default Conformation")).label("Rotate to Default Conformation");
                model.geom(id).feature(mw.getID("Rotate to Default Conformation")).set("rot", "Rot_def");
                model.geom(id).feature(mw.getID("Rotate to Default Conformation")).selection("input").named(mw.getID("CUFF FINAL"));

                model.geom(id).create(mw.nextID("endif"), "EndIf");
                model.geom(id).run();
                break;
            case "RibbonContact_Primitive":
                model.geom(id).inputParam().set("Thk_elec", "0.1 [mm]");
                model.geom(id).inputParam().set("L_elec", "3 [mm]");
                model.geom(id).inputParam().set("R_in", "1 [mm]");
                model.geom(id).inputParam().set("Recess", "0.1 [mm]");
                model.geom(id).inputParam().set("Center", "10 [mm]");
                model.geom(id).inputParam().set("Theta_contact", "100 [deg]");
                model.geom(id).inputParam().set("Rot_def", "0 [deg]");

                model.geom(id).selection().create(mw.nextID("csel","CONTACT CROSS SECTION"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("CONTACT CROSS SECTION")).label("CONTACT CROSS SECTION");
                model.geom(id).selection().create(mw.nextID("csel","RECESS CROSS SECTION"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("RECESS CROSS SECTION")).label("RECESS CROSS SECTION");
                model.geom(id).selection().create(mw.nextID("csel","SRC"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("SRC")).label("SRC");
                model.geom(id).selection().create(mw.nextID("csel","CONTACT FINAL"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("CONTACT FINAL")).label("CONTACT FINAL");
                model.geom(id).selection().create(mw.nextID("csel","RECESS FINAL"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("RECESS FINAL")).label("RECESS FINAL");

                model.geom(id).create(mw.nextID("wp","Contact Cross Section"), "WorkPlane");
                model.geom(id).feature(mw.getID("Contact Cross Section")).label("Contact Cross Section");
                model.geom(id).feature(mw.getID("Contact Cross Section")).set("contributeto", mw.getID("CONTACT CROSS SECTION"));
                model.geom(id).feature(mw.getID("Contact Cross Section")).set("quickplane", "xz");
                model.geom(id).feature(mw.getID("Contact Cross Section")).set("unite", true);
                model.geom(id).feature(mw.getID("Contact Cross Section")).geom().create("r1", "Rectangle");
                model.geom(id).feature(mw.getID("Contact Cross Section")).geom().feature("r1").label("Contact Cross Section");
                model.geom(id).feature(mw.getID("Contact Cross Section")).geom().feature("r1")
                        .set("pos", new String[]{"R_in+Recess+Thk_elec/2", "Center"});
                model.geom(id).feature(mw.getID("Contact Cross Section")).geom().feature("r1").set("base", "center");
                model.geom(id).feature(mw.getID("Contact Cross Section")).geom().feature("r1").set("size", new String[]{"Thk_elec", "L_elec"});

                model.geom(id).create(mw.nextID("rev","Make Contact"), "Revolve");
                model.geom(id).feature(mw.getID("Make Contact")).label("Make Contact");
                model.geom(id).feature(mw.getID("Make Contact")).set("contributeto", mw.getID("CONTACT FINAL"));
                model.geom(id).feature(mw.getID("Make Contact")).set("angle1", "Rot_def");
                model.geom(id).feature(mw.getID("Make Contact")).set("angle2", "Rot_def+Theta_contact");
                model.geom(id).feature(mw.getID("Make Contact")).selection("input").named(mw.getID("CONTACT CROSS SECTION"));

                model.geom(id).create(mw.nextID("if","IF RECESS"), "If");
                model.geom(id).feature(mw.getID("IF RECESS")).set("condition", "Recess>0");
                model.geom(id).feature(mw.getID("IF RECESS")).label("IF RECESS"); // added this line

                model.geom(id).create(mw.nextID("wp","Recess Cross Section 1"), "WorkPlane");
                model.geom(id).feature(mw.getID("Recess Cross Section 1")).label("Recess Cross Section 1");
                model.geom(id).feature(mw.getID("Recess Cross Section 1")).set("contributeto", mw.getID(("RECESS CROSS SECTION"));
                model.geom(id).feature(mw.getID("Recess Cross Section 1")).set("quickplane", "xz");
                model.geom(id).feature(mw.getID("Recess Cross Section 1")).set("unite", true);
//                model.geom(id).feature(mw.getID("Recess Cross Section 1")).geom().selection().create("csel1", "CumulativeSelection");
//                model.geom(id).feature(mw.getID("Recess Cross Section 1")).geom().selection("csel1").label("Cumulative Selection 1");
//                model.geom(id).feature(mw.getID("Recess Cross Section 1")).geom().selection().create("csel2", "CumulativeSelection");
//                model.geom(id).feature(mw.getID("Recess Cross Section 1")).geom().selection("csel2").label("RECESS CROSS SECTION");
                model.geom(id).feature(mw.getID("Recess Cross Section 1")).geom().create("r1", "Rectangle");
                model.geom(id).feature(mw.getID("Recess Cross Section 1")).geom().feature("r1").label("Recess Cross Section");
                model.geom(id).feature(mw.getID("Recess Cross Section 1")).geom().feature("r1").set("contributeto", mw.getID("RECESS CROSS SECTION"));
                model.geom(id).feature(mw.getID("Recess Cross Section 1")).geom().feature("r1").set("pos", new String[]{"R_in+Recess/2", "Center"});
                model.geom(id).feature(mw.getID("Recess Cross Section 1")).geom().feature("r1").set("base", "center");
                model.geom(id).feature(mw.getID("Recess Cross Section 1")).geom().feature("r1").set("size", new String[]{"Recess", "L_elec"});

                model.geom(id).create(mw.nextID("rev","Make Recess"), "Revolve");
                model.geom(id).feature(mw.getID("Make Recess")).label("Make Recess");
                model.geom(id).feature(mw.getID("Make Recess")).set("contributeto", "csel5");
                model.geom(id).feature(mw.getID("Make Recess")).set("angle1", "Rot_def");
                model.geom(id).feature(mw.getID("Make Recess")).set("angle2", "Rot_def+Theta_contact");
                model.geom(id).feature(mw.getID("Make Recess")).selection("input").named(mw.getID("RECESS CROSS SECTION"));

                model.geom(id).create(mw.nextID("endif"), "EndIf"); // add label?

                model.geom(id).create(mw.nextID("pt","SRC"), "Point");
                model.geom(id).feature(mw.getID("SRC")).label("src");
                model.geom(id).feature(mw.getID("SRC")).set("contributeto", mw.getID("SRC")); // IMPORTANT: this is conflict between csel3 and pt1, how can we take care of this? better names maybe? since hashmaps are case sensitive this is an option
                model.geom(id).feature(mw.getID("SRC"))
                        .set("p", new String[]{"(R_in+Recess+Thk_elec/2)*cos(Rot_def+Theta_contact/2)", "(R_in+Recess+Thk_elec/2)*sin(Rot_def+Theta_contact/2)", "Center"});

                model.geom(id).run();
                break;
            case "WireContact_Primitive":
                model.geom(id).inputParam().set("R_conductor", "r_conductor_P");
                model.geom(id).inputParam().set("R_in", "R_in_P");
                model.geom(id).inputParam().set("Center", "Center_P");
                model.geom(id).inputParam().set("Pitch", "Pitch_P");
                model.geom(id).inputParam().set("Sep_conductor", "sep_conductor_P");
                model.geom(id).inputParam().set("Theta_conductor", "theta_conductor_P");

                model.geom(id).selection().create(mw.nextID("csel","CONTACT CROSS SECTION"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("CONTACT CROSS SECTION")).label("CONTACT CROSS SECTION");
                model.geom(id).selection().create(mw.nextID("csel","CONTACT FINAL"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("CONTACT FINAL")).label("CONTACT FINAL");
                model.geom(id).selection().create(mw.nextID("csel","SRC"), "CumulativeSelection");
                model.geom(id).selection(mw.getID("SRC")).label("SRC");

                model.geom(id).create(mw.nextID("wp","Contact Cross Section"), "WorkPlane");
                model.geom(id).feature(mw.getID("Contact Cross Section")).label("Contact Cross Section");
                model.geom(id).feature(mw.getID("Contact Cross Section")).set("contributeto", mw.getID("CONTACT CROSS SECTION"));
                model.geom(id).feature(mw.getID("Contact Cross Section").set("quickplane", "zx");
                model.geom(id).feature(mw.getID("Contact Cross Section")).set("unite", true);
                model.geom(id).feature(mw.getID("Contact Cross Section")).geom().selection().create(mw.getID("CONTACT CROSS SECTION"), "CumulativeSelection");
                model.geom(id).feature(mw.getID("Contact Cross Section")).geom().selection(mw.getID("CONTACT CROSS SECTION")).label("CONTACT CROSS SECTION");
                model.geom(id).feature(mw.getID("Contact Cross Section")).geom().create("c1", "Circle");
                model.geom(id).feature(mw.getID("Contact Cross Section")).geom().feature("c1").label("Contact Cross Section");
                model.geom(id).feature(mw.getID("Contact Cross Section")).geom().feature("c1").set("contributeto", mw.getID("CONTACT CROSS SECTION"));
                model.geom(id).feature(mw.getID("Contact Cross Section")).geom().feature("c1")
                        .set("pos", new String[]{"Center", "R_in-R_conductor-Sep_conductor"});
                model.geom(id).feature(mw.getID("Contact Cross Section")).geom().feature("c1").set("r", "R_conductor");

                model.geom(id).create(mw.nextID("rev","Make Contact"), "Revolve");
                model.geom(id).feature(mw.getID("Make Contact")).label("Make Contact");
                model.geom(id).feature(mw.getID("Make Contact")).set("contributeto", mw.getID("CONTACT FINAL"));
                model.geom(id).feature(mw.getID("Make Contact")).set("angle2", "Theta_conductor");
                model.geom(id).feature(mw.getID("Make Contact")).set("axis", new int[]{1, 0});
                model.geom(id).feature(mw.getID("Make Contact")).selection("input").named(mw.getID("CONTACT CROSS SECTION"));

                model.geom(id).create(mw.nextID("pt","Src"), "Point");
                model.geom(id).feature(mw.getID("Src")).label("Src");
                model.geom(id).feature(mw.getID("Src")).set("contributeto", mw.getID("SRC"));
                model.geom(id).feature(mw.getID("Src"))
                        .set("p", new String[]{"(R_in-R_conductor-Sep_conductor)*cos(Theta_conductor/2)", "(R_in-R_conductor-Sep_conductor)*sin(Theta_conductor/2)", "Center"});

                model.geom(id).run();
                break;
            case "CircleContact_Primitive":
                model.geom(id).inputParam().set("Recess", "Recess_ITC");
                model.geom(id).inputParam().set("Rotation_angle", "0 [deg]");
                model.geom(id).inputParam().set("Center", "Center_IT");
                model.geom(id).inputParam().set("Round_def", "Round_def_ITC");
                model.geom(id).inputParam().set("R_in", "R_in_ITI");
                model.geom(id).inputParam().set("Contact_depth", "Contact_depth_ITC");
                model.geom(id).inputParam().set("Overshoot", "Overshoot_ITC");
                model.geom(id).inputParam().set("A_ellipse_contact", "a_ellipse_contact_ITC");
                model.geom(id).inputParam().set("Diam_contact", "diam_contact_ITC");
                model.geom(id).inputParam().set("L", "L_IT");

                model.geom(id).selection().create("csel11", "CumulativeSelection");
                model.geom(id).selection("csel11").label("CONTACT CUTTER IN");
                model.geom(id).selection().create("csel10", "CumulativeSelection");
                model.geom(id).selection("csel10").label("PRE CUT CONTACT");
                model.geom(id).selection().create("csel7", "CumulativeSelection");
                model.geom(id).selection("csel7").label("RECESS FINAL");
                model.geom(id).selection().create("csel8", "CumulativeSelection");
                model.geom(id).selection("csel8").label("RECESS OVERSHOOT");
                model.geom(id).selection().create("csel14", "CumulativeSelection");
                model.geom(id).selection("csel14").label("SRC");
                model.geom(id).selection().create("csel9", "CumulativeSelection");
                model.geom(id).selection("csel9").label("PLANE FOR CONTACT");
                model.geom(id).selection().create("csel13", "CumulativeSelection");
                model.geom(id).selection("csel13").label("CONTACT FINAL");
                model.geom(id).selection().create("csel12", "CumulativeSelection");
                model.geom(id).selection("csel12").label("CONTACT CUTTER OUT");
                model.geom(id).selection().create("csel1", "CumulativeSelection");
                model.geom(id).selection("csel1").label("BASE CONTACT PLANE (PRE ROTATION)");
                model.geom(id).selection().create("csel2", "CumulativeSelection");
                model.geom(id).selection("csel2").label("BASE PLANE (PRE ROTATION)");
                model.geom(id).selection().create("csel3", "CumulativeSelection");
                model.geom(id).selection("csel3").label("PLANE FOR RECESS");
                model.geom(id).selection().create("csel4", "CumulativeSelection");
                model.geom(id).selection("csel4").label("PRE CUT RECESS");
                model.geom(id).selection().create("csel5", "CumulativeSelection");
                model.geom(id).selection("csel5").label("RECESS CUTTER IN");
                model.geom(id).selection().create("csel6", "CumulativeSelection");
                model.geom(id).selection("csel6").label("RECESS CUTTER OUT");

                model.geom(id).create("wp1", "WorkPlane");
                model.geom(id).feature("wp1").label("Base Plane (Pre Rrotation)");
                model.geom(id).feature("wp1").set("contributeto", "csel2");
                model.geom(id).feature("wp1").set("quickplane", "yz");
                model.geom(id).feature("wp1").set("unite", true);
                model.geom(id).create("if1", "If");
                model.geom(id).feature("if1").label("If Recess");
                model.geom(id).feature("if1").set("condition", "Recess>0");
                model.geom(id).create("wp2", "WorkPlane");
                model.geom(id).feature("wp2").label("Rotated Plane for Recess");
                model.geom(id).feature("wp2").set("contributeto", "csel3");
                model.geom(id).feature("wp2").set("planetype", "transformed");
                model.geom(id).feature("wp2").set("workplane", "wp1");
                model.geom(id).feature("wp2").set("transaxis", new int[]{0, 1, 0});
                model.geom(id).feature("wp2").set("transrot", "Rotation_angle");
                model.geom(id).feature("wp2").set("unite", true);
                model.geom(id).feature("wp2").geom().selection().create("csel1", "CumulativeSelection");
                model.geom(id).feature("wp2").geom().selection("csel1").label("CONTACT OUTLINE SHAPE");
                model.geom(id).feature("wp2").geom().create("if1", "If");
                model.geom(id).feature("wp2").geom().feature("if1").label("If Contact Surface is Circle");
                model.geom(id).feature("wp2").geom().feature("if1").set("condition", "Round_def_ITC==1");
                model.geom(id).feature("wp2").geom().create("e1", "Ellipse");
                model.geom(id).feature("wp2").geom().feature("e1").label("Contact Outline");
                model.geom(id).feature("wp2").geom().feature("e1").set("contributeto", "csel1");
                model.geom(id).feature("wp2").geom().feature("e1").set("pos", new String[]{"0", "Center"});
                model.geom(id).feature("wp2").geom().feature("e1")
                        .set("semiaxes", new String[]{"A_ellipse_contact", "Diam_contact/2"});
                model.geom(id).feature("wp2").geom().create("elseif1", "ElseIf");
                model.geom(id).feature("wp2").geom().feature("elseif1").label("Else If Contact Outline is Circle");
                model.geom(id).feature("wp2").geom().feature("elseif1").set("condition", "Round_def_ITC==2");
                model.geom(id).feature("wp2").geom().create("e2", "Ellipse");
                model.geom(id).feature("wp2").geom().feature("e2").label("Contact Outline 1");
                model.geom(id).feature("wp2").geom().feature("e2").set("contributeto", "csel1");
                model.geom(id).feature("wp2").geom().feature("e2").set("pos", new String[]{"0", "Center"});
                model.geom(id).feature("wp2").geom().feature("e2")
                        .set("semiaxes", new String[]{"Diam_contact/2", "Diam_contact/2"});
                model.geom(id).feature("wp2").geom().create("endif1", "EndIf");
                model.geom(id).create("ext1", "Extrude");
                model.geom(id).feature("ext1").label("Make Pre Cut Recess Domains");
                model.geom(id).feature("ext1").set("contributeto", "csel4");
                model.geom(id).feature("ext1").setIndex("distance", "R_in+Recess+Overshoot", 0);
                model.geom(id).feature("ext1").selection("input").named("csel3");
                model.geom(id).create("cyl1", "Cylinder");
                model.geom(id).feature("cyl1").label("Recess Cut In");
                model.geom(id).feature("cyl1").set("contributeto", "csel5");
                model.geom(id).feature("cyl1").set("pos", new String[]{"0", "0", "Center-L/2"});
                model.geom(id).feature("cyl1").set("r", "R_in");
                model.geom(id).feature("cyl1").set("h", "L");
                model.geom(id).create("cyl2", "Cylinder");
                model.geom(id).feature("cyl2").label("Recess Cut Out");
                model.geom(id).feature("cyl2").set("contributeto", "csel6");
                model.geom(id).feature("cyl2").set("pos", new String[]{"0", "0", "Center-L/2"});
                model.geom(id).feature("cyl2").set("r", "R_in+Recess");
                model.geom(id).feature("cyl2").set("h", "L");
                model.geom(id).create("dif1", "Difference");
                model.geom(id).feature("dif1").label("Execute Recess Cut In");
                model.geom(id).feature("dif1").set("contributeto", "csel7");
                model.geom(id).feature("dif1").selection("input").named("csel4");
                model.geom(id).feature("dif1").selection("input2").named("csel5");
                model.geom(id).create("pard1", "PartitionDomains");
                model.geom(id).feature("pard1").set("contributeto", "csel7");
                model.geom(id).feature("pard1").set("partitionwith", "objects");
                model.geom(id).feature("pard1").set("keepobject", false);
                model.geom(id).feature("pard1").selection("domain").named("csel4");
                model.geom(id).feature("pard1").selection("object").named("csel6");
                model.geom(id).create("ballsel1", "BallSelection");
                model.geom(id).feature("ballsel1").label("Select Overshoot");
                model.geom(id).feature("ballsel1").set("posx", "(R_in+Recess+Overshoot/2)*cos(Rotation_angle)");
                model.geom(id).feature("ballsel1").set("posy", "(R_in+Recess+Overshoot/2)*sin(Rotation_angle)");
                model.geom(id).feature("ballsel1").set("posz", "Center");
                model.geom(id).feature("ballsel1").set("r", 1);
                model.geom(id).feature("ballsel1").set("contributeto", "csel8");
                model.geom(id).create("del1", "Delete");
                model.geom(id).feature("del1").label("Delete Recess Overshoot");
                model.geom(id).feature("del1").selection("input").init(3);
                model.geom(id).feature("del1").selection("input").named("csel8");
                model.geom(id).create("endif1", "EndIf");
                model.geom(id).create("wp3", "WorkPlane");
                model.geom(id).feature("wp3").label("Rotated Plane for Contact");
                model.geom(id).feature("wp3").set("contributeto", "csel9");
                model.geom(id).feature("wp3").set("planetype", "transformed");
                model.geom(id).feature("wp3").set("workplane", "wp1");
                model.geom(id).feature("wp3").set("transaxis", new int[]{0, 1, 0});
                model.geom(id).feature("wp3").set("transrot", "Rotation_angle");
                model.geom(id).feature("wp3").set("unite", true);
                model.geom(id).feature("wp3").geom().selection().create("csel1", "CumulativeSelection");
                model.geom(id).feature("wp3").geom().selection("csel1").label("CONTACT OUTLINE SHAPE");
                model.geom(id).feature("wp3").geom().create("if1", "If");
                model.geom(id).feature("wp3").geom().feature("if1").label("If Contact Surface is Circle");
                model.geom(id).feature("wp3").geom().feature("if1").set("condition", "Round_def_ITC==1");
                model.geom(id).feature("wp3").geom().create("e1", "Ellipse");
                model.geom(id).feature("wp3").geom().feature("e1").label("Contact Outline");
                model.geom(id).feature("wp3").geom().feature("e1").set("contributeto", "csel1");
                model.geom(id).feature("wp3").geom().feature("e1").set("pos", new String[]{"0", "Center"});
                model.geom(id).feature("wp3").geom().feature("e1")
                        .set("semiaxes", new String[]{"A_ellipse_contact", "Diam_contact/2"});
                model.geom(id).feature("wp3").geom().create("elseif1", "ElseIf");
                model.geom(id).feature("wp3").geom().feature("elseif1").label("Else If Contact Outline is Circle");
                model.geom(id).feature("wp3").geom().feature("elseif1").set("condition", "Round_def_ITC==2");
                model.geom(id).feature("wp3").geom().create("e2", "Ellipse");
                model.geom(id).feature("wp3").geom().feature("e2").label("Contact Outline 1");
                model.geom(id).feature("wp3").geom().feature("e2").set("contributeto", "csel1");
                model.geom(id).feature("wp3").geom().feature("e2").set("pos", new String[]{"0", "Center"});
                model.geom(id).feature("wp3").geom().feature("e2")
                        .set("semiaxes", new String[]{"Diam_contact/2", "Diam_contact/2"});
                model.geom(id).feature("wp3").geom().create("endif1", "EndIf");
                model.geom(id).create("ext2", "Extrude");
                model.geom(id).feature("ext2").label("Make Pre Cut Contact Domains");
                model.geom(id).feature("ext2").set("contributeto", "csel10");
                model.geom(id).feature("ext2").setIndex("distance", "R_in+Recess+Contact_depth+Overshoot", 0);
                model.geom(id).feature("ext2").selection("input").named("csel9");
                model.geom(id).create("cyl3", "Cylinder");
                model.geom(id).feature("cyl3").label("Contact Cut In");
                model.geom(id).feature("cyl3").set("contributeto", "csel11");
                model.geom(id).feature("cyl3").set("pos", new String[]{"0", "0", "Center-L/2"});
                model.geom(id).feature("cyl3").set("r", "R_in+Recess");
                model.geom(id).feature("cyl3").set("h", "L");
                model.geom(id).create("cyl4", "Cylinder");
                model.geom(id).feature("cyl4").label("Contact Cut Out");
                model.geom(id).feature("cyl4").set("contributeto", "csel12");
                model.geom(id).feature("cyl4").set("pos", new String[]{"0", "0", "Center-L/2"});
                model.geom(id).feature("cyl4").set("r", "R_in+Recess+Contact_depth");
                model.geom(id).feature("cyl4").set("h", "L");
                model.geom(id).create("dif2", "Difference");
                model.geom(id).feature("dif2").label("Execute Contact Cut In");
                model.geom(id).feature("dif2").set("contributeto", "csel13");
                model.geom(id).feature("dif2").selection("input").named("csel10");
                model.geom(id).feature("dif2").selection("input2").named("csel11");
                model.geom(id).create("pard2", "PartitionDomains");
                model.geom(id).feature("pard2").set("contributeto", "csel13");
                model.geom(id).feature("pard2").set("partitionwith", "objects");
                model.geom(id).feature("pard2").set("keepobject", false);
                model.geom(id).feature("pard2").selection("domain").named("csel10");
                model.geom(id).feature("pard2").selection("object").named("csel12");
                model.geom(id).create("ballsel2", "BallSelection");
                model.geom(id).feature("ballsel2").label("Select Overshoot 1");
                model.geom(id).feature("ballsel2")
                        .set("posx", "(R_in+Recess+Contact_depth+Overshoot/2)*cos(Rotation_angle)");
                model.geom(id).feature("ballsel2")
                        .set("posy", "(R_in+Recess+Contact_depth+Overshoot/2)*sin(Rotation_angle)");
                model.geom(id).feature("ballsel2").set("posz", "Center");
                model.geom(id).feature("ballsel2").set("r", 1);
                model.geom(id).feature("ballsel2").set("contributeto", "csel8");
                model.geom(id).create("del2", "Delete");
                model.geom(id).feature("del2").label("Delete Recess Overshoot 1");
                model.geom(id).feature("del2").selection("input").init(3);
                model.geom(id).feature("del2").selection("input").named("csel8");
                model.geom(id).create("pt1", "Point");
                model.geom(id).feature("pt1").label("Src");
                model.geom(id).feature("pt1").set("contributeto", "csel14");
                model.geom(id).feature("pt1")
                        .set("p", new String[]{"(R_in+Recess+Contact_depth/2)*cos(Rotation_angle)", "(R_in+Recess+Contact_depth/2)*sin(Rotation_angle)", "Center"});
                model.geom(id).run();
                break;
            case "HelicalCuffnContact_Primitive":
                model.geom("part5").inputParam().set("Center", "Center_LN");

                model.geom(id).selection().create("csel1", "CumulativeSelection");
                model.geom(id).selection("csel1").label("PC1");
                model.geom(id).selection().create("csel2", "CumulativeSelection");
                model.geom(id).selection("csel2").label("Cuffp1");
                model.geom(id).selection().create("csel3", "CumulativeSelection");
                model.geom(id).selection("csel3").label("SEL END P1");
                model.geom(id).selection().create("csel4", "CumulativeSelection");
                model.geom(id).selection("csel4").label("PC2");
                model.geom(id).selection().create("csel10", "CumulativeSelection");
                model.geom(id).selection("csel10").label("SRC");
                model.geom(id).selection().create("csel5", "CumulativeSelection");
                model.geom(id).selection("csel5").label("Cuffp2");
                model.geom(id).selection().create("csel6", "CumulativeSelection");
                model.geom(id).selection("csel6").label("Conductorp2");
                model.geom(id).selection().create("csel7", "CumulativeSelection");
                model.geom(id).selection("csel7").label("SEL END P2");
                model.geom(id).selection().create("csel8", "CumulativeSelection");
                model.geom(id).selection("csel8").label("Cuffp3");
                model.geom(id).selection().create("csel9", "CumulativeSelection");
                model.geom(id).selection("csel9").label("PC3");

                model.geom(id).create("wp1", "WorkPlane");
                model.geom(id).feature("wp1").label("Helical Insulator Cross Section Part 1");
                model.geom(id).feature("wp1").set("quickplane", "xz");
                model.geom(id).feature("wp1").set("unite", true);
                model.geom(id).feature("wp1").geom().selection().create("csel1", "CumulativeSelection");
                model.geom(id).feature("wp1").geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION");
                model.geom(id).feature("wp1").geom().selection().create("csel2", "CumulativeSelection");
                model.geom(id).feature("wp1").geom().selection("csel2").label("HELICAL INSULATOR CROSS SECTION P1");
                model.geom(id).feature("wp1").geom().create("r1", "Rectangle");
                model.geom(id).feature("wp1").geom().feature("r1").label("Helical Insulator Cross Section Part 1");
                model.geom(id).feature("wp1").geom().feature("r1").set("contributeto", "csel2");
                model.geom(id).feature("wp1").geom().feature("r1")
                        .set("pos", new String[]{"r_cuff_in_LN+(thk_cuff_LN/2)", "Center-(L_cuff_LN/2)"});
                model.geom(id).feature("wp1").geom().feature("r1").set("base", "center");
                model.geom(id).feature("wp1").geom().feature("r1").set("size", new String[]{"thk_cuff_LN", "w_cuff_LN"});
                model.geom(id).create("pc1", "ParametricCurve");
                model.geom(id).feature("pc1").label("Parametric Curve Part 1");
                model.geom(id).feature("pc1").set("contributeto", "csel1");
                model.geom(id).feature("pc1").set("parmax", "rev_cuff_LN*(0.75/2.5)");
                model.geom(id).feature("pc1")
                        .set("coord", new String[]{"cos(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "sin(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "Center+(L_cuff_LN)*(s/rev_cuff_LN)-(L_cuff_LN/2)"});
                model.geom(id).create("swe1", "Sweep");
                model.geom(id).feature("swe1").label("Make Cuff Part 1");
                model.geom(id).feature("swe1").set("contributeto", "csel2");
                model.geom(id).feature("swe1").set("crossfaces", true);
                model.geom(id).feature("swe1").set("keep", false);
                model.geom(id).feature("swe1").set("includefinal", false);
                model.geom(id).feature("swe1").set("twistcomp", false);
                model.geom(id).feature("swe1").selection("face").named("wp1_csel2");
                model.geom(id).feature("swe1").selection("edge").named("csel1");
                model.geom(id).feature("swe1").selection("diredge").set("pc1(1)", 1);
                model.geom(id).create("ballsel1", "BallSelection");
                model.geom(id).feature("ballsel1").set("entitydim", 2);
                model.geom(id).feature("ballsel1").label("Select End Face Part 1");
                model.geom(id).feature("ballsel1").set("posx", "cos(2*pi*rev_cuff_LN*((0.75)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                model.geom(id).feature("ballsel1").set("posy", "sin(2*pi*rev_cuff_LN*((0.75)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                model.geom(id).feature("ballsel1")
                        .set("posz", "Center+(L_cuff_LN)*(rev_cuff_LN*((0.75)/2.5)/rev_cuff_LN)-(L_cuff_LN/2)");
                model.geom(id).feature("ballsel1").set("r", 1);
                model.geom(id).feature("ballsel1").set("contributeto", "csel3");
                model.geom(id).create("wp2", "WorkPlane");
                model.geom(id).feature("wp2").label("Helical Insulator Cross Section Part 2");
                model.geom(id).feature("wp2").set("planetype", "faceparallel");
                model.geom(id).feature("wp2").set("unite", true);
                model.geom(id).feature("wp2").selection("face").named("csel3");
                model.geom(id).feature("wp2").geom().selection().create("csel1", "CumulativeSelection");
                model.geom(id).feature("wp2").geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION P2");
                model.geom(id).feature("wp2").geom().selection().create("csel2", "CumulativeSelection");
                model.geom(id).feature("wp2").geom().selection("csel2").label("HELICAL CONDUCTOR CROSS SECTION P2");
                model.geom(id).feature("wp2").geom().create("r1", "Rectangle");
                model.geom(id).feature("wp2").geom().feature("r1").label("Helical Insulator Cross Section Part 2");
                model.geom(id).feature("wp2").geom().feature("r1").set("contributeto", "csel1");
                model.geom(id).feature("wp2").geom().feature("r1").set("base", "center");
                model.geom(id).feature("wp2").geom().feature("r1").set("size", new String[]{"thk_cuff_LN", "w_cuff_LN"});
                model.geom(id).create("wp3", "WorkPlane");
                model.geom(id).feature("wp3").label("Helical Conductor Cross Section Part 2");
                model.geom(id).feature("wp3").set("planetype", "faceparallel");
                model.geom(id).feature("wp3").set("unite", true);
                model.geom(id).feature("wp3").selection("face").named("csel3");
                model.geom(id).feature("wp3").geom().selection().create("csel1", "CumulativeSelection");
                model.geom(id).feature("wp3").geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION P2");
                model.geom(id).feature("wp3").geom().selection().create("csel2", "CumulativeSelection");
                model.geom(id).feature("wp3").geom().selection("csel2").label("HELICAL CONDUCTOR CROSS SECTION P2");
                model.geom(id).feature("wp3").geom().create("r2", "Rectangle");
                model.geom(id).feature("wp3").geom().feature("r2").label("Helical Conductor Cross Section Part 2");
                model.geom(id).feature("wp3").geom().feature("r2").set("contributeto", "csel2");
                model.geom(id).feature("wp3").geom().feature("r2").set("pos", new String[]{"(thk_elec_LN-thk_cuff_LN)/2", "0"});
                model.geom(id).feature("wp3").geom().feature("r2").set("base", "center");
                model.geom(id).feature("wp3").geom().feature("r2").set("size", new String[]{"thk_elec_LN", "w_elec_LN"});
                model.geom(id).create("pc2", "ParametricCurve");
                model.geom(id).feature("pc2").label("Parametric Curve Part 2");
                model.geom(id).feature("pc2").set("contributeto", "csel4");
                model.geom(id).feature("pc2").set("parmin", "rev_cuff_LN*(0.75/2.5)");
                model.geom(id).feature("pc2").set("parmax", "rev_cuff_LN*((0.75+1)/2.5)");
                model.geom(id).feature("pc2")
                        .set("coord", new String[]{"cos(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "sin(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "Center+(L_cuff_LN)*(s/rev_cuff_LN)-(L_cuff_LN/2)"});
                model.geom(id).create("swe2", "Sweep");
                model.geom(id).feature("swe2").label("Make Cuff Part 2");
                model.geom(id).feature("swe2").set("contributeto", "csel5");
                model.geom(id).feature("swe2").set("crossfaces", true);
                model.geom(id).feature("swe2").set("includefinal", false);
                model.geom(id).feature("swe2").set("twistcomp", false);
                model.geom(id).feature("swe2").selection("face").named("wp2_csel1");
                model.geom(id).feature("swe2").selection("edge").named("csel4");
                model.geom(id).feature("swe2").selection("diredge").set("pc2(1)", 1);
                model.geom(id).create("swe3", "Sweep");
                model.geom(id).feature("swe3").label("Make Conductor Part 2");
                model.geom(id).feature("swe3").set("contributeto", "csel6");
                model.geom(id).feature("swe3").set("crossfaces", true);
                model.geom(id).feature("swe3").set("keep", false);
                model.geom(id).feature("swe3").set("includefinal", false);
                model.geom(id).feature("swe3").set("twistcomp", false);
                model.geom(id).feature("swe3").selection("face").named("wp3_csel2");
                model.geom(id).feature("swe3").selection("edge").named("csel4");
                model.geom(id).feature("swe3").selection("diredge").set("pc2(1)", 1);
                model.geom(id).create("ballsel2", "BallSelection");
                model.geom(id).feature("ballsel2").set("entitydim", 2);
                model.geom(id).feature("ballsel2").label("Select End Face Part 2");
                model.geom(id).feature("ballsel2")
                        .set("posx", "cos(2*pi*rev_cuff_LN*((0.75+1)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                model.geom(id).feature("ballsel2")
                        .set("posy", "sin(2*pi*rev_cuff_LN*((0.75+1)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                model.geom(id).feature("ballsel2")
                        .set("posz", "Center+(L_cuff_LN)*(rev_cuff_LN*((0.75+1)/2.5)/rev_cuff_LN)-(L_cuff_LN/2)");
                model.geom(id).feature("ballsel2").set("r", 1);
                model.geom(id).feature("ballsel2").set("contributeto", "csel7");
                model.geom(id).create("wp4", "WorkPlane");
                model.geom(id).feature("wp4").label("Helical Insulator Cross Section Part 3");
                model.geom(id).feature("wp4").set("planetype", "faceparallel");
                model.geom(id).feature("wp4").set("unite", true);
                model.geom(id).feature("wp4").selection("face").named("csel7");
                model.geom(id).feature("wp4").geom().selection().create("csel1", "CumulativeSelection");
                model.geom(id).feature("wp4").geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION P3");
                model.geom(id).feature("wp4").geom().create("r1", "Rectangle");
                model.geom(id).feature("wp4").geom().feature("r1").label("Helical Insulator Cross Section Part 3");
                model.geom(id).feature("wp4").geom().feature("r1").set("contributeto", "csel1");
                model.geom(id).feature("wp4").geom().feature("r1").set("base", "center");
                model.geom(id).feature("wp4").geom().feature("r1").set("size", new String[]{"thk_cuff_LN", "w_cuff_LN"});
                model.geom(id).create("pc3", "ParametricCurve");
                model.geom(id).feature("pc3").label("Parametric Curve Part 3");
                model.geom(id).feature("pc3").set("contributeto", "csel9");
                model.geom(id).feature("pc3").set("parmin", "rev_cuff_LN*((0.75+1)/2.5)");
                model.geom(id).feature("pc3").set("parmax", "rev_cuff_LN");
                model.geom(id).feature("pc3")
                        .set("coord", new String[]{"cos(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "sin(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "Center+(L_cuff_LN)*(s/rev_cuff_LN)-(L_cuff_LN/2)"});
                model.geom(id).create("swe4", "Sweep");
                model.geom(id).feature("swe4").label("Make Cuff Part 3");
                model.geom(id).feature("swe4").set("contributeto", "csel8");
                model.geom(id).feature("swe4").selection("face").named("wp4_csel1");
                model.geom(id).feature("swe4").selection("edge").named("csel9");
                model.geom(id).feature("swe4").set("keep", false);
                model.geom(id).feature("swe4").set("twistcomp", false);
                model.geom(id).create("pt1", "Point");
                model.geom(id).feature("pt1").label("src");
                model.geom(id).feature("pt1").set("contributeto", "csel10");
                model.geom(id).feature("pt1")
                        .set("p", new String[]{"cos(2*pi*rev_cuff_LN*(1.25/2.5))*((thk_elec_LN/2)+r_cuff_in_LN)", "sin(2*pi*rev_cuff_LN*(1.25/2.5))*((thk_elec_LN/2)+r_cuff_in_LN)", "Center"});
                model.geom(id).run();
                break;
            case "RectangleContact_Primitive":
                model.geom(id).inputParam().set("r_inner_contact", "r_cuff_in_Pitt+recess_Pitt");
                model.geom(id).inputParam().set("r_outer_contact", "r_cuff_in_Pitt+recess_Pitt+thk_contact_Pitt");
                model.geom(id).inputParam().set("z_center", "0 [mm]");
                model.geom(id).inputParam().set("rotation_angle", "0 [deg]");

                model.geom(id).selection().create("csel11", "CumulativeSelection");
                model.geom(id).selection("csel11").label("OUTER CONTACT CUTTER");
                model.geom(id).selection().create("csel22", "CumulativeSelection");
                model.geom(id).selection("csel22").label("SEL INNER EXCESS CONTACT");
                model.geom(id).selection().create("csel10", "CumulativeSelection");
                model.geom(id).selection("csel10").label("INNER CONTACT CUTTER");
                model.geom(id).selection().create("csel21", "CumulativeSelection");
                model.geom(id).selection("csel21").label("SEL OUTER EXCESS RECESS");
                model.geom(id).selection().create("csel20", "CumulativeSelection");
                model.geom(id).selection("csel20").label("SEL INNER EXCESS RECESS");
                model.geom(id).selection().create("csel7", "CumulativeSelection");
                model.geom(id).selection("csel7").label("OUTER CUTTER");
                model.geom(id).selection().create("csel15", "CumulativeSelection");
                model.geom(id).selection("csel15").label("FINAL RECESS");
                model.geom(id).selection().create("csel8", "CumulativeSelection");
                model.geom(id).selection("csel8").label("RECESS CROSS SECTION");
                model.geom(id).selection().create("csel14", "CumulativeSelection");
                model.geom(id).selection("csel14").label("OUTER RECESS CUTTER");
                model.geom(id).selection().create("csel9", "CumulativeSelection");
                model.geom(id).selection("csel9").label("RECESS PRE CUTS");
                model.geom(id).selection().create("csel13", "CumulativeSelection");
                model.geom(id).selection("csel13").label("INNER RECESS CUTTER");
                model.geom(id).selection().create("csel12", "CumulativeSelection");
                model.geom(id).selection("csel12").label("FINAL CONTACT");
                model.geom(id).selection().create("csel23", "CumulativeSelection");
                model.geom(id).selection("csel23").label("SEL OUTER EXCESS CONTACT");
                model.geom(id).selection().create("csel19", "CumulativeSelection");
                model.geom(id).selection("csel19").label("SEL OUTER EXCESS");
                model.geom(id).selection().create("csel18", "CumulativeSelection");
                model.geom(id).selection("csel18").label("SEL INNER EXCESS");
                model.geom(id).selection().create("csel17", "CumulativeSelection");
                model.geom(id).selection("csel17").label("BASE CONTACT PLANE (PRE ROTATION)");
                model.geom(id).selection().create("csel16", "CumulativeSelection");
                model.geom(id).selection("csel16").label("SRC");
                model.geom(id).selection().create("csel1", "CumulativeSelection");
                model.geom(id).selection("csel1").label("CONTACT PRE CUTS");
                model.geom(id).selection().create("csel2", "CumulativeSelection");
                model.geom(id).selection("csel2").label("CONTACT CROSS SECTION");
                model.geom(id).selection().create("csel3", "CumulativeSelection");
                model.geom(id).selection("csel3").label("INNER CUFF CUTTER");
                model.geom(id).selection().create("csel4", "CumulativeSelection");
                model.geom(id).selection("csel4").label("OUTER CUFF CUTTER");
                model.geom(id).selection().create("csel5", "CumulativeSelection");
                model.geom(id).selection("csel5").label("FINAL");
                model.geom(id).selection().create("csel6", "CumulativeSelection");
                model.geom(id).selection("csel6").label("INNER CUTTER");

                model.geom(id).create("wp3", "WorkPlane");
                model.geom(id).feature("wp3").label("base plane (pre rotation)");
                model.geom(id).feature("wp3").set("contributeto", "csel17");
                model.geom(id).feature("wp3").set("quickplane", "yz");
                model.geom(id).feature("wp3").set("unite", true);
                model.geom(id).create("wp1", "WorkPlane");
                model.geom(id).feature("wp1").label("Contact Cross Section");
                model.geom(id).feature("wp1").set("contributeto", "csel2");
                model.geom(id).feature("wp1").set("planetype", "transformed");
                model.geom(id).feature("wp1").set("workplane", "wp3");
                model.geom(id).feature("wp1").set("transaxis", new int[]{0, 1, 0});
                model.geom(id).feature("wp1").set("transrot", "rotation_angle");
                model.geom(id).feature("wp1").set("unite", true);
                model.geom(id).feature("wp1").geom().selection().create("csel1", "CumulativeSelection");
                model.geom(id).feature("wp1").geom().selection("csel1").label("CONTACT PRE FILLET");
                model.geom(id).feature("wp1").geom().selection().create("csel2", "CumulativeSelection");
                model.geom(id).feature("wp1").geom().selection("csel2").label("CONTACT FILLETED");
                model.geom(id).feature("wp1").geom().create("r1", "Rectangle");
                model.geom(id).feature("wp1").geom().feature("r1").label("Contact Pre Fillet Corners");
                model.geom(id).feature("wp1").geom().feature("r1").set("contributeto", "csel1");
                model.geom(id).feature("wp1").geom().feature("r1").set("pos", new int[]{0, 0});
                model.geom(id).feature("wp1").geom().feature("r1").set("base", "center");
                model.geom(id).feature("wp1").geom().feature("r1").set("size", new String[]{"w_contact_Pitt", "z_contact_Pitt"});
                model.geom(id).feature("wp1").geom().create("fil1", "Fillet");
                model.geom(id).feature("wp1").geom().feature("fil1").label("Fillet Corners");
                model.geom(id).feature("wp1").geom().feature("fil1").set("contributeto", "csel2");
                model.geom(id).feature("wp1").geom().feature("fil1").set("radius", "fillet_contact_Pitt");
                model.geom(id).feature("wp1").geom().feature("fil1").selection("point").named("csel1");
                model.geom(id).feature("wp1").geom().create("sca1", "Scale");
                model.geom(id).feature("wp1").geom().feature("sca1").set("type", "anisotropic");
                model.geom(id).feature("wp1").geom().feature("sca1")
                        .set("factor", new String[]{"1", "scale_morph_w_contact_Pitt"});
                model.geom(id).feature("wp1").geom().feature("sca1").selection("input").named("csel2");
                model.geom(id).feature("wp1").geom().create("mov1", "Move");
                model.geom(id).feature("wp1").geom().feature("mov1").set("disply", "z_center");
                model.geom(id).feature("wp1").geom().feature("mov1").selection("input").named("csel2");
                model.geom(id).create("ext1", "Extrude");
                model.geom(id).feature("ext1").label("Make Contact Pre Cuts");
                model.geom(id).feature("ext1").set("contributeto", "csel1");
                model.geom(id).feature("ext1").setIndex("distance", "2*r_cuff_in_Pitt", 0);
                model.geom(id).feature("ext1").selection("input").named("csel2");
                model.geom(id).create("cyl1", "Cylinder");
                model.geom(id).feature("cyl1").label("Inner Contact Cutter");
                model.geom(id).feature("cyl1").set("contributeto", "csel10");
                model.geom(id).feature("cyl1").set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                model.geom(id).feature("cyl1").set("r", "r_inner_contact");
                model.geom(id).feature("cyl1").set("h", "L_cuff_Pitt");
                model.geom(id).create("cyl2", "Cylinder");
                model.geom(id).feature("cyl2").label("Outer Contact Cutter");
                model.geom(id).feature("cyl2").set("contributeto", "csel11");
                model.geom(id).feature("cyl2").set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                model.geom(id).feature("cyl2").set("r", "r_outer_contact");
                model.geom(id).feature("cyl2").set("h", "L_cuff_Pitt");
                model.geom(id).create("par1", "Partition");
                model.geom(id).feature("par1").set("contributeto", "csel12");
                model.geom(id).feature("par1").selection("input").named("csel1");
                model.geom(id).feature("par1").selection("tool").named("csel11");
                model.geom(id).create("par2", "Partition");
                model.geom(id).feature("par2").set("contributeto", "csel12");
                model.geom(id).feature("par2").selection("input").named("csel1");
                model.geom(id).feature("par2").selection("tool").named("csel10");
                model.geom(id).create("ballsel1", "BallSelection");
                model.geom(id).feature("ballsel1").label("sel inner excess");
                model.geom(id).feature("ballsel1").set("posx", "(r_inner_contact/2)*cos(rotation_angle)");
                model.geom(id).feature("ballsel1").set("posy", "(r_inner_contact/2)*sin(rotation_angle)");
                model.geom(id).feature("ballsel1").set("posz", "z_center");
                model.geom(id).feature("ballsel1").set("r", 1);
                model.geom(id).feature("ballsel1").set("contributeto", "csel22");
                model.geom(id).create("ballsel2", "BallSelection");
                model.geom(id).feature("ballsel2").label("sel outer excess");
                model.geom(id).feature("ballsel2").set("posx", "((r_outer_contact+2*r_cuff_in_Pitt)/2)*cos(rotation_angle)");
                model.geom(id).feature("ballsel2").set("posy", "((r_outer_contact+2*r_cuff_in_Pitt)/2)*sin(rotation_angle)");
                model.geom(id).feature("ballsel2").set("posz", "z_center");
                model.geom(id).feature("ballsel2").set("r", 1);
                model.geom(id).feature("ballsel2").set("contributeto", "csel23");
                model.geom(id).create("del1", "Delete");
                model.geom(id).feature("del1").label("Delete Inner Excess Contact");
                model.geom(id).feature("del1").selection("input").init(3);
                model.geom(id).feature("del1").selection("input").named("csel22");
                model.geom(id).create("del3", "Delete");
                model.geom(id).feature("del3").label("Delete Outer Excess Contact");
                model.geom(id).feature("del3").selection("input").init(3);
                model.geom(id).feature("del3").selection("input").named("csel23");
                model.geom(id).create("if1", "If");
                model.geom(id).feature("if1").set("condition", "recess_Pitt>0");
                model.geom(id).create("wp2", "WorkPlane");
                model.geom(id).feature("wp2").label("Recess Cross Section");
                model.geom(id).feature("wp2").set("contributeto", "csel8");
                model.geom(id).feature("wp2").set("planetype", "transformed");
                model.geom(id).feature("wp2").set("workplane", "wp3");
                model.geom(id).feature("wp2").set("transaxis", new int[]{0, 1, 0});
                model.geom(id).feature("wp2").set("transrot", "rotation_angle");
                model.geom(id).feature("wp2").set("unite", true);
                model.geom(id).feature("wp2").geom().selection().create("csel1", "CumulativeSelection");
                model.geom(id).feature("wp2").geom().selection("csel1").label("CONTACT PRE FILLET");
                model.geom(id).feature("wp2").geom().selection().create("csel2", "CumulativeSelection");
                model.geom(id).feature("wp2").geom().selection("csel2").label("CONTACT FILLETED");
                model.geom(id).feature("wp2").geom().selection().create("csel3", "CumulativeSelection");
                model.geom(id).feature("wp2").geom().selection("csel3").label("RECESS PRE FILLET");
                model.geom(id).feature("wp2").geom().selection().create("csel4", "CumulativeSelection");
                model.geom(id).feature("wp2").geom().selection("csel4").label("RECESS FILLETED");
                model.geom(id).feature("wp2").geom().create("r1", "Rectangle");
                model.geom(id).feature("wp2").geom().feature("r1").label("Recess Pre Fillet Corners");
                model.geom(id).feature("wp2").geom().feature("r1").set("contributeto", "csel3");
                model.geom(id).feature("wp2").geom().feature("r1").set("pos", new int[]{0, 0});
                model.geom(id).feature("wp2").geom().feature("r1").set("base", "center");
                model.geom(id).feature("wp2").geom().feature("r1").set("size", new String[]{"w_contact_Pitt", "z_contact_Pitt"});
                model.geom(id).feature("wp2").geom().create("fil1", "Fillet");
                model.geom(id).feature("wp2").geom().feature("fil1").label("Fillet Corners");
                model.geom(id).feature("wp2").geom().feature("fil1").set("contributeto", "csel4");
                model.geom(id).feature("wp2").geom().feature("fil1").set("radius", "fillet_contact_Pitt");
                model.geom(id).feature("wp2").geom().feature("fil1").selection("point").named("csel3");
                model.geom(id).feature("wp2").geom().create("sca1", "Scale");
                model.geom(id).feature("wp2").geom().feature("sca1").set("type", "anisotropic");
                model.geom(id).feature("wp2").geom().feature("sca1")
                        .set("factor", new String[]{"1", "scale_morph_w_contact_Pitt"});
                model.geom(id).feature("wp2").geom().feature("sca1").selection("input").named("csel4");
                model.geom(id).feature("wp2").geom().create("mov1", "Move");
                model.geom(id).feature("wp2").geom().feature("mov1").set("disply", "z_center");
                model.geom(id).feature("wp2").geom().feature("mov1").selection("input").named("csel4");
                model.geom(id).create("ext2", "Extrude");
                model.geom(id).feature("ext2").label("Make Recess Pre Cuts 1");
                model.geom(id).feature("ext2").set("contributeto", "csel9");
                model.geom(id).feature("ext2").setIndex("distance", "2*r_cuff_in_Pitt", 0);
                model.geom(id).feature("ext2").selection("input").named("csel8");
                model.geom(id).create("cyl3", "Cylinder");
                model.geom(id).feature("cyl3").label("Inner Recess Cutter");
                model.geom(id).feature("cyl3").set("contributeto", "csel13");
                model.geom(id).feature("cyl3").set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                model.geom(id).feature("cyl3").set("r", "r_cuff_in_Pitt");
                model.geom(id).feature("cyl3").set("h", "L_cuff_Pitt");
                model.geom(id).create("cyl4", "Cylinder");
                model.geom(id).feature("cyl4").label("Outer Recess Cutter");
                model.geom(id).feature("cyl4").set("contributeto", "csel14");
                model.geom(id).feature("cyl4").set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                model.geom(id).feature("cyl4").set("r", "r_inner_contact");
                model.geom(id).feature("cyl4").set("h", "L_cuff_Pitt");
                model.geom(id).create("par3", "Partition");
                model.geom(id).feature("par3").set("contributeto", "csel15");
                model.geom(id).feature("par3").selection("input").named("csel9");
                model.geom(id).feature("par3").selection("tool").named("csel14");
                model.geom(id).create("par4", "Partition");
                model.geom(id).feature("par4").set("contributeto", "csel15");
                model.geom(id).feature("par4").selection("input").named("csel9");
                model.geom(id).feature("par4").selection("tool").named("csel13");
                model.geom(id).create("ballsel3", "BallSelection");
                model.geom(id).feature("ballsel3").label("sel inner excess 1");
                model.geom(id).feature("ballsel3").set("posx", "((r_inner_contact+recess_Pitt)/2)*cos(rotation_angle)");
                model.geom(id).feature("ballsel3").set("posy", "((r_inner_contact+recess_Pitt)/2)*sin(rotation_angle)");
                model.geom(id).feature("ballsel3").set("posz", "z_center");
                model.geom(id).feature("ballsel3").set("r", 1);
                model.geom(id).feature("ballsel3").set("contributeto", "csel20");
                model.geom(id).create("ballsel4", "BallSelection");
                model.geom(id).feature("ballsel4").label("sel outer excess 1");
                model.geom(id).feature("ballsel4").set("posx", "((r_cuff_in_Pitt+2*r_cuff_in_Pitt)/2)*cos(rotation_angle)");
                model.geom(id).feature("ballsel4").set("posy", "((r_cuff_in_Pitt+2*r_cuff_in_Pitt)/2)*sin(rotation_angle)");
                model.geom(id).feature("ballsel4").set("posz", "z_center");
                model.geom(id).feature("ballsel4").set("r", 1);
                model.geom(id).feature("ballsel4").set("contributeto", "csel21");
                model.geom(id).create("del4", "Delete");
                model.geom(id).feature("del4").label("Delete Inner Excess Recess");
                model.geom(id).feature("del4").selection("input").init(3);
                model.geom(id).feature("del4").selection("input").named("csel20");
                model.geom(id).create("del5", "Delete");
                model.geom(id).feature("del5").label("Delete Outer Excess Recess");
                model.geom(id).feature("del5").selection("input").init(3);
                model.geom(id).feature("del5").selection("input").named("csel21");
                model.geom(id).create("endif1", "EndIf");
                model.geom(id).create("pt1", "Point");
                model.geom(id).feature("pt1").label("src");
                model.geom(id).feature("pt1").set("contributeto", "csel16");
                model.geom(id).feature("pt1")
                        .set("p", new String[]{"(r_cuff_in_Pitt+recess_Pitt+(thk_contact_Pitt/2))*cos(rotation_angle)", "(r_cuff_in_Pitt+recess_Pitt+(thk_contact_Pitt/2))*sin(rotation_angle)", "z_center"});
                model.geom(id).run();
                break;
            default:
                throw new IllegalStateException("Unexpected value: " + pseudonym);
        }
        return true;
    }

    /**
     *
     * @param id
     * @param pseudonym
     * @param mw
     * @param data
     * @return
     */
    public static boolean createPartInstance(String id, String pseudonym, ModelWrapper2 mw, HashMap<String, Object> data) {

        Model model = mw.getModel();
        model.component().create("comp1", true);
        model.component("comp1").geom().create("geom1", 3);
        model.component("comp1").mesh().create("mesh1");

        // EXAMPLE
        String nextCsel = mw.nextID("csel", "mySuperCoolCsel");

        // you can either refer to it with that variable, nextCsel
        model.geom(id).selection().create(nextCsel, "CumulativeSelection");

        // or retrieve it later (likely in another method where the first variable isn't easily accessible
        model.geom(id).selection(mw.getID("mySuperCoolCsel")).label("INNER CUFF SURFACE");

        switch (pseudonym) {
            case "TubeCuff_Primitive":
                break;
            case "RibbonContact_Primitive":
                break;
            case "WireContact_Primitive":
                break;
            case "CircleContact_Primitive":
                break;
            case "HelicalCuffnContact_Primitive":
                break;
            case "RectangleContact_Primitive":
                break;
        }

        return true;
    }
}

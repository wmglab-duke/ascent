package model;

import com.comsol.model.GeomFeature;
import com.comsol.model.Model;
import com.comsol.model.ModelParam;

import java.util.HashMap;

class Part {

    private static void examples(ModelWrapper2 mw) {

        Model model = mw.getModel();

        // assume this is passed in (i.e. "id" in method below)
        String partID = "pi1";

        //  id's and pseudonyms
        String wpPseudo = "MY_WORKPLANE";
        String wpID = mw.next("wp", wpPseudo);

        String swePseudo = "MY_SWEEP"; // I ~think~ it's a sweep?
        String sweID = mw.next("swe", swePseudo);

        String cselPseudo = "MY_CSEL";
        String cselID = mw.next("csel", cselPseudo);

        // create those items
        model.geom(partID).create(wpID, "WorkPlane");
        model.geom(partID).create(sweID, "Sweep");
        model.geom(partID).selection().create(cselID, "CumulativeSelection");

        // one mechanic, but not sure if this is how it actually works
        // assuming this is first wp1_csel, should have the name "wp1_csel1"
        model.geom(partID).feature(sweID).selection("face").named(mw.next(wpID + "_csel"));

        // other possible mechanic: that name is just referring to already existing objects
        model.geom(partID).feature(sweID).selection("face").named(wpID + "_" + cselID);

        // also, other new thing: just instantiate a new CMI if need  to restart indexing for part
        IdentifierManager thisPartIM = new IdentifierManager();
        String restartedIDwp = thisPartIM.next("wp");

    }


    public static IdentifierManager createPartPrimitive(String id, String pseudonym, ModelWrapper2 mw) throws IllegalArgumentException {
        return Part.createPartPrimitive(id, pseudonym, mw, null);
    }

//    public static boolean createPartInstance(String id, String pseudonym, ModelWrapper2 mw,
//                                             HashMap<String, String> partPrimitives) {
//        return createPartInstance(id, pseudonym, mw, partPrimitives, null);
//    }

    /**
     *
     * @param id
     * @param pseudonym
     * @param mw
     * @param data
     * @param data
     * @return
     */
    public static IdentifierManager createPartPrimitive(String id, String pseudonym, ModelWrapper2 mw,
                                              HashMap<String, Object> data) throws IllegalArgumentException {


        Model model = mw.getModel();

        model.geom().create(id, "Part", 3);
        model.geom(id).label(pseudonym);
        model.geom(id).lengthUnit("\u00b5m");

        // only used once per method, so ok to define outside the switch
        IdentifierManager im = new IdentifierManager();
        ModelParam mp = model.geom(id).inputParam();

        switch (pseudonym) {
            case "TubeCuff_Primitive":
                mp.set("N_holes", "1");
                mp.set("Theta", "340 [deg]");
                mp.set("Center", "10 [mm]");
                mp.set("R_in", "1 [mm]");
                mp.set("R_out", "2 [mm]");
                mp.set("L", "5 [mm]");
                mp.set("Rot_def", "0 [deg]");
                mp.set("D_hole", "0.3 [mm]");
                mp.set("Buffer_hole", "0.1 [mm]");
                mp.set("L_holecenter_cuffseam", "0.3 [mm]");
                mp.set("Pitch_holecenter_holecenter", "0 [mm]");

                String[] cselTCLabels = {
                        "INNER CUFF SURFACE",
                        "OUTER CUFF SURFACE", "CUFF FINAL",
                        "CUFF wGAP PRE HOLES",
                        "CUFF PRE GAP",
                        "CUFF PRE GAP PRE HOLES",
                        "CUFF GAP CROSS SECTION",
                        "CUFF GAP",
                        "CUFF PRE HOLES",
                        "HOLE 1",
                        "HOLE 2",
                        "HOLES"
                };
                for (String cselTCLabel: cselTCLabels) {
                    model.geom(id).selection().create(im.next("csel", cselTCLabel), "CumulativeSelection")
                            .label(cselTCLabel);
                }

                String micsLabel = "Make Inner Cuff Surface";
                GeomFeature inner_surf = model.geom(id).create(im.next("cyl",micsLabel), "Cylinder");
                inner_surf.label(micsLabel);
                inner_surf.set("contributeto", im.get(cselTCLabels[0]));
                inner_surf.set("pos", new String[]{"0", "0", "Center-(L/2)"});
                inner_surf.set("r", "R_in");
                inner_surf.set("h", "L");

                String mocsLabel = "Make Outer Cuff Surface";
                GeomFeature outer_surf = model.geom(id).create(im.next("cyl",mocsLabel),"Cylinder");
                outer_surf.label(mocsLabel);
                outer_surf.set("contributeto", mw.get("OUTER CUFF SURFACE"));
                outer_surf.set("pos", new String[]{"0", "0", "Center-(L/2)"});
                outer_surf.set("r", "R_out");
                outer_surf.set("h", "L");

                String ifgnhLabel = "If (No Gap AND No Holes)";
                GeomFeature if_gap_no_holes = model.geom(id).create(im.next("if", ifgnhLabel), "If");
                if_gap_no_holes.label(ifgnhLabel);
                if_gap_no_holes.set("condition", "(Theta==360) && (N_holes==0)");

                String difrdwicsLabel = "Remove Domain Within Inner Cuff Surface";
                GeomFeature dif_remove_ics = model.geom(id).create(im.next("dif", difrdwicsLabel), "Difference");
                dif_remove_ics.label(difrdwicsLabel);
                dif_remove_ics.set("contributeto", im.get("CUFF FINAL"));
                dif_remove_ics.selection("input").named(im.get("OUTER CUFF SURFACE"));
                dif_remove_ics.selection("input2").named(im.get("INNER CUFF SURFACE"));

                String elseifganhLabel = "If (Gap AND No Holes)";
                GeomFeature elseif_gap_noholes = model.geom(id).create(im.next("elseif",elseifganhLabel), "ElseIf");
                elseif_gap_noholes.label(elseifganhLabel);
                elseif_gap_noholes.set("condition", "(Theta<360) && (N_holes==0)");

                String difrmwics1Label = "Remove Domain Within Inner Cuff Surface 1";
                GeomFeature dif_remove_ics1 = model.geom(id).create(im.next("dif",difrmwics1Label), "Difference");
                dif_remove_ics1.label(difrmwics1Label);
                dif_remove_ics1.set("contributeto", im.get("CUFF PRE GAP"));
                dif_remove_ics1.selection("input").named(im.get("OUTER CUFF SURFACE"));
                dif_remove_ics1.selection("input2").named(im.get("INNER CUFF SURFACE"));

                String wpmcgcsLabel = "Make Cuff Gap Cross Section";
                GeomFeature wp_make_cuffgapcx = model.geom(id).create(im.next("wp",wpmcgcsLabel), "WorkPlane");
                wp_make_cuffgapcx.label(wpmcgcsLabel);
                wp_make_cuffgapcx.set("contributeto", im.get("CUFF GAP CROSS SECTION"));
                wp_make_cuffgapcx.set("quickplane", "xz");
                wp_make_cuffgapcx.set("unite", true);
                wp_make_cuffgapcx.geom().create("r1", "Rectangle");
                wp_make_cuffgapcx.geom().feature("r1").label("Cuff Gap Cross Section");
                wp_make_cuffgapcx.geom().feature("r1").set("pos", new String[]{"R_in+((R_out-R_in)/2)", "Center"});
                wp_make_cuffgapcx.geom().feature("r1").set("base", "center");
                wp_make_cuffgapcx.geom().feature("r1").set("size", new String[]{"R_out-R_in", "L"});

                String revmcgLabel = "Make Cuff Gap";
                GeomFeature rev_make_cuffgap = model.geom(id).create(im.next("rev",revmcgLabel), "Revolve");
                rev_make_cuffgap.label(revmcgLabel);
                rev_make_cuffgap.set("contributeto", im.get("CUFF GAP"));
                rev_make_cuffgap.set("angle1", "Theta");
                rev_make_cuffgap.selection("input").set(im.get("Make Cuff Gap Cross Section"));

                String difrcgLabel = "Remove Cuff Gap";
                GeomFeature dif_remove_cuffgap = model.geom(id).create(im.next("dif",difrcgLabel), "Difference");
                dif_remove_cuffgap.label(difrcgLabel);
                dif_remove_cuffgap.set("contributeto", im.get("CUFF FINAL"));
                dif_remove_cuffgap.selection("input").named(im.get("CUFF PRE GAP"));
                dif_remove_cuffgap.selection("input2").named(im.get("CUFF GAP"));

                String rotdc1Label = "Rotate to Default Conformation 1";
                GeomFeature rot_default_conformation1 = model.geom(id).create(im.next("rot",rotdc1Label), "Rotate");
                rot_default_conformation1.label(rotdc1Label);
                rot_default_conformation1.set("rot", "Rot_def");
                rot_default_conformation1.selection("input").named(im.get("CUFF FINAL"));

                String elifngnhLabel = "If (No Gap AND Holes)";
                GeomFeature elif_nogap_noholes = model.geom(id).create(im.next("elseif",elifngnhLabel), "ElseIf");
                elif_nogap_noholes.label(elifngnhLabel);
                elif_nogap_noholes.set("condition", "(Theta==360) && (N_holes>0)");

                String difrdwics2 = "Remove Domain Within Inner Cuff Surface 2";
                GeomFeature dif_remove_domain_inner_cuff2 = model.geom(id).create(im.next("dif",difrdwics2), "Difference");
                dif_remove_domain_inner_cuff2.label(difrdwics2);
                dif_remove_domain_inner_cuff2.set("contributeto", im.get("CUFF PRE HOLES"));
                dif_remove_domain_inner_cuff2.selection("input").named(im.get("OUTER CUFF SURFACE"));
                dif_remove_domain_inner_cuff2.selection("input2").named(im.get("INNER CUFF SURFACE"));

                String econmhsLabel = "Make Hole Shape";
                GeomFeature econ_make_holeshape = model.geom(id).create(im.next("econ",econmhsLabel), "ECone");
                econ_make_holeshape.label(econmhsLabel);
                econ_make_holeshape.set("contributeto", im.get("HOLES"));
                econ_make_holeshape.set("pos", new String[]{"R_in-Buffer_hole/2", "0", "Center+Pitch_holecenter_holecenter/2"});
                econ_make_holeshape.set("axis", new int[]{1, 0, 0});
                econ_make_holeshape.set("semiaxes", new String[]{"D_hole/2", "D_hole/2"});
                econ_make_holeshape.set("h", "(R_out-R_in)+Buffer_hole");
                econ_make_holeshape.set("rat", "R_out/R_in");

                String rotphicLabel = "Position Hole in Cuff";
                GeomFeature rot_pos_hole = model.geom(id).create(im.next("rot",rotphicLabel), "Rotate");
                rot_pos_hole.label(rotphicLabel);
                rot_pos_hole.set("rot", "(360*L_holecenter_cuffseam)/(pi*2*R_in)");
                rot_pos_hole.selection("input").named(im.get("HOLES"));

                String difmichLabel = "Make Inner Cuff Hole";
                GeomFeature dif_make_innercuff_hole = model.geom(id).create(im.next("dif",difmichLabel), "Difference");
                dif_make_innercuff_hole.label(difmichLabel);
                dif_make_innercuff_hole.set("contributeto", im.get("CUFF FINAL"));
                dif_make_innercuff_hole.selection("input").named(im.get("CUFF PRE HOLES"));
                dif_make_innercuff_hole.selection("input2").named(im.get("HOLES"));

                String elifgahLabel = "If (Gap AND Holes)";
                GeomFeature elif_gap_and_holes = model.geom(id).create(im.next("elseif",elifgahLabel), "ElseIf");
                elif_gap_and_holes.label(elifgahLabel);
                elif_gap_and_holes.set("condition", "(Theta<360) && (N_holes>0)");

                String difrdwics3Label = "Remove Domain Within Inner Cuff Surface 3";
                GeomFeature dif_remove_domain_inner_cuff3 = model.geom(id).create(im.next("dif",difrdwics3Label), "Difference");
                dif_remove_domain_inner_cuff3.label(difrdwics3Label);
                dif_remove_domain_inner_cuff3.set("contributeto", im.get("CUFF PRE GAP PRE HOLES"));
                dif_remove_domain_inner_cuff3.selection("input").named(im.get("OUTER CUFF SURFACE"));
                dif_remove_domain_inner_cuff3.selection("input2").named(im.get("INNER CUFF SURFACE"));

                String wpmcgcs1Label  = "Make Cuff Gap Cross Section 1";
                GeomFeature wp_make_cuffgapcx1 = model.geom(id).create(im.next("wp",wpmcgcs1Label), "WorkPlane");
                wp_make_cuffgapcx1.label(wpmcgcs1Label);
                wp_make_cuffgapcx1.set("contributeto", im.get("CUFF GAP CROSS SECTION"));
                wp_make_cuffgapcx1.set("quickplane", "xz");
                wp_make_cuffgapcx1.set("unite", true);
                wp_make_cuffgapcx1.geom().create("r1", "Rectangle");
                wp_make_cuffgapcx1.geom().feature("r1").label("Cuff Gap Cross Section");
                wp_make_cuffgapcx1.geom().feature("r1").set("pos", new String[]{"R_in+((R_out-R_in)/2)", "Center"});
                wp_make_cuffgapcx1.geom().feature("r1").set("base", "center");
                wp_make_cuffgapcx1.geom().feature("r1").set("size", new String[]{"R_out-R_in", "L"});

                String revmcg1Label = "Make Cuff Gap 1";
                GeomFeature rev_make_cuffgap1 = model.geom(id).create(im.next("rev",revmcg1Label), "Revolve");
                rev_make_cuffgap1.label(revmcg1Label);
                rev_make_cuffgap1.set("contributeto", im.get("CUFF GAP"));
                rev_make_cuffgap1.set("angle1", "Theta");
                rev_make_cuffgap1.selection("input").named(im.get("CUFF GAP CROSS SECTION"));

                String difrcg1Label = "Remove Cuff Gap 1";
                GeomFeature dif_remove_cuffgap1 = model.geom(id).create(im.next("dif",difrcg1Label), "Difference");
                dif_remove_cuffgap1.label(difrcg1Label);
                dif_remove_cuffgap1.set("contributeto", im.get("CUFF wGAP PRE HOLES"));
                dif_remove_cuffgap1.selection("input").named(im.get("CUFF PRE GAP PRE HOLES"));
                dif_remove_cuffgap1.selection("input2").named(im.get("CUFF GAP"));

                String econmhs1Label = "Make Hole Shape 1";
                GeomFeature econ_makehole1 = model.geom(id).create(im.next("econ",econmhs1Label), "ECone");
                econ_makehole1.label(econmhs1Label);
                econ_makehole1.set("contributeto", im.get("HOLES"));
                econ_makehole1.set("pos", new String[]{"R_in-Buffer_hole/2", "0", "Center+Pitch_holecenter_holecenter/2"});
                econ_makehole1.set("axis", new int[]{1, 0, 0});
                econ_makehole1.set("semiaxes", new String[]{"D_hole/2", "D_hole/2"});
                econ_makehole1.set("h", "(R_out-R_in)+Buffer_hole");
                econ_makehole1.set("rat", "R_out/R_in");

                String rotphic1Label = "Position Hole in Cuff 1";
                GeomFeature rot_position_hole1 = model.geom(id).create(im.next("rot",rotphic1Label), "Rotate");
                rot_position_hole1.label(rotphic1Label);
                rot_position_hole1.set("rot", "(360*L_holecenter_cuffseam)/(pi*2*R_in)");
                rot_position_hole1.selection("input").named(im.get("HOLES"));

                String difmich1Label = "Make Inner Cuff Hole 1";
                GeomFeature dif_make_hole1 = model.geom(id).create(im.next("dif",difmich1Label), "Difference");
                dif_make_hole1.label(difmich1Label);
                dif_make_hole1.set("contributeto", im.get("CUFF FINAL"));
                dif_make_hole1.selection("input").named(im.get("CUFF wGAP PRE HOLES"));
                dif_make_hole1.selection("input2").named(im.get("HOLES"));

                String rotdcLabel = "Rotate to Default Conformation";
                GeomFeature rot_default_conformation = model.geom(id).create(im.next("rot",rotdcLabel), "Rotate");
                rot_default_conformation.label(rotdcLabel);
                rot_default_conformation.set("rot", "Rot_def");
                rot_default_conformation.selection("input").named(im.get("CUFF FINAL"));

                String endifLabel = "End";
                GeomFeature endif = model.geom(id).create(im.next("endif", endifLabel), "EndIf");
                endif.label(endifLabel);

                model.geom(id).run();
                break;
            case "RibbonContact_Primitive":

                mp.set("Thk_elec", "0.1 [mm]");
                mp.set("L_elec", "3 [mm]");
                mp.set("R_in", "1 [mm]");
                mp.set("Recess", "0.1 [mm]");
                mp.set("Center", "10 [mm]");
                mp.set("Theta_contact", "100 [deg]");
                mp.set("Rot_def", "0 [deg]");

                String[] cselRiCLabels = {
                        "CONTACT CROSS SECTION",
                        "RECESS CROSS SECTION",
                        "SRC",
                        "CONTACT FINAL",
                        "RECESS FINAL"
                };
                for (String cselRiCLabel: cselRiCLabels) {
                    model.geom(id).selection().create(im.next("csel", cselRiCLabel), "CumulativeSelection")
                            .label(cselRiCLabel);
                }

                String wpccxLabel = "Contact Cross Section";
                GeomFeature wp_contact_cx = model.geom(id).create(im.next("wp",wpccxLabel), "WorkPlane");
                wp_contact_cx.label(wpccxLabel);
                wp_contact_cx.set("contributeto",im.get("CONTACT CROSS SECTION"));
                wp_contact_cx.set("quickplane", "xz");
                wp_contact_cx.set("unite", true);
                wp_contact_cx.geom().create("r1", "Rectangle");
                wp_contact_cx.geom().feature("r1").label("Contact Cross Section");
                wp_contact_cx.geom().feature("r1")
                        .set("pos", new String[]{"R_in+Recess+Thk_elec/2", "Center"});
                wp_contact_cx.geom().feature("r1").set("base", "center");
                wp_contact_cx.geom().feature("r1").set("size", new String[]{"Thk_elec", "L_elec"});

                String revmcLabel = "Make Contact";
                GeomFeature rev_make_contact = model.geom(id).create(im.next("rev",revmcLabel), "Revolve");
                rev_make_contact.label("Make Contact");
                rev_make_contact.set("contributeto", im.get("CONTACT FINAL"));
                rev_make_contact.set("angle1", "Rot_def");
                rev_make_contact.set("angle2", "Rot_def+Theta_contact");
                rev_make_contact.selection("input").named(im.get("CONTACT CROSS SECTION"));

                String ifrecessLabel = "IF RECESS";
                GeomFeature if_recess = model.geom(id).create(im.next("if",ifrecessLabel), "If");
                if_recess.set("condition", "Recess>0");
                if_recess.label(ifrecessLabel);

                String wprcx1Label = "Recess Cross Section 1";
                GeomFeature wp_recess_cx1 = model.geom(id).create(im.next("wp",wprcx1Label), "WorkPlane");
                wp_recess_cx1.label(wprcx1Label);
                wp_recess_cx1.set("contributeto", im.get("RECESS CROSS SECTION"));
                wp_recess_cx1.set("quickplane", "xz");
                wp_recess_cx1.set("unite", true);

                im.next(im.get("Recess Cross Section 1") + "_" + "csel", "MY_NESTED_CSEL");
                wp_recess_cx1.geom().selection().create(im.get("MY_NESTED_CSEL").split("_")[1], "CumulativeSelection"); // TODO: how do we handle sections within a selection?
                wp_recess_cx1.geom().selection("csel1").label("Cumulative Selection 1"); // wp1_csel

                wp_recess_cx1.geom().selection().create("csel2", "CumulativeSelection");
                wp_recess_cx1.geom().selection("csel2").label("RECESS CROSS SECTION");

                wp_recess_cx1.geom().create("r1", "Rectangle");
                wp_recess_cx1.geom().feature("r1").label("Recess Cross Section");
                wp_recess_cx1.geom().feature("r1").set("contributeto", im.get("RECESS CROSS SECTION")); // TODO see above
                wp_recess_cx1.geom().feature("r1").set("pos", new String[]{"R_in+Recess/2", "Center"});
                wp_recess_cx1.geom().feature("r1").set("base", "center");
                wp_recess_cx1.geom().feature("r1").set("size", new String[]{"Recess", "L_elec"});

                String revmrLabel = "Make Recess";
                GeomFeature rev_make_racess = model.geom(id).create(im.next("rev",revmrLabel), "Revolve");
                rev_make_racess.label(revmrLabel);
                rev_make_racess.set("contributeto", im.get("RECESS FINAL"));
                rev_make_racess.set("angle1", "Rot_def");
                rev_make_racess.set("angle2", "Rot_def+Theta_contact");
                rev_make_racess.selection("input").named(im.get("RECESS CROSS SECTION"));

                endifLabel = "EndIf";
                model.geom(id).create(im.next("endif"), endifLabel).label(endifLabel);

                String srcLabel = "Src";
                GeomFeature src = model.geom(id).create(im.next("pt",srcLabel), "Point");
                src.label(srcLabel);
                src.set("contributeto", im.get("SRC"));
                src.set("p", new String[]{"(R_in+Recess+Thk_elec/2)*cos(Rot_def+Theta_contact/2)", "(R_in+Recess+Thk_elec/2)*sin(Rot_def+Theta_contact/2)", "Center"});

                model.geom(id).run();
                break;
            case "WireContact_Primitive":
                model.geom(id).inputParam().set("R_conductor", "r_conductor_P");
                model.geom(id).inputParam().set("R_in", "R_in_P");
                model.geom(id).inputParam().set("Center", "Center_P");
                model.geom(id).inputParam().set("Pitch", "Pitch_P");
                model.geom(id).inputParam().set("Sep_conductor", "sep_conductor_P");
                model.geom(id).inputParam().set("Theta_conductor", "theta_conductor_P");

                String[] cselWCLabels = {
                        "CONTACT CROSS SECTION",
                        "CONTACT FINAL",
                        "SRC"
                };
                for (String cselWCLabel: cselWCLabels) {
                    model.geom(id).selection().create(im.next("csel", cselWCLabel), "CumulativeSelection")
                            .label(cselWCLabel);
                }

                model.geom(id).create(mw.next("wp","Contact Cross Section"), "WorkPlane");
                model.geom(id).feature(mw.get("Contact Cross Section")).label("Contact Cross Section");
                model.geom(id).feature(mw.get("Contact Cross Section")).set("contributeto", mw.get("CONTACT CROSS SECTION"));
                model.geom(id).feature(mw.get("Contact Cross Section")).set("quickplane", "zx");
                model.geom(id).feature(mw.get("Contact Cross Section")).set("unite", true);
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().selection().create(mw.get("CONTACT CROSS SECTION"), "CumulativeSelection");
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().selection(mw.get("CONTACT CROSS SECTION")).label("CONTACT CROSS SECTION");
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().create("c1", "Circle"); // TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("c1").label("Contact Cross Section");
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("c1").set("contributeto", mw.get("CONTACT CROSS SECTION"));
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("c1")
                        .set("pos", new String[]{"Center", "R_in-R_conductor-Sep_conductor"});
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("c1").set("r", "R_conductor");

                model.geom(id).create(mw.next("rev","Make Contact"), "Revolve");
                model.geom(id).feature(mw.get("Make Contact")).label("Make Contact");
                model.geom(id).feature(mw.get("Make Contact")).set("contributeto", mw.get("CONTACT FINAL"));
                model.geom(id).feature(mw.get("Make Contact")).set("angle2", "Theta_conductor");
                model.geom(id).feature(mw.get("Make Contact")).set("axis", new int[]{1, 0});
                model.geom(id).feature(mw.get("Make Contact")).selection("input").named(mw.get("CONTACT CROSS SECTION"));

                model.geom(id).create(mw.next("pt","Src"), "Point");
                model.geom(id).feature(mw.get("Src")).label("Src");
                model.geom(id).feature(mw.get("Src")).set("contributeto", mw.get("SRC"));
                model.geom(id).feature(mw.get("Src"))
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

                String[] cselCCLabels = {
                        "CONTACT CUTTER IN",
                        "PRE CUT CONTACT",
                        "RECESS FINAL",
                        "RECESS OVERSHOOT",
                        "SRC",
                        "PLANE FOR CONTACT",
                        "CONTACT FINAL",
                        "CONTACT CUTTER OUT",
                        "BASE CONTACT PLANE (PRE ROTATION)",
                        "PLANE FOR RECESS",
                        "PRE CUT RECESS",
                        "RECESS CUTTER IN",
                        "RECESS CUTTER OUT"
                };
                for (String cselCCLabel: cselCCLabels) {
                    model.geom(id).selection().create(im.next("csel", cselCCLabel), "CumulativeSelection")
                            .label(cselCCLabel);
                }

                model.geom(id).create(mw.next("wp", "Base Plane (Pre Rrotation)"), "WorkPlane");
                model.geom(id).feature(mw.get("Base Plane (Pre Rrotation)")).label("Base Plane (Pre Rrotation)");
                model.geom(id).feature(mw.get("Base Plane (Pre Rrotation)")).set("contributeto", mw.get("BASE PLANE (PRE ROTATION)"));
                model.geom(id).feature(mw.get("Base Plane (Pre Rrotation)")).set("quickplane", "yz");
                model.geom(id).feature(mw.get("Base Plane (Pre Rrotation)")).set("unite", true);

                model.geom(id).create(mw.next("if","If Recess"), "If");
                model.geom(id).feature(mw.get("If Recess")).label("If Recess");
                model.geom(id).feature(mw.get("If Recess")).set("condition", "Recess>0");

                model.geom(id).create(mw.next("wp","Rotated Plane for Recess"), "WorkPlane");
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).label("Rotated Plane for Recess");
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).set("contributeto", mw.get("PLANE FOR RECESS"));
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).set("planetype", "transformed");
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).set("workplane", mw.get("Rotated Plane for Recess"));
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).set("transaxis", new int[]{0, 1, 0});
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).set("transrot", "Rotation_angle");
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).set("unite", true);
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().selection().create(mw.next("csel","CONTACT OUTLINE SHAPE"), "CumulativeSelection"); // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().selection(mw.get("CONTACT OUTLINE SHAPE")).label("CONTACT OUTLINE SHAPE");
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().create(mw.next("if","If Contact Surface is Circle"), "If");                                // TODO: this is wrong how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().feature(mw.get("If Contact Surface is Circle")).label("If Contact Surface is Circle");
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().feature(mw.get("If Contact Surface is Circle")).set("condition", "Round_def==1");
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().create(mw.next("e","Contact Outline"), "Ellipse");                            // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().feature(mw.get("Contact Outline")).label("Contact Outline");
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().feature(mw.get("Contact Outline")).set("contributeto", mw.get("CONTACT OUTLINE SHAPE"));
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().feature(mw.get("Contact Outline")).set("pos", new String[]{"0", "Center"});
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().feature(mw.get("Contact Outline"))
                        .set("semiaxes", new String[]{"A_ellipse_contact", "Diam_contact/2"});
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().create(mw.next("elseif","Else If Contact Outline is Circle"), "ElseIf");
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().feature(mw.get("Else If Contact Outline is Circle")).label("Else If Contact Outline is Circle");
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().feature(mw.get("Else If Contact Outline is Circle")).set("condition", "Round_def==2");
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().create(mw.next("e","Contact Outline 1"), "Ellipse");
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().feature(mw.get("Contact Outline 1")).label("Contact Outline 1");
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().feature(mw.get("Contact Outline 1")).set("contributeto", "csel1"); // TODO: this is wrong --- probably lots of errors in this region
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().feature(mw.get("Contact Outline 1")).set("pos", new String[]{"0", "Center"});
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().feature(mw.get("Contact Outline 1"))
                        .set("semiaxes", new String[]{"Diam_contact/2", "Diam_contact/2"});
                model.geom(id).feature(mw.get("Rotated Plane for Recess")).geom().create(mw.next("endif"), "EndIf");

                model.geom(id).create(mw.next("ext","Make Pre Cut Recess Domains"), "Extrude");
                model.geom(id).feature(mw.get("Make Pre Cut Recess Domains")).label("Make Pre Cut Recess Domains");
                model.geom(id).feature(mw.get("Make Pre Cut Recess Domains")).set("contributeto", mw.get("PRE CUT RECESS"));
                model.geom(id).feature(mw.get("Make Pre Cut Recess Domains")).setIndex("distance", "R_in+Recess+Overshoot", 0);
                model.geom(id).feature(mw.get("Make Pre Cut Recess Domains")).selection("input").named(mw.get("PLANE FOR RECESS"));

                model.geom(id).create(mw.next("cyl","Recess Cut In"), "Cylinder");
                model.geom(id).feature(mw.get("Recess Cut In")).label("Recess Cut In");
                model.geom(id).feature(mw.get("Recess Cut In")).set("contributeto", mw.get("RECESS CUTTER IN"));
                model.geom(id).feature(mw.get("Recess Cut In")).set("pos", new String[]{"0", "0", "Center-L/2"});
                model.geom(id).feature(mw.get("Recess Cut In")).set("r", "R_in");
                model.geom(id).feature(mw.get("Recess Cut In")).set("h", "L");

                model.geom(id).create(mw.next("cyl","Recess Cut Out"), "Cylinder");
                model.geom(id).feature(mw.get("Recess Cut Out")).label("Recess Cut Out");
                model.geom(id).feature(mw.get("Recess Cut Out")).set("contributeto", mw.get("RECESS CUTTER OUT"));
                model.geom(id).feature(mw.get("Recess Cut Out")).set("pos", new String[]{"0", "0", "Center-L/2"});
                model.geom(id).feature(mw.get("Recess Cut Out")).set("r", "R_in+Recess");
                model.geom(id).feature(mw.get("Recess Cut Out")).set("h", "L");

                model.geom(id).create(mw.next("dif","Execute Recess Cut In"), "Difference");
                model.geom(id).feature(mw.get("Execute Recess Cut In")).label("Execute Recess Cut In");
                model.geom(id).feature(mw.get("Execute Recess Cut In")).set("contributeto", mw.get("RECESS FINAL"));
                model.geom(id).feature(mw.get("Execute Recess Cut In")).selection("input").named(mw.get("PRE CUT RECESS"));
                model.geom(id).feature(mw.get("Execute Recess Cut In")).selection("input2").named(mw.get("RECESS CUTTER IN"));

                model.geom(id).create(mw.next("pard", "Partition Outer Recess Domain"), "PartitionDomains");
                model.geom(id).feature(mw.get("Partition Outer Recess Domain")).label("Partition Outer Recess Domain");
                model.geom(id).feature(mw.get("Partition Outer Recess Domain")).set("contributeto", mw.get("RECESS FINAL"));
                model.geom(id).feature(mw.get("Partition Outer Recess Domain")).set("partitionwith", "objects");
                model.geom(id).feature(mw.get("Partition Outer Recess Domain")).set("keepobject", false);
                model.geom(id).feature(mw.get("Partition Outer Recess Domain")).selection("domain").named(mw.get("PRE CUT RECESS"));
                model.geom(id).feature(mw.get("Partition Outer Recess Domain")).selection("object").named(mw.get("RECESS CUTTER OUT"));

                model.geom(id).create(mw.next("ballsel","Select Overshoot"), "BallSelection");
                model.geom(id).feature(mw.get("Select Overshoot")).label("Select Overshoot");
                model.geom(id).feature(mw.get("Select Overshoot")).set("posx", "(R_in+Recess+Overshoot/2)*cos(Rotation_angle)");
                model.geom(id).feature(mw.get("Select Overshoot")).set("posy", "(R_in+Recess+Overshoot/2)*sin(Rotation_angle)");
                model.geom(id).feature(mw.get("Select Overshoot")).set("posz", "Center");
                model.geom(id).feature(mw.get("Select Overshoot")).set("r", 1);
                model.geom(id).feature(mw.get("Select Overshoot")).set("contributeto", mw.get("RECESS OVERSHOOT"));

                model.geom(id).create(mw.next("del","Delete Recess Overshoot"), "Delete");
                model.geom(id).feature(mw.get("Delete Recess Overshoot")).label("Delete Recess Overshoot");
                model.geom(id).feature(mw.get("Delete Recess Overshoot")).selection("input").init(3);                                         // TODO: not sure what this means, look closer in GUI to see if it is clear there
                model.geom(id).feature(mw.get("Delete Recess Overshoot")).selection("input").named(mw.get("RECESS OVERSHOOT"));

                model.geom(id).create(mw.next("endif"), "EndIf");

                String gfKey = mw.next("wp");

                GeomFeature gf = model.geom(id).feature(gfKey);

                model.geom(id).create(gfKey, "WorkPlane");
                gf.label("Rotated Plane for Contact");

                model.geom(id).feature(mw.get("Rotated Plane for Contact")).set("contributeto", mw.get("PLANE FOR CONTACT"));
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).set("planetype", "transformed");
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).set("workplane", mw.get("Base Plane (Pre Rrotation)"));
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).set("transaxis", new int[]{0, 1, 0});
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).set("transrot", "Rotation_angle");
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).set("unite", true);
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().selection().create("csel1", "CumulativeSelection");    // TODO
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().selection("csel1").label("CONTACT OUTLINE SHAPE");     // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().create("if1", "If");                               // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().feature("if1").label("If Contact Surface is Circle");  // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().feature("if1").set("condition", "Round_def==1");   // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().create("e1", "Ellipse");                           // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().feature("e1").label("Contact Outline");                // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().feature("e1").set("contributeto", "csel1");            // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().feature("e1").set("pos", new String[]{"0", "Center"}); // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().feature("e1")                                          // TODO: how do we handle sections within a selection?
                        .set("semiaxes", new String[]{"A_ellipse_contact", "Diam_contact/2"});
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().create("elseif1", "ElseIf");                       // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().feature("elseif1").label("Else If Contact Outline is Circle"); // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().feature("elseif1").set("condition", "Round_def==2"); // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().create("e2", "Ellipse");                             // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().feature("e2").label("Contact Outline 1");                // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().feature("e2").set("contributeto", "csel1");              // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().feature("e2").set("pos", new String[]{"0", "Center"});   // TODO: how do we handle sections within a selection?
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().feature("e2")                                            // TODO: how do we handle sections within a selection?
                        .set("semiaxes", new String[]{"Diam_contact/2", "Diam_contact/2"});
                model.geom(id).feature(mw.get("Rotated Plane for Contact")).geom().create("endif1", "EndIf");                           // TODO: how do we handle sections within a selection?


                model.geom(id).create(mw.next("ext","Make Pre Cut Contact Domains"), "Extrude");
                model.geom(id).feature(mw.get("Make Pre Cut Contact Domains")).label("Make Pre Cut Contact Domains");
                model.geom(id).feature(mw.get("Make Pre Cut Contact Domains")).set("contributeto", mw.get("PRE CUT CONTACT"));
                model.geom(id).feature(mw.get("Make Pre Cut Contact Domains")).setIndex("distance", "R_in+Recess+Contact_depth+Overshoot", 0);
                model.geom(id).feature(mw.get("Make Pre Cut Contact Domains")).selection("input").named(mw.get("PLANE FOR CONTACT"));

                model.geom(id).create(mw.next("cyl","Contact Cut In"), "Cylinder");
                model.geom(id).feature(mw.get("Contact Cut In")).label("Contact Cut In");
                model.geom(id).feature(mw.get("Contact Cut In")).set("contributeto", mw.get("CONTACT CUTTER IN"));
                model.geom(id).feature(mw.get("Contact Cut In")).set("pos", new String[]{"0", "0", "Center-L/2"});
                model.geom(id).feature(mw.get("Contact Cut In")).set("r", "R_in+Recess");
                model.geom(id).feature(mw.get("Contact Cut In")).set("h", "L");

                model.geom(id).create(mw.next("cyl","Contact Cut Out"), "Cylinder");
                model.geom(id).feature(mw.get("Contact Cut Out")).label("Contact Cut Out");
                model.geom(id).feature(mw.get("Contact Cut Out")).set("contributeto", mw.get("CONTACT CUTTER OUT"));
                model.geom(id).feature(mw.get("Contact Cut Out")).set("pos", new String[]{"0", "0", "Center-L/2"});
                model.geom(id).feature(mw.get("Contact Cut Out")).set("r", "R_in+Recess+Contact_depth");
                model.geom(id).feature(mw.get("Contact Cut Out")).set("h", "L");

                model.geom(id).create(mw.next("dif","Execute Contact Cut In"), "Difference");
                model.geom(id).feature(mw.get("Execute Contact Cut In")).label("Execute Contact Cut In");
                model.geom(id).feature(mw.get("Execute Contact Cut In")).set("contributeto", mw.get("CONTACT FINAL"));
                model.geom(id).feature(mw.get("Execute Contact Cut In")).selection("input").named("PRE CUT CONTACT");
                model.geom(id).feature(mw.get("Execute Contact Cut In")).selection("input2").named(mw.get("CONTACT CUTTER IN"));

                model.geom(id).create(mw.next("pard","Partition Outer Contact Domain"), "PartitionDomains");
                model.geom(id).feature(mw.get("Partition Outer Contact Domain")).label("Partition Outer Contact Domain"); // added this
                model.geom(id).feature(mw.get("Partition Outer Contact Domain")).set("contributeto", mw.get("CONTACT FINAL"));
                model.geom(id).feature(mw.get("Partition Outer Contact Domain")).set("partitionwith", "objects");
                model.geom(id).feature(mw.get("Partition Outer Contact Domain")).set("keepobject", false);
                model.geom(id).feature(mw.get("Partition Outer Contact Domain")).selection("domain").named(mw.get("PRE CUT CONTACT"));
                model.geom(id).feature(mw.get("Partition Outer Contact Domain")).selection("object").named(mw.get("CONTACT CUTTER OUT"));

                model.geom(id).create(mw.next("ballsel", "Select Overshoot 1"), "BallSelection");
                model.geom(id).feature(mw.get("Select Overshoot 1")).label("Select Overshoot 1");
                model.geom(id).feature(mw.get("Select Overshoot 1"))
                        .set("posx", "(R_in+Recess+Contact_depth+Overshoot/2)*cos(Rotation_angle)");
                model.geom(id).feature(mw.get("Select Overshoot 1"))
                        .set("posy", "(R_in+Recess+Contact_depth+Overshoot/2)*sin(Rotation_angle)");
                model.geom(id).feature(mw.get("Select Overshoot 1")).set("posz", "Center");
                model.geom(id).feature(mw.get("Select Overshoot 1")).set("r", 1);
                model.geom(id).feature(mw.get("Select Overshoot 1")).set("contributeto", mw.get("RECESS OVERSHOOT"));

                model.geom(id).create(mw.next("del","Delete Recess Overshoot 1"), "Delete");
                model.geom(id).feature(mw.get("Delete Recess Overshoot 1")).label("Delete Recess Overshoot 1");
                model.geom(id).feature(mw.get("Delete Recess Overshoot 1")).selection("input").init(3);
                model.geom(id).feature(mw.get("Delete Recess Overshoot 1")).selection("input").named(mw.get("RECESS OVERSHOOT"));

                model.geom(id).create(mw.next("pt","Src"), "Point");
                model.geom(id).feature(mw.get("Src")).label("Src");
                model.geom(id).feature(mw.get("Src")).set("contributeto", mw.get("SRC"));
                model.geom(id).feature(mw.get("Src"))
                        .set("p", new String[]{"(R_in+Recess+Contact_depth/2)*cos(Rotation_angle)", "(R_in+Recess+Contact_depth/2)*sin(Rotation_angle)", "Center"});
                model.geom(id).run();
                break;
            case "HelicalCuffnContact_Primitive":
                model.geom(id).inputParam().set("Center", "Center_LN");

                String[] cselHCCLabels = {
                        "PC1",
                        "Cuffp1",
                        "SEL END P1",
                        "PC2",
                        "SRC",
                        "Cuffp2",
                        "Conductorp2",
                        "SEL END P2",
                        "Cuffp3",
                        "PC3"
                };
                for (String cselHCCLabel: cselHCCLabels) {
                    model.geom(id).selection().create(im.next("csel", cselHCCLabel), "CumulativeSelection")
                            .label(cselHCCLabel);
                }

                model.geom(id).create(mw.next("wp","Helical Insulator Cross Section Part 1"), "WorkPlane");
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 1")).label("Helical Insulator Cross Section Part 1");
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 1")).set("quickplane", "xz");
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 1")).set("unite", true);
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 1")).geom().selection().create("csel1", "CumulativeSelection");               // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 1")).geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION");          // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 1")).geom().selection().create("csel2", "CumulativeSelection");               // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 1")).geom().selection("csel2").label("HELICAL INSULATOR CROSS SECTION P1");       // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 1")).geom().create("r1", "Rectangle");                                        // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 1")).geom().feature("r1").label("Helical Insulator Cross Section Part 1");        // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 1")).geom().feature("r1").set("contributeto", "csel2");                           // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 1")).geom().feature("r1")                                                         // TODO
                        .set("pos", new String[]{"r_cuff_in_LN+(thk_cuff_LN/2)", "Center-(L_cuff_LN/2)"});
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 1")).geom().feature("r1").set("base", "center");                                  // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 1")).geom().feature("r1").set("size", new String[]{"thk_cuff_LN", "w_cuff_LN"});  // TODO

                model.geom(id).create(mw.next("pc","Parametric Curve Part 1"), "ParametricCurve");
                model.geom(id).feature(mw.get("Parametric Curve Part 1")).label("Parametric Curve Part 1");
                model.geom(id).feature(mw.get("Parametric Curve Part 1")).set("contributeto", mw.get("PC1"));
                model.geom(id).feature(mw.get("Parametric Curve Part 1")).set("parmax", "rev_cuff_LN*(0.75/2.5)");
                model.geom(id).feature(mw.get("Parametric Curve Part 1"))
                        .set("coord", new String[]{"cos(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "sin(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "Center+(L_cuff_LN)*(s/rev_cuff_LN)-(L_cuff_LN/2)"});

                model.geom(id).create(mw.next("swe","Make Cuff Part 1"), "Sweep");
                model.geom(id).feature(mw.get("Make Cuff Part 1")).label("Make Cuff Part 1");
                model.geom(id).feature(mw.get("Make Cuff Part 1")).set("contributeto", mw.get("Cuffp1"));
                model.geom(id).feature(mw.get("Make Cuff Part 1")).set("crossfaces", true);
                model.geom(id).feature(mw.get("Make Cuff Part 1")).set("keep", false);
                model.geom(id).feature(mw.get("Make Cuff Part 1")).set("includefinal", false);
                model.geom(id).feature(mw.get("Make Cuff Part 1")).set("twistcomp", false);
                model.geom(id).feature(mw.get("Make Cuff Part 1")).selection("face").named("wp1_csel2");  // TODO
                model.geom(id).feature(mw.get("Make Cuff Part 1")).selection("edge").named(mw.get("PC1")); // TODO
                model.geom(id).feature(mw.get("Make Cuff Part 1")).selection("diredge").set("pc1(1)", 1); // TODO

                model.geom(id).create(mw.next("ballsel", "Select End Face Part 1"), "BallSelection");
                model.geom(id).feature(mw.get("Select End Face Part 1")).set("entitydim", 2);
                model.geom(id).feature(mw.get("Select End Face Part 1")).label("Select End Face Part 1");
                model.geom(id).feature(mw.get("Select End Face Part 1")).set("posx", "cos(2*pi*rev_cuff_LN*((0.75)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                model.geom(id).feature(mw.get("Select End Face Part 1")).set("posy", "sin(2*pi*rev_cuff_LN*((0.75)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                model.geom(id).feature(mw.get("Select End Face Part 1"))
                        .set("posz", "Center+(L_cuff_LN)*(rev_cuff_LN*((0.75)/2.5)/rev_cuff_LN)-(L_cuff_LN/2)");
                model.geom(id).feature(mw.get("Select End Face Part 1")).set("r", 1);
                model.geom(id).feature(mw.get("Select End Face Part 1")).set("contributeto", mw.get("SEL END P1"));

                model.geom(id).create(mw.next("wp","Helical Insulator Cross Section Part 2"), "WorkPlane");
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 2")).label("Helical Insulator Cross Section Part 2");
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 2")).set("planetype", "faceparallel");
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 2")).set("unite", true);
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 2")).selection("face").named("csel3");                                        // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 2")).geom().selection().create("csel1", "CumulativeSelection");           // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 2")).geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION P2");   // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 2")).geom().selection().create("csel2", "CumulativeSelection");           // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 2")).geom().selection("csel2").label("HELICAL CONDUCTOR CROSS SECTION P2");   // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 2")).geom().create("r1", "Rectangle"); // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 2")).geom().feature("r1").label("Helical Insulator Cross Section Part 2"); // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 2")).geom().feature("r1").set("contributeto", "csel1");                       // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 2")).geom().feature("r1").set("base", "center"); // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 2")).geom().feature("r1").set("size", new String[]{"thk_cuff_LN", "w_cuff_LN"}); // TODO

                model.geom(id).create(mw.next("wp","Helical Conductor Cross Section Part 2"), "WorkPlane");
                model.geom(id).feature(mw.next("wp","Helical Conductor Cross Section Part 2")).label("Helical Conductor Cross Section Part 2");
                model.geom(id).feature(mw.next("wp","Helical Conductor Cross Section Part 2")).set("planetype", "faceparallel");
                model.geom(id).feature(mw.next("wp","Helical Conductor Cross Section Part 2")).set("unite", true);
                model.geom(id).feature(mw.next("wp","Helical Conductor Cross Section Part 2")).selection("face").named("csel3");                                      // TODO
                model.geom(id).feature(mw.next("wp","Helical Conductor Cross Section Part 2")).geom().selection().create("csel1", "CumulativeSelection");         // TODO
                model.geom(id).feature(mw.next("wp","Helical Conductor Cross Section Part 2")).geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION P2"); // TODO
                model.geom(id).feature(mw.next("wp","Helical Conductor Cross Section Part 2")).geom().selection().create("csel2", "CumulativeSelection");         // TODO
                model.geom(id).feature(mw.next("wp","Helical Conductor Cross Section Part 2")).geom().selection("csel2").label("HELICAL CONDUCTOR CROSS SECTION P2"); // TODO
                model.geom(id).feature(mw.next("wp","Helical Conductor Cross Section Part 2")).geom().create("r2", "Rectangle");
                model.geom(id).feature(mw.next("wp","Helical Conductor Cross Section Part 2")).geom().feature("r2").label("Helical Conductor Cross Section Part 2");  // TODO
                model.geom(id).feature(mw.next("wp","Helical Conductor Cross Section Part 2")).geom().feature("r2").set("contributeto", "csel2");                     // TODO
                model.geom(id).feature(mw.next("wp","Helical Conductor Cross Section Part 2")).geom().feature("r2").set("pos", new String[]{"(thk_elec_LN-thk_cuff_LN)/2", "0"});
                model.geom(id).feature(mw.next("wp","Helical Conductor Cross Section Part 2")).geom().feature("r2").set("base", "center");
                model.geom(id).feature(mw.next("wp","Helical Conductor Cross Section Part 2")).geom().feature("r2").set("size", new String[]{"thk_elec_LN", "w_elec_LN"});

                model.geom(id).create(mw.next("pc","Parametric Curve Part 2"), "ParametricCurve");
                model.geom(id).feature(mw.get("Parametric Curve Part 2")).label("Parametric Curve Part 2");
                model.geom(id).feature(mw.get("Parametric Curve Part 2")).set("contributeto", "csel4");
                model.geom(id).feature(mw.get("Parametric Curve Part 2")).set("parmin", "rev_cuff_LN*(0.75/2.5)");
                model.geom(id).feature(mw.get("Parametric Curve Part 2")).set("parmax", "rev_cuff_LN*((0.75+1)/2.5)");
                model.geom(id).feature(mw.get("Parametric Curve Part 2"))
                        .set("coord", new String[]{"cos(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "sin(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "Center+(L_cuff_LN)*(s/rev_cuff_LN)-(L_cuff_LN/2)"});

                model.geom(id).create(mw.next("swe","Make Cuff Part 2"), "Sweep");
                model.geom(id).feature(mw.get("Make Cuff Part 2")).label("Make Cuff Part 2");
                model.geom(id).feature(mw.get("Make Cuff Part 2")).set("contributeto", mw.get("Cuffp2"));
                model.geom(id).feature(mw.get("Make Cuff Part 2")).set("crossfaces", true);
                model.geom(id).feature(mw.get("Make Cuff Part 2")).set("includefinal", false);
                model.geom(id).feature(mw.get("Make Cuff Part 2")).set("twistcomp", false);
                model.geom(id).feature(mw.get("Make Cuff Part 2")).selection("face").named("wp2_csel1"); //TODO
                model.geom(id).feature(mw.get("Make Cuff Part 2")).selection("edge").named("csel4"); //TODO
                model.geom(id).feature(mw.get("Make Cuff Part 2")).selection("diredge").set("pc2(1)", 1); //TODO

                model.geom(id).create(mw.next("swe","Make Conductor Part 2"), "Sweep");
                model.geom(id).feature(mw.get("Make Conductor Part 2")).label("Make Conductor Part 2");
                model.geom(id).feature(mw.get("Make Conductor Part 2")).set("contributeto", mw.get("Conductorp2"));
                model.geom(id).feature(mw.get("Make Conductor Part 2")).set("crossfaces", true);
                model.geom(id).feature(mw.get("Make Conductor Part 2")).set("keep", false);
                model.geom(id).feature(mw.get("Make Conductor Part 2")).set("includefinal", false);
                model.geom(id).feature(mw.get("Make Conductor Part 2")).set("twistcomp", false);
                model.geom(id).feature(mw.get("Make Conductor Part 2")).selection("face").named("wp3_csel2"); //TODO
                model.geom(id).feature(mw.get("Make Conductor Part 2")).selection("edge").named(mw.get("PC2")); //TODO
                model.geom(id).feature(mw.get("Make Conductor Part 2")).selection("diredge").set("pc2(1)", 1); //TODO

                model.geom(id).create(mw.next("ballsel","Select End Face Part 2"), "BallSelection");
                model.geom(id).feature(mw.get("Select End Face Part 2")).set("entitydim", 2);
                model.geom(id).feature(mw.get("Select End Face Part 2")).label("Select End Face Part 2");
                model.geom(id).feature(mw.get("Select End Face Part 2"))
                        .set("posx", "cos(2*pi*rev_cuff_LN*((0.75+1)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                model.geom(id).feature(mw.get("Select End Face Part 2"))
                        .set("posy", "sin(2*pi*rev_cuff_LN*((0.75+1)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                model.geom(id).feature(mw.get("Select End Face Part 2"))
                        .set("posz", "Center+(L_cuff_LN)*(rev_cuff_LN*((0.75+1)/2.5)/rev_cuff_LN)-(L_cuff_LN/2)");
                model.geom(id).feature(mw.get("Select End Face Part 2")).set("r", 1);
                model.geom(id).feature(mw.get("Select End Face Part 2")).set("contributeto", mw.get("SEL END P2"));

                model.geom(id).create(mw.next("wp","Helical Insulator Cross Section Part 3"), "WorkPlane");
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 3")).label("Helical Insulator Cross Section Part 3");
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 3")).set("planetype", "faceparallel");
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 3")).set("unite", true);
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 3")).selection("face").named(mw.get("SEL END P2"));
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 3")).geom().selection().create("csel1", "CumulativeSelection"); //TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 3")).geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION P3"); //TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 3")).geom().create("r1", "Rectangle"); // TODO
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 3")).geom().feature("r1").label("Helical Insulator Cross Section Part 3");
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 3")).geom().feature("r1").set("contributeto", "csel1"); //TODO - might not be necessary? maybe on the ones that are like wp1_csel1 need this actually
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 3")).geom().feature("r1").set("base", "center");
                model.geom(id).feature(mw.get("Helical Insulator Cross Section Part 3")).geom().feature("r1").set("size", new String[]{"thk_cuff_LN", "w_cuff_LN"});

                model.geom(id).create(mw.next("pc","Parametric Curve Part 3"), "ParametricCurve");
                model.geom(id).feature(mw.get("Parametric Curve Part 3")).label("Parametric Curve Part 3");
                model.geom(id).feature(mw.get("Parametric Curve Part 3")).set("contributeto", mw.get("PC3"));
                model.geom(id).feature(mw.get("Parametric Curve Part 3")).set("parmin", "rev_cuff_LN*((0.75+1)/2.5)");
                model.geom(id).feature(mw.get("Parametric Curve Part 3")).set("parmax", "rev_cuff_LN");
                model.geom(id).feature(mw.get("Parametric Curve Part 3"))
                        .set("coord", new String[]{"cos(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "sin(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "Center+(L_cuff_LN)*(s/rev_cuff_LN)-(L_cuff_LN/2)"});

                model.geom(id).create(mw.next("swe","Make Cuff Part 3"), "Sweep");
                model.geom(id).feature(mw.get("Make Cuff Part 3")).label("Make Cuff Part 3");
                model.geom(id).feature(mw.get("Make Cuff Part 3")).set("contributeto", mw.get("Cuffp3"));
                model.geom(id).feature(mw.get("Make Cuff Part 3")).selection("face").named("wp4_csel1"); //TODO
                model.geom(id).feature(mw.get("Make Cuff Part 3")).selection("edge").named(mw.get("PC3"));
                model.geom(id).feature(mw.get("Make Cuff Part 3")).set("keep", false);
                model.geom(id).feature(mw.get("Make Cuff Part 3")).set("twistcomp", false);

                model.geom(id).create(mw.next("pt","SRC"), "Point");
                model.geom(id).feature(mw.get("SRC")).label("src");
                model.geom(id).feature(mw.get("SRC")).set("contributeto", mw.get("SRC"));
                model.geom(id).feature(mw.get("SRC"))
                        .set("p", new String[]{"cos(2*pi*rev_cuff_LN*(1.25/2.5))*((thk_elec_LN/2)+r_cuff_in_LN)", "sin(2*pi*rev_cuff_LN*(1.25/2.5))*((thk_elec_LN/2)+r_cuff_in_LN)", "Center"});
                model.geom(id).run();
                break;
            case "RectangleContact_Primitive":
                model.geom(id).inputParam().set("r_inner_contact", "r_cuff_in_Pitt+recess_Pitt");
                model.geom(id).inputParam().set("r_outer_contact", "r_cuff_in_Pitt+recess_Pitt+thk_contact_Pitt");
                model.geom(id).inputParam().set("z_center", "0 [mm]");
                model.geom(id).inputParam().set("rotation_angle", "0 [deg]");

                String[] cselReCLabels = {
                        "OUTER CONTACT CUTTER",
                        "SEL INNER EXCESS CONTACT",
                        "INNER CONTACT CUTTER",
                        "SEL OUTER EXCESS RECESS",
                        "SEL INNER EXCESS RECESS",
                        "OUTER CUTTER",
                        "FINAL RECESS",
                        "RECESS CROSS SECTION",
                        "OUTER RECESS CUTTER",
                        "RECESS PRE CUTS",
                        "INNER RECESS CUTTER",
                        "FINAL CONTACT",
                        "SEL OUTER EXCESS CONTACT",
                        "SEL OUTER EXCESS",
                        "SEL INNER EXCESS",
                        "BASE CONTACT PLANE (PRE ROTATION)",
                        "SRC",
                        "CONTACT PRE CUTS",
                        "CONTACT CROSS SECTION",
                        "INNER CUFF CUTTER",
                        "OUTER CUFF CUTTER",
                        "FINAL",
                        "INNER CUTTER"
                };
                for (String cselReCLabel: cselReCLabels) {
                    model.geom(id).selection().create(im.next("csel", cselReCLabel), "CumulativeSelection")
                            .label(cselReCLabel);
                }

                model.geom(id).create(mw.next("wp","base plane (pre rotation)"), "WorkPlane");
                model.geom(id).feature(mw.get("base plane (pre rotation)")).label("base plane (pre rotation)");
                model.geom(id).feature(mw.get("base plane (pre rotation)")).set("contributeto", mw.get("BASE CONTACT PLANE (PRE ROTATION)"));
                model.geom(id).feature(mw.get("base plane (pre rotation)")).set("quickplane", "yz");
                model.geom(id).feature(mw.get("base plane (pre rotation)")).set("unite", true);

                model.geom(id).create(mw.next("wp","Contact Cross Section"), "WorkPlane");
                model.geom(id).feature(mw.get("Contact Cross Section")).label("Contact Cross Section");
                model.geom(id).feature(mw.get("Contact Cross Section")).set("contributeto", mw.get("CONTACT CROSS SECTION"));
                model.geom(id).feature(mw.get("Contact Cross Section")).set("planetype", "transformed");
                model.geom(id).feature(mw.get("Contact Cross Section")).set("workplane", mw.get("Contact Cross Section"));
                model.geom(id).feature(mw.get("Contact Cross Section")).set("transaxis", new int[]{0, 1, 0});
                model.geom(id).feature(mw.get("Contact Cross Section")).set("transrot", "rotation_angle");
                model.geom(id).feature(mw.get("Contact Cross Section")).set("unite", true);
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().selection().create("csel1", "CumulativeSelection"); //TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().selection("csel1").label("CONTACT PRE FILLET"); //TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().selection().create("csel2", "CumulativeSelection"); //TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().selection("csel2").label("CONTACT FILLETED"); //TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().create("r1", "Rectangle"); // TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("r1").label("Contact Pre Fillet Corners"); // TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("r1").set("contributeto", "csel1"); // TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("r1").set("pos", new int[]{0, 0}); // TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("r1").set("base", "center"); // TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("r1").set("size", new String[]{"w_contact_Pitt", "z_contact_Pitt"}); // TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().create("fil1", "Fillet"); // TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("fil1").label("Fillet Corners"); // TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("fil1").set("contributeto", "csel2"); //TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("fil1").set("radius", "fillet_contact_Pitt"); // TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("fil1").selection("point").named("csel1"); // TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().create("sca1", "Scale"); // TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("sca1").set("type", "anisotropic"); // TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("sca1")// TODO
                        .set("factor", new String[]{"1", "scale_morph_w_contact_Pitt"});
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("sca1").selection("input").named("csel2"); //TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().create("mov1", "Move"); // TODO
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("mov1").set("disply", "z_center");
                model.geom(id).feature(mw.get("Contact Cross Section")).geom().feature("mov1").selection("input").named("csel2"); //TODO

                model.geom(id).create(mw.next("ext","Make Contact Pre Cuts"), "Extrude");
                model.geom(id).feature(mw.get("Make Contact Pre Cuts")).label("Make Contact Pre Cuts");
                model.geom(id).feature(mw.get("Make Contact Pre Cuts")).set("contributeto", mw.get("CONTACT PRE CUTS"));
                model.geom(id).feature(mw.get("Make Contact Pre Cuts")).setIndex("distance", "2*r_cuff_in_Pitt", 0);
                model.geom(id).feature(mw.get("Make Contact Pre Cuts")).selection("input").named(mw.get("CONTACT CROSS SECTION"));

                model.geom(id).create(mw.next("cyl","Inner Contact Cutter"), "Cylinder");
                model.geom(id).feature(mw.get("Inner Contact Cutter")).label("Inner Contact Cutter");
                model.geom(id).feature(mw.get("Inner Contact Cutter")).set("contributeto", mw.get("INNER CONTACT CUTTER"));
                model.geom(id).feature(mw.get("Inner Contact Cutter")).set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                model.geom(id).feature(mw.get("Inner Contact Cutter")).set("r", "r_inner_contact");
                model.geom(id).feature(mw.get("Inner Contact Cutter")).set("h", "L_cuff_Pitt");

                model.geom(id).create(mw.next("cyl","Outer Contact Cutter"), "Cylinder");
                model.geom(id).feature(mw.get("Outer Contact Cutter")).label("Outer Contact Cutter");
                model.geom(id).feature(mw.get("Outer Contact Cutter")).set("contributeto", mw.get("OUTER CONTACT CUTTER"));
                model.geom(id).feature(mw.get("Outer Contact Cutter")).set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                model.geom(id).feature(mw.get("Outer Contact Cutter")).set("r", "r_outer_contact");
                model.geom(id).feature(mw.get("Outer Contact Cutter")).set("h", "L_cuff_Pitt");

                model.geom(id).create(mw.next("par","Cut Outer Excess"), "Partition");
                model.geom(id).feature(mw.get("Cut Outer Excess")).label("Cut Outer Excess"); // added this
                model.geom(id).feature(mw.get("Cut Outer Excess")).set("contributeto", mw.get("FINAL CONTACT"));
                model.geom(id).feature(mw.get("Cut Outer Excess")).selection("input").named(mw.get("CONTACT PRE CUTS"));
                model.geom(id).feature(mw.get("Cut Outer Excess")).selection("tool").named(mw.get("OUTER CONTACT CUTTER"));

                model.geom(id).create(mw.next("par","Cut Inner Excess"), "Partition");
                model.geom(id).feature(mw.get("Cut Inner Excess")).label("Cut Inner Excess"); // added this
                model.geom(id).feature(mw.get("Cut Inner Excess")).set("contributeto", mw.get("FINAL CONTACT"));
                model.geom(id).feature(mw.get("Cut Inner Excess")).selection("input").named(mw.get("CONTACT PRE CUTS"));
                model.geom(id).feature(mw.get("Cut Inner Excess")).selection("tool").named(mw.get("INNER CONTACT CUTTER"));

                model.geom(id).create(mw.next("ballsel","sel inner excess"), "BallSelection");
                model.geom(id).feature(mw.get("sel inner excess")).label("sel inner excess");
                model.geom(id).feature(mw.get("sel inner excess")).set("posx", "(r_inner_contact/2)*cos(rotation_angle)");
                model.geom(id).feature(mw.get("sel inner excess")).set("posy", "(r_inner_contact/2)*sin(rotation_angle)");
                model.geom(id).feature(mw.get("sel inner excess")).set("posz", "z_center");
                model.geom(id).feature(mw.get("sel inner excess")).set("r", 1);
                model.geom(id).feature(mw.get("sel inner excess")).set("contributeto", mw.get("SEL INNER EXCESS CONTACT"));

                model.geom(id).create(mw.next("ballsel","sel outer excess"), "BallSelection");
                model.geom(id).feature(mw.get("sel outer excess")).label("sel outer excess");
                model.geom(id).feature(mw.get("sel outer excess")).set("posx", "((r_outer_contact+2*r_cuff_in_Pitt)/2)*cos(rotation_angle)");
                model.geom(id).feature(mw.get("sel outer excess")).set("posy", "((r_outer_contact+2*r_cuff_in_Pitt)/2)*sin(rotation_angle)");
                model.geom(id).feature(mw.get("sel outer excess")).set("posz", "z_center");
                model.geom(id).feature(mw.get("sel outer excess")).set("r", 1);
                model.geom(id).feature(mw.get("sel outer excess")).set("contributeto", mw.get("SEL OUTER EXCESS CONTACT"));

                model.geom(id).create(mw.next("del","Delete Inner Excess Contact"), "Delete");
                model.geom(id).feature(mw.get("Delete Inner Excess Contact")).label("Delete Inner Excess Contact");
                model.geom(id).feature(mw.get("Delete Inner Excess Contact")).selection("input").init(3);
                model.geom(id).feature(mw.get("Delete Inner Excess Contact")).selection("input").named(mw.get("SEL INNER EXCESS CONTACT"));

                model.geom(id).create(mw.next("del","Delete Outer Excess Contact"), "Delete");
                model.geom(id).feature(mw.get("Delete Outer Excess Contact")).label("Delete Outer Excess Contact");
                model.geom(id).feature(mw.get("Delete Outer Excess Contact")).selection("input").init(3);
                model.geom(id).feature(mw.get("Delete Outer Excess Contact")).selection("input").named(mw.get("SEL OUTER EXCESS CONTACT"));

                model.geom(id).create(mw.next("if","If Recess"), "If");
                model.geom(id).feature(mw.get("If Recess")).set("condition", "recess_Pitt>0");
                model.geom(id).feature(mw.get("If Recess")).label("If Recess");

                model.geom(id).create(mw.next("wp","Recess Cross Section"), "WorkPlane");
                model.geom(id).feature(mw.get("Recess Cross Section")).label("Recess Cross Section");
                model.geom(id).feature(mw.get("Recess Cross Section")).set("contributeto", mw.get("RECESS CROSS SECTION"));
                model.geom(id).feature(mw.get("Recess Cross Section")).set("planetype", "transformed");
                model.geom(id).feature(mw.get("Recess Cross Section")).set("workplane", mw.get("base plane (pre rotation)"));
                model.geom(id).feature(mw.get("Recess Cross Section")).set("transaxis", new int[]{0, 1, 0});
                model.geom(id).feature(mw.get("Recess Cross Section")).set("transrot", "rotation_angle");
                model.geom(id).feature(mw.get("Recess Cross Section")).set("unite", true);
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().selection().create("csel1", "CumulativeSelection"); // TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().selection("csel1").label("CONTACT PRE FILLET");// TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().selection().create("csel2", "CumulativeSelection");// TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().selection("csel2").label("CONTACT FILLETED");// TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().selection().create("csel3", "CumulativeSelection");// TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().selection("csel3").label("RECESS PRE FILLET");// TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().selection().create("csel4", "CumulativeSelection");// TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().selection("csel4").label("RECESS FILLETED");// TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().create("r1", "Rectangle");
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().feature("r1").label("Recess Pre Fillet Corners");// TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().feature("r1").set("contributeto", "csel3");// TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().feature("r1").set("pos", new int[]{0, 0});
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().feature("r1").set("base", "center");
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().feature("r1").set("size", new String[]{"w_contact_Pitt", "z_contact_Pitt"});
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().create("fil1", "Fillet"); // TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().feature("fil1").label("Fillet Corners"); // TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().feature("fil1").set("contributeto", "csel4");// TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().feature("fil1").set("radius", "fillet_contact_Pitt");
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().feature("fil1").selection("point").named("csel3");// TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().create("sca1", "Scale"); // TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().feature("sca1").set("type", "anisotropic"); // TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().feature("sca1") // TODO
                        .set("factor", new String[]{"1", "scale_morph_w_contact_Pitt"});
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().feature("sca1").selection("input").named("csel4");// TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().create("mov1", "Move"); // TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().feature("mov1").set("disply", "z_center"); // TODO
                model.geom(id).feature(mw.get("Recess Cross Section")).geom().feature("mov1").selection("input").named("csel4");// TODO

                model.geom(id).create(mw.next("ext", "Make Recess Pre Cuts 1"), "Extrude");
                model.geom(id).feature(mw.get("Make Recess Pre Cuts 1")).label("Make Recess Pre Cuts 1");
                model.geom(id).feature(mw.get("Make Recess Pre Cuts 1")).set("contributeto", mw.get("RECESS PRE CUTS"));
                model.geom(id).feature(mw.get("Make Recess Pre Cuts 1")).setIndex("distance", "2*r_cuff_in_Pitt", 0);
                model.geom(id).feature(mw.get("Make Recess Pre Cuts 1")).selection("input").named(mw.get("RECESS CROSS SECTION"));

                model.geom(id).create(mw.next("cyl", "Inner Recess Cutter"), "Cylinder");
                model.geom(id).feature(mw.get("Inner Recess Cutter")).label("Inner Recess Cutter");
                model.geom(id).feature(mw.get("Inner Recess Cutter")).set("contributeto", mw.get("INNER RECESS CUTTER"));
                model.geom(id).feature(mw.get("Inner Recess Cutter")).set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                model.geom(id).feature(mw.get("Inner Recess Cutter")).set("r", "r_cuff_in_Pitt");
                model.geom(id).feature(mw.get("Inner Recess Cutter")).set("h", "L_cuff_Pitt");

                model.geom(id).create(mw.next("cyl","Outer Recess Cutter"), "Cylinder");
                model.geom(id).feature(mw.get("Outer Recess Cutter")).label("Outer Recess Cutter");
                model.geom(id).feature(mw.get("Outer Recess Cutter")).set("contributeto", mw.get("OUTER RECESS CUTTER"));
                model.geom(id).feature(mw.get("Outer Recess Cutter")).set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                model.geom(id).feature(mw.get("Outer Recess Cutter")).set("r", "r_inner_contact");
                model.geom(id).feature(mw.get("Outer Recess Cutter")).set("h", "L_cuff_Pitt");

                model.geom(id).create(mw.next("par","Remove Outer Recess Excess"), "Partition");
                model.geom(id).feature(mw.get("Remove Outer Recess Excess")).label("Remove Outer Recess Excess");
                model.geom(id).feature(mw.get("Remove Outer Recess Excess")).set("contributeto", mw.get("FINAL RECESS"));
                model.geom(id).feature(mw.get("Remove Outer Recess Excess")).selection("input").named(mw.get("RECESS PRE CUTS"));
                model.geom(id).feature(mw.get("Remove Outer Recess Excess")).selection("tool").named(mw.get("OUTER RECESS CUTTER"));

                model.geom(id).create(mw.next("par","Remove Inner Recess Excess"), "Partition");
                model.geom(id).feature(mw.get("Remove Inner Recess Excess")).label("Remove Inner Recess Excess");
                model.geom(id).feature(mw.get("Remove Inner Recess Excess")).set("contributeto", mw.get("FINAL RECESS"));
                model.geom(id).feature(mw.get("Remove Inner Recess Excess")).selection("input").named(mw.get("RECESS PRE CUTS"));
                model.geom(id).feature(mw.get("Remove Inner Recess Excess")).selection("tool").named(mw.get("INNER RECESS CUTTER"));

                model.geom(id).create(mw.next("ballsel","sel inner excess 1"), "BallSelection");
                model.geom(id).feature(mw.get("sel inner excess 1")).label("sel inner excess 1");
                model.geom(id).feature(mw.get("sel inner excess 1")).set("posx", "((r_inner_contact+recess_Pitt)/2)*cos(rotation_angle)");
                model.geom(id).feature(mw.get("sel inner excess 1")).set("posy", "((r_inner_contact+recess_Pitt)/2)*sin(rotation_angle)");
                model.geom(id).feature(mw.get("sel inner excess 1")).set("posz", "z_center");
                model.geom(id).feature(mw.get("sel inner excess 1")).set("r", 1);
                model.geom(id).feature(mw.get("sel inner excess 1")).set("contributeto", mw.get("SEL INNER EXCESS RECESS"));

                model.geom(id).create(mw.next("ballsel","sel outer excess 1"), "BallSelection");
                model.geom(id).feature(mw.get("sel outer excess 1")).label("sel outer excess 1");
                model.geom(id).feature(mw.get("sel outer excess 1")).set("posx", "((r_cuff_in_Pitt+2*r_cuff_in_Pitt)/2)*cos(rotation_angle)");
                model.geom(id).feature(mw.get("sel outer excess 1")).set("posy", "((r_cuff_in_Pitt+2*r_cuff_in_Pitt)/2)*sin(rotation_angle)");
                model.geom(id).feature(mw.get("sel outer excess 1")).set("posz", "z_center");
                model.geom(id).feature(mw.get("sel outer excess 1")).set("r", 1);
                model.geom(id).feature(mw.get("sel outer excess 1")).set("contributeto", mw.get("SEL OUTER EXCESS RECESS"));

                model.geom(id).create(mw.next("del","Delete Inner Excess Recess"), "Delete");
                model.geom(id).feature(mw.get("Delete Inner Excess Recess")).label("Delete Inner Excess Recess");
                model.geom(id).feature(mw.get("Delete Inner Excess Recess")).selection("input").init(3);
                model.geom(id).feature(mw.get("Delete Inner Excess Recess")).selection("input").named(mw.get("SEL INNER EXCESS RECESS"));

                model.geom(id).create(mw.next("del","Delete Outer Excess Recess"), "Delete");
                model.geom(id).feature(mw.get("Delete Outer Excess Recess")).label("Delete Outer Excess Recess");
                model.geom(id).feature(mw.get("Delete Outer Excess Recess")).selection("input").init(3);
                model.geom(id).feature(mw.get("Delete Outer Excess Recess")).selection("input").named(mw.get("SEL OUTER EXCESS RECESS"));

                model.geom(id).create(mw.next("endif"), "EndIf");

                model.geom(id).create(mw.next("pt","src"), "Point");
                model.geom(id).feature(mw.get("src")).label("src");
                model.geom(id).feature(mw.get("src")).set("contributeto", mw.get("SRC"));
                model.geom(id).feature(mw.get("src"))
                        .set("p", new String[]{"(r_cuff_in_Pitt+recess_Pitt+(thk_contact_Pitt/2))*cos(rotation_angle)", "(r_cuff_in_Pitt+recess_Pitt+(thk_contact_Pitt/2))*sin(rotation_angle)", "z_center"});
                model.geom(id).run();
                break;
            default:
                throw new  IllegalArgumentException("No implementation for part primitive name: " + pseudonym);
        }

        // if im was not edited for some reason, return null
        if (im.count() == 0) return null;
        return im;
    }

    /**
     *
     * @param id
     * @param pseudonym
     * @param mw
     * @return
     */
    public static boolean createPartInstance(String id, String pseudonym, ModelWrapper2 mw) throws IllegalArgumentException {
        return createPartInstance(id, pseudonym, mw, null);
    }

    /**
     *
     * @param id
     * @param pseudonym
     * @param mw
     * @param data
     * @return
     */
    public static boolean createPartInstance(String id, String pseudonym, ModelWrapper2 mw, HashMap<String, Object> data) throws IllegalArgumentException {

        Model model = mw.getModel();
        model.component().create("comp1", true);
        model.component("comp1").geom().create("geom1", 3);
        model.component("comp1").mesh().create("mesh1");

        // EXAMPLE
        String nextCsel = mw.next("csel", "mySuperCoolCsel");

        // you can either refer to it with that variable, nextCsel
        model.geom(id).selection().create(nextCsel, "CumulativeSelection");

        // or retrieve it later (likely in another method where the first variable isn't easily accessible
        model.geom(id).selection(mw.get("mySuperCoolCsel")).label("INNER CUFF SURFACE");



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
            default:
                throw new IllegalArgumentException("No implementation for part instance name: " + pseudonym);
        }

        return true;
    }
}

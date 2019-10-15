package model;

import com.comsol.model.GeomFeature;
import com.comsol.model.Model;
import com.comsol.model.ModelParam;

import java.io.IOException;
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

    public static boolean createPartInstance(String id, String pseudonym, ModelWrapper2 mw, HashMap<String, String> partPrimitives) {
        return createPartInstance(id, pseudonym, mw, partPrimitives, null);
    }

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
                outer_surf.set("contributeto", im.get("OUTER CUFF SURFACE"));
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

                String cs1Label = "Cumulative Selection 1";
                wp_recess_cx1.geom().selection().create(im.next("csel", cs1Label), "CumulativeSelection");
                wp_recess_cx1.geom().selection(im.get(cs1Label)).label(cs1Label);

                String rcxLabel = "wp RECESS CROSS SECTION";
                wp_recess_cx1.geom().selection().create(im.next("csel",rcxLabel), "CumulativeSelection");
                wp_recess_cx1.geom().selection(im.get(rcxLabel)).label(rcxLabel);

                wp_recess_cx1.geom().create("r1", "Rectangle");
                wp_recess_cx1.geom().feature("r1").label("Recess Cross Section");
                wp_recess_cx1.geom().feature("r1").set("contributeto", im.get(rcxLabel));
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

                String contactxsLabel = "Contact Cross Section";
                GeomFeature contact_xs = model.geom(id).create(im.next("wp",contactxsLabel), "WorkPlane");
                contact_xs.set("contributeto", im.get("CONTACT CROSS SECTION"));
                contact_xs.label(contactxsLabel);
                contact_xs.set("quickplane", "zx");
                contact_xs.set("unite", true);
                contact_xs.geom().selection().create(im.get("CONTACT CROSS SECTION"), "CumulativeSelection");
                contact_xs.geom().selection(im.get("CONTACT CROSS SECTION")).label("CONTACT CROSS SECTION");
                contact_xs.geom().create("c1", "Circle");
                contact_xs.geom().feature("c1").label("Contact Cross Section");
                contact_xs.geom().feature("c1").set("contributeto", im.get("CONTACT CROSS SECTION"));
                contact_xs.geom().feature("c1").set("pos", new String[]{"Center", "R_in-R_conductor-Sep_conductor"});
                contact_xs.geom().feature("c1").set("r", "R_conductor");

                String mcLabel = "Make Contact";
                GeomFeature contact = model.geom(id).create(im.next("rev",mcLabel), "Revolve");
                contact.label(mcLabel);
                contact.set("contributeto", im.get("CONTACT FINAL"));
                contact.set("angle2", "Theta_conductor");
                contact.set("axis", new int[]{1, 0});
                contact.selection("input").named(im.get("CONTACT CROSS SECTION"));

                String sourceLabel = "Src";
                GeomFeature source = model.geom(id).create(im.next("pt",sourceLabel), "Point");
                source.label(sourceLabel);
                source.set("contributeto", im.get("SRC"));
                source.set("p", new String[]{"(R_in-R_conductor-Sep_conductor)*cos(Theta_conductor/2)", "(R_in-R_conductor-Sep_conductor)*sin(Theta_conductor/2)", "Center"});
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
                        "RECESS CUTTER OUT",
                        "BASE PLANE (PRE ROTATION)"
                };
                for (String cselCCLabel: cselCCLabels) {
                    model.geom(id).selection().create(im.next("csel", cselCCLabel), "CumulativeSelection")
                            .label(cselCCLabel);
                }

                String bpprLabel = "Base Plane (Pre Rrotation)";
                GeomFeature baseplane_prerot = model.geom(id).create(im.next("wp", bpprLabel), "WorkPlane");
                baseplane_prerot.label(bpprLabel);
                baseplane_prerot.set("contributeto", im.get("BASE PLANE (PRE ROTATION)"));
                baseplane_prerot.set("quickplane", "yz");
                baseplane_prerot.set("unite", true);

                String ifrecessCCLabel = "If Recess";
                GeomFeature ifrecessCC = model.geom(id).create(im.next("if",ifrecessCCLabel), "If");
                ifrecessCC.label(ifrecessCCLabel);
                ifrecessCC.set("condition", "Recess>0");

                String rprLabel = "Rotated Plane for Recess";
                GeomFeature rpr = model.geom(id).create(im.next("wp",rprLabel), "WorkPlane");
                rpr.label(rprLabel);
                rpr.set("contributeto", im.get("PLANE FOR RECESS"));
                rpr.set("planetype", "transformed");
                rpr.set("workplane", im.get(bpprLabel));
                rpr.set("transaxis", new int[]{0, 1, 0});
                rpr.set("transrot", "Rotation_angle");
                rpr.set("unite", true);

                String cosLabel = "CONTACT OUTLINE SHAPE";
                rpr.geom().selection().create(im.next("csel",cosLabel), "CumulativeSelection");
                rpr.geom().selection(im.get(cosLabel)).label(cosLabel);

                String ifcsicLabel = "If Contact Surface is Circle (for recess)";
                GeomFeature ifcsic = rpr.geom().create(im.next("if",ifcsicLabel), "If");
                ifcsic.label("If Contact Surface is Circle");
                ifcsic.set("condition", "Round_def==1");

                String coLabel = "Contact Outline";
                GeomFeature co = rpr.geom().create(im.next("e",coLabel), "Ellipse");
                co.label("Contact Outline");
                co.set("contributeto", im.get("CONTACT OUTLINE SHAPE"));
                co.set("pos", new String[]{"0", "Center"});
                co.set("semiaxes", new String[]{"A_ellipse_contact", "Diam_contact/2"});

                String elifcocLabel = "Else If Contact Outline is Circle";
                GeomFeature elifcoc = rpr.geom().create(im.next("elseif",elifcocLabel), "ElseIf");
                elifcoc.label("Else If Contact Outline is Circle");
                elifcoc.set("condition", "Round_def==2");

                String co1Label = "Contact Outline 1";
                GeomFeature co1 = rpr.geom().create(im.next("e",co1Label), "Ellipse");
                co1.label(co1Label);
                co1.set("contributeto", im.get("CONTACT OUTLINE SHAPE"));
                co1.set("pos", new String[]{"0", "Center"});
                co1.set("semiaxes", new String[]{"Diam_contact/2", "Diam_contact/2"});
                rpr.geom().create(im.next("endif"), "EndIf");

                String mpcrdLabel = "Make Pre Cut Recess Domains";
                GeomFeature mpcrd = model.geom(id).create(im.next("ext",mpcrdLabel), "Extrude");
                mpcrd.label(mpcrdLabel);
                mpcrd.set("contributeto", im.get("PRE CUT RECESS"));
                mpcrd.setIndex("distance", "R_in+Recess+Overshoot", 0);
                mpcrd.selection("input").named(im.get("PLANE FOR RECESS"));

                String rciLabel = "Recess Cut In";
                GeomFeature rci = model.geom(id).create(im.next("cyl",rciLabel), "Cylinder");
                rci.label(rciLabel);
                rci.set("contributeto", im.get("RECESS CUTTER IN"));
                rci.set("pos", new String[]{"0", "0", "Center-L/2"});
                rci.set("r", "R_in");
                rci.set("h", "L");

                String rcoLabel = "Recess Cut Out";
                GeomFeature rco = model.geom(id).create(im.next("cyl",rcoLabel), "Cylinder");
                rco.label(rcoLabel);
                rco.set("contributeto", im.get("RECESS CUTTER OUT"));
                rco.set("pos", new String[]{"0", "0", "Center-L/2"});
                rco.set("r", "R_in+Recess");
                rco.set("h", "L");

                String erciLabel = "Execute Recess Cut In";
                GeomFeature erci = model.geom(id).create(im.next("dif",erciLabel), "Difference");
                erci.label(erciLabel);
                erci.set("contributeto", im.get("RECESS FINAL"));
                erci.selection("input").named(im.get("PRE CUT RECESS"));
                erci.selection("input2").named(im.get("RECESS CUTTER IN"));

                String pordLabel = "Partition Outer Recess Domain";
                GeomFeature pord = model.geom(id).create(im.next("pard", pordLabel), "PartitionDomains");
                pord.label(pordLabel);
                pord.set("contributeto", im.get("RECESS FINAL"));
                pord.set("partitionwith", "objects");
                pord.set("keepobject", false);
                pord.selection("domain").named(im.get("PRE CUT RECESS"));
                pord.selection("object").named(im.get("RECESS CUTTER OUT"));

                String soLabel = "Select Overshoot";
                GeomFeature so = model.geom(id).create(im.next("ballsel",soLabel), "BallSelection");
                so.label(soLabel);
                so.set("posx", "(R_in+Recess+Overshoot/2)*cos(Rotation_angle)");
                so.set("posy", "(R_in+Recess+Overshoot/2)*sin(Rotation_angle)");
                so.set("posz", "Center");
                so.set("r", 1);
                so.set("contributeto", im.get("RECESS OVERSHOOT"));

                String droLabel = "Delete Recess Overshoot";
                GeomFeature dro = model.geom(id).create(im.next("del",droLabel), "Delete");
                dro.label(droLabel);
                dro.selection("input").init(3);
                dro.selection("input").named(im.get("RECESS OVERSHOOT"));

                String endifrecessLabel = "EndIf";
                model.geom(id).create(im.next("endif"), endifrecessLabel);

                String rpcLabel = "Rotated Plane for Contact";
                GeomFeature rpc = model.geom(id).create(im.next("wp",rpcLabel), "WorkPlane");
                rpc.label(rpcLabel);
                rpc.set("contributeto", im.get("PLANE FOR CONTACT"));
                rpc.set("planetype", "transformed");
                rpc.set("workplane", im.get("Base Plane (Pre Rrotation)"));
                rpc.set("transaxis", new int[]{0, 1, 0});
                rpc.set("transrot", "Rotation_angle");
                rpc.set("unite", true);

                String coscLabel = "wp CONTACT OUTLINE SHAPE";
                rpc.geom().selection().create(im.next("csel",coscLabel), "CumulativeSelection");
                rpc.geom().selection(im.get(coscLabel)).label(coscLabel);

                String ifcsiccLabel = "If Contact Surface is Circle (for contact)";
                GeomFeature icsicc = rpc.geom().create(im.next("if",ifcsiccLabel), "If");
                icsicc.label(ifcsiccLabel);
                icsicc.set("condition", "Round_def==1");

                String cocLabel = "Contact Outline circle";
                GeomFeature coc = rpc.geom().create(im.next("e",cocLabel), "Ellipse");
                coc.label(cocLabel);
                coc.set("contributeto", im.get(coscLabel));
                coc.set("pos", new String[]{"0", "Center"});
                coc.set("semiaxes", new String[]{"A_ellipse_contact", "Diam_contact/2"}); //

                String elifcoccLabel = "wp Else If Contact Outline is Circle";
                GeomFeature elifcocc = rpc.geom().create(im.next("elseif",elifcoccLabel), "ElseIf");
                elifcoc.label(elifcoccLabel);
                elifcocc.set("condition", "Round_def==2");

                String co1cLabel = "wp Contact Outline 1";
                GeomFeature co1c = rpc.geom().create(im.next("e",co1cLabel), "Ellipse");
                co1c.label(co1cLabel);
                co1c.set("contributeto", im.get(coscLabel));
                co1c.set("pos", new String[]{"0", "Center"});
                co1c.set("semiaxes", new String[]{"Diam_contact/2", "Diam_contact/2"});
                rpc.geom().create(im.next("endif"), "EndIf");

                String mpccdLabel = "Make Pre Cut Contact Domains";
                GeomFeature mpccd = model.geom(id).create(im.next("ext",mpccdLabel), "Extrude");
                mpccd.label(mpccdLabel);
                mpccd.set("contributeto", im.get("PRE CUT CONTACT"));
                mpccd.setIndex("distance", "R_in+Recess+Contact_depth+Overshoot", 0);
                mpccd.selection("input").named(im.get("PLANE FOR CONTACT"));

                String cciLabel = "Contact Cut In";
                GeomFeature cci = model.geom(id).create(im.next("cyl",cciLabel), "Cylinder");
                cci.label(cciLabel);
                cci.set("contributeto", im.get("CONTACT CUTTER IN"));
                cci.set("pos", new String[]{"0", "0", "Center-L/2"});
                cci.set("r", "R_in+Recess");
                cci.set("h", "L");

                String ccoLabel = "Contact Cut Out";
                GeomFeature cco = model.geom(id).create(im.next("cyl",ccoLabel), "Cylinder");
                cco.label(ccoLabel);
                cco.set("contributeto", im.get("CONTACT CUTTER OUT"));
                cco.set("pos", new String[]{"0", "0", "Center-L/2"});
                cco.set("r", "R_in+Recess+Contact_depth");
                cco.set("h", "L");

                String ecciLabel = "Execute Contact Cut In";
                GeomFeature ecci = model.geom(id).create(im.next("dif",ecciLabel), "Difference");
                ecci.label(ecciLabel);
                ecci.set("contributeto", im.get("CONTACT FINAL"));
                ecci.selection("input").named(im.get("PRE CUT CONTACT"));
                ecci.selection("input2").named(im.get("CONTACT CUTTER IN"));

                String pocdLabel = "Partition Outer Contact Domain";
                GeomFeature pocd = model.geom(id).create(im.next("pard",pocdLabel), "PartitionDomains");
                pocd.label(pocdLabel);
                pocd.set("contributeto", im.get("CONTACT FINAL"));
                pocd.set("partitionwith", "objects");
                pocd.set("keepobject", false);
                pocd.selection("domain").named(im.get("PRE CUT CONTACT"));
                pocd.selection("object").named(im.get("CONTACT CUTTER OUT"));

                String so1Label = "Select Overshoot 1";
                GeomFeature so1 = model.geom(id).create(im.next("ballsel", so1Label), "BallSelection");
                so1.label(so1Label);
                so1.set("posx", "(R_in+Recess+Contact_depth+Overshoot/2)*cos(Rotation_angle)");
                so1.set("posy", "(R_in+Recess+Contact_depth+Overshoot/2)*sin(Rotation_angle)");
                so1.set("posz", "Center");
                so1.set("r", 1);
                so1.set("contributeto", im.get("RECESS OVERSHOOT"));

                String dro1Label = "Delete Recess Overshoot 1";
                GeomFeature dro1 = model.geom(id).create(im.next("del",dro1Label), "Delete");
                dro1.label(dro1Label);
                dro1.selection("input").init(3);
                dro1.selection("input").named(im.get("RECESS OVERSHOOT"));

                String srccLabel = "Src";
                GeomFeature srcc = model.geom(id).create(im.next("pt",srccLabel), "Point");
                srcc.label(srccLabel);
                srcc.set("contributeto", im.get("SRC"));
                srcc.set("p", new String[]{"(R_in+Recess+Contact_depth/2)*cos(Rotation_angle)", "(R_in+Recess+Contact_depth/2)*sin(Rotation_angle)", "Center"});

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

                String hicsp1Label = "Helical Insulator Cross Section Part 1";
                GeomFeature hicsp1 = model.geom(id).create(im.next("wp",hicsp1Label), "WorkPlane");
                hicsp1.label(hicsp1Label);
                hicsp1.set("quickplane", "xz");
                hicsp1.set("unite", true);

                String hicsLabel = "HELICAL INSULATOR CROSS SECTION";
                hicsp1.geom().selection().create(im.next("csel",hicsLabel), "CumulativeSelection");
                hicsp1.geom().selection(im.get(hicsLabel)).label(hicsLabel);

                String hicxp1Label = "HELICAL INSULATOR CROSS SECTION P1";
                hicsp1.geom().selection().create(im.next("csel",hicxp1Label), "CumulativeSelection");
                hicsp1.geom().selection(im.get(hicxp1Label)).label(hicxp1Label);
                hicsp1.geom().create("r1", "Rectangle");
                hicsp1.geom().feature("r1").label("Helical Insulator Cross Section Part 1");
                hicsp1.geom().feature("r1").set("contributeto", im.get(hicxp1Label));
                hicsp1.geom().feature("r1").set("pos", new String[]{"r_cuff_in_LN+(thk_cuff_LN/2)", "Center-(L_cuff_LN/2)"});
                hicsp1.geom().feature("r1").set("base", "center");
                hicsp1.geom().feature("r1").set("size", new String[]{"thk_cuff_LN", "w_cuff_LN"});

                String pcp1Label = "Parametric Curve Part 1";
                GeomFeature pcp1 = model.geom(id).create(im.next("pc",pcp1Label), "ParametricCurve");
                pcp1.label(pcp1Label);
                pcp1.set("contributeto", im.get("PC1"));
                pcp1.set("parmax", "rev_cuff_LN*(0.75/2.5)");
                pcp1.set("coord", new String[]{"cos(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "sin(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "Center+(L_cuff_LN)*(s/rev_cuff_LN)-(L_cuff_LN/2)"});

                String mcp1Label = "Make Cuff Part 1";
                GeomFeature mcp1 = model.geom(id).create(im.next("swe",mcp1Label), "Sweep");
                mcp1.label("Make Cuff Part 1");
                mcp1.set("contributeto", im.get("Cuffp1"));
                mcp1.set("crossfaces", true);
                mcp1.set("keep", false);
                mcp1.set("includefinal", false);
                mcp1.set("twistcomp", false);
                mcp1.selection("face").named(im.get(hicsp1Label) + "_" + im.get(hicxp1Label));
                mcp1.selection("edge").named(im.get("PC1"));
                mcp1.selection("diredge").set(im.get(pcp1Label) + "(1)", 1); //TODO

                String sefp1Label = "Select End Face Part 1";
                GeomFeature sefp1 = model.geom(id).create(im.next("ballsel", sefp1Label), "BallSelection");
                sefp1.set("entitydim", 2);
                sefp1.label(sefp1Label);
                sefp1.set("posx", "cos(2*pi*rev_cuff_LN*((0.75)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                sefp1.set("posy", "sin(2*pi*rev_cuff_LN*((0.75)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                sefp1.set("posz", "Center+(L_cuff_LN)*(rev_cuff_LN*((0.75)/2.5)/rev_cuff_LN)-(L_cuff_LN/2)");
                sefp1.set("r", 1);
                sefp1.set("contributeto", im.get("SEL END P1"));

                String hicsp2Label = "Helical Insulator Cross Section Part 2";
                GeomFeature hicsp2 = model.geom(id).create(im.next("wp","Helical Insulator Cross Section Part 2"), "WorkPlane");
                hicsp2.label(hicsp2Label);
                hicsp2.set("planetype", "faceparallel");
                hicsp2.set("unite", true);
                hicsp2.selection("face").named(im.get("SEL END P1"));

                String hicsp2wpLabel =  "HELICAL INSULATOR CROSS SECTION P2";
                hicsp2.geom().selection().create(im.next("csel",hicsp2wpLabel), "CumulativeSelection");
                hicsp2.geom().selection(im.get(hicsp2wpLabel)).label(hicsp2wpLabel);

                String hccsp2wpLabel = "HELICAL CONDUCTOR CROSS SECTION P2";
                hicsp2.geom().selection().create(im.next("csel",hccsp2wpLabel), "CumulativeSelection");
                hicsp2.geom().selection(im.get(hccsp2wpLabel)).label(hccsp2wpLabel);

                hicsp2.geom().create("r1", "Rectangle");
                hicsp2.geom().feature("r1").label("Helical Insulator Cross Section Part 2");
                hicsp2.geom().feature("r1").set("contributeto", im.get(hicsp2wpLabel));
                hicsp2.geom().feature("r1").set("base", "center");
                hicsp2.geom().feature("r1").set("size", new String[]{"thk_cuff_LN", "w_cuff_LN"});

                String hccsp2Label = "Helical Conductor Cross Section Part 2";
                GeomFeature hccsp2 = model.geom(id).create(im.next("wp",hccsp2Label), "WorkPlane");
                hccsp2.label(hccsp2Label);
                hccsp2.set("planetype", "faceparallel");
                hccsp2.set("unite", true);
                hccsp2.selection("face").named(im.get("SEL END P1"));

                String hicxp2Label = "wp HELICAL INSULATOR CROSS SECTION P2";
                hccsp2.geom().selection().create(im.next("csel",hicxp2Label), "CumulativeSelection");
                hccsp2.geom().selection(im.get(hicxp2Label)).label(hicxp2Label);

                String hccxp2Label = "wp HELICAL CONDUCTOR CROSS SECTION P2";
                hccsp2.geom().selection().create(im.next("csel",hccxp2Label), "CumulativeSelection");
                hccsp2.geom().selection(im.get(hccxp2Label)).label(hccxp2Label);
                hccsp2.geom().create("r2", "Rectangle");
                hccsp2.geom().feature("r2").label("Helical Conductor Cross Section Part 2");
                hccsp2.geom().feature("r2").set("contributeto", im.get(hccxp2Label));
                hccsp2.geom().feature("r2").set("pos", new String[]{"(thk_elec_LN-thk_cuff_LN)/2", "0"});
                hccsp2.geom().feature("r2").set("base", "center");
                hccsp2.geom().feature("r2").set("size", new String[]{"thk_elec_LN", "w_elec_LN"});

                String pcp2Label = "Parametric Curve Part 2";
                GeomFeature pcp2 = model.geom(id).create(im.next("pc",pcp2Label), "ParametricCurve");
                pcp2.label(pcp2Label);
                pcp2.set("contributeto", im.get("PC2"));
                pcp2.set("parmin", "rev_cuff_LN*(0.75/2.5)");
                pcp2.set("parmax", "rev_cuff_LN*((0.75+1)/2.5)");
                pcp2.set("coord", new String[]{"cos(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "sin(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "Center+(L_cuff_LN)*(s/rev_cuff_LN)-(L_cuff_LN/2)"});

                String mcp2Label = "Make Cuff Part 2";
                GeomFeature mcp2 = model.geom(id).create(im.next("swe",mcp2Label), "Sweep");
                mcp2.label("Make Cuff Part 2");
                mcp2.set("contributeto", im.get("Cuffp2"));
                mcp2.set("crossfaces", true);
                mcp2.set("includefinal", false);
                mcp2.set("twistcomp", false);
                mcp2.selection("face").named(im.get(hicsp2Label) + "_" + im.get(hicsp2wpLabel));
                mcp2.selection("edge").named(im.get("PC2"));
                mcp2.selection("diredge").set(im.get(pcp2Label) + "(1)", 1);

                String mcp2cLabel = "Make Conductor Part 2";
                GeomFeature mcp2c = model.geom(id).create(im.next("swe",mcp2cLabel), "Sweep");
                mcp2c.label(mcp2cLabel);
                mcp2c.set("contributeto", im.get("Conductorp2"));
                mcp2c.set("crossfaces", true);
                mcp2c.set("keep", false);
                mcp2c.set("includefinal", false);
                mcp2c.set("twistcomp", false);
                mcp2c.selection("face").named(im.get(hccsp2Label) + "_" + im.get(hccxp2Label));
                mcp2c.selection("edge").named(im.get("PC2"));
                mcp2c.selection("diredge").set(im.get(pcp2Label) + "(1)", 1);

                String sefp2Label = "Select End Face Part 2";
                GeomFeature sefp2 = model.geom(id).create(im.next("ballsel",sefp2Label), "BallSelection");
                sefp2.set("entitydim", 2);
                sefp2.label(sefp2Label);
                sefp2.set("posx", "cos(2*pi*rev_cuff_LN*((0.75+1)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                sefp2.set("posy", "sin(2*pi*rev_cuff_LN*((0.75+1)/2.5))*((thk_cuff_LN/2)+r_cuff_in_LN)");
                sefp2.set("posz", "Center+(L_cuff_LN)*(rev_cuff_LN*((0.75+1)/2.5)/rev_cuff_LN)-(L_cuff_LN/2)");
                sefp2.set("r", 1);
                sefp2.set("contributeto", im.get("SEL END P2"));

                String hicsp3Label = "Helical Insulator Cross Section Part 3";
                GeomFeature hicsp3 = model.geom(id).create(im.next("wp",hicsp3Label), "WorkPlane");
                hicsp3.label(hicsp3Label);
                hicsp3.set("planetype", "faceparallel");
                hicsp3.set("unite", true);
                hicsp3.selection("face").named(im.get("SEL END P2")); // here

                String hicssp3Label = "HELICAL INSULATOR CROSS SECTION P3";
                hicsp3.geom().selection().create(im.next("csel", hicssp3Label), "CumulativeSelection");
                hicsp3.geom().selection(im.get(hicssp3Label)).label(hicssp3Label);
                hicsp3.geom().create("r1", "Rectangle");
                hicsp3.geom().feature("r1").label("Helical Insulator Cross Section Part 3");
                hicsp3.geom().feature("r1").set("contributeto", im.get(hicssp3Label));
                hicsp3.geom().feature("r1").set("base", "center");
                hicsp3.geom().feature("r1").set("size", new String[]{"thk_cuff_LN", "w_cuff_LN"});

                String pcp3Label = "Parametric Curve Part 3";
                GeomFeature pcp3 = model.geom(id).create(im.next("pc",pcp3Label), "ParametricCurve");
                pcp3.label(pcp3Label);
                pcp3.set("contributeto", im.get("PC3"));
                pcp3.set("parmin", "rev_cuff_LN*((0.75+1)/2.5)");
                pcp3.set("parmax", "rev_cuff_LN");
                pcp3.set("coord", new String[]{"cos(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "sin(2*pi*s)*((thk_cuff_LN/2)+r_cuff_in_LN)", "Center+(L_cuff_LN)*(s/rev_cuff_LN)-(L_cuff_LN/2)"});

                String mcp3Label = "Make Cuff Part 3";
                GeomFeature mcp3 = model.geom(id).create(im.next("swe",mcp3Label), "Sweep");
                mcp3.label(mcp3Label);
                mcp3.set("contributeto", im.get("Cuffp3"));
                mcp3.selection("face").named(im.get(hicsp3Label) + "_" + im.get(hicssp3Label));
                mcp3.selection("edge").named(im.get("PC3"));
                mcp3.set("keep", false);
                mcp3.set("twistcomp", false);

                String srchLabel = "ptSRC";
                GeomFeature srch = model.geom(id).create(im.next("pt",srchLabel), "Point");
                srch.label(srchLabel);
                srch.set("contributeto", im.get("SRC"));
                srch.set("p", new String[]{"cos(2*pi*rev_cuff_LN*(1.25/2.5))*((thk_elec_LN/2)+r_cuff_in_LN)", "sin(2*pi*rev_cuff_LN*(1.25/2.5))*((thk_elec_LN/2)+r_cuff_in_LN)", "Center"});

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

                String bpprsLabel = "base plane (pre rotation)";
                GeomFeature bpprs = model.geom(id).create(im.next("wp",bpprsLabel), "WorkPlane");
                bpprs.label(bpprsLabel);
                bpprs.set("contributeto", im.get("BASE CONTACT PLANE (PRE ROTATION)"));
                bpprs.set("quickplane", "yz");
                bpprs.set("unite", true);

                String ccscLabel = "Contact Cross Section";
                GeomFeature ccsc = model.geom(id).create(im.next("wp",ccscLabel), "WorkPlane");
                ccsc.label(ccscLabel);
                ccsc.set("contributeto", im.get("CONTACT CROSS SECTION"));
                ccsc.set("planetype", "transformed");
                ccsc.set("workplane", im.get(bpprsLabel));
                ccsc.set("transaxis", new int[]{0, 1, 0});
                ccsc.set("transrot", "rotation_angle");
                ccsc.set("unite", true);

                String cpfLabel = "CONTACT PRE FILLET";
                ccsc.geom().selection().create(im.next("csel", cpfLabel), "CumulativeSelection");
                ccsc.geom().selection(im.get(cpfLabel)).label(cpfLabel);

                String cfLabel = "CONTACT FILLETED";
                ccsc.geom().selection().create(im.next("csel",cfLabel), "CumulativeSelection");
                ccsc.geom().selection(im.get(cfLabel)).label(cfLabel);
                ccsc.geom().create("r1", "Rectangle");
                ccsc.geom().feature("r1").label("Contact Pre Fillet Corners");
                ccsc.geom().feature("r1").set("contributeto", im.get(cpfLabel));
                ccsc.geom().feature("r1").set("pos", new int[]{0, 0});
                ccsc.geom().feature("r1").set("base", "center");
                ccsc.geom().feature("r1").set("size", new String[]{"w_contact_Pitt", "z_contact_Pitt"});

                String filletLabel = "Fillet Corners";
                GeomFeature fillet = ccsc.geom().create(im.next("fil",filletLabel), "Fillet");
                fillet.label(filletLabel);
                fillet.set("contributeto", im.get(cfLabel));
                fillet.set("radius", "fillet_contact_Pitt");
                fillet.selection("point").named(im.get(cpfLabel));
                String scaleLabel = "scLabel";
                GeomFeature scale = ccsc.geom().create(im.next("sca",scaleLabel), "Scale");
                scale.label(scaleLabel);
                scale.set("type", "anisotropic");
                scale.set("factor", new String[]{"1", "scale_morph_w_contact_Pitt"});
                scale.selection("input").named(im.get(cfLabel));

                ccsc.geom().create("mov1", "Move");
                ccsc.geom().feature("mov1").set("disply", "z_center");
                ccsc.geom().feature("mov1").selection("input").named(im.get(cfLabel));

                String mcpcLabel = "Make Contact Pre Cuts";
                GeomFeature mcpc = model.geom(id).create(im.next("ext",mcpcLabel), "Extrude");
                mcpc.label("Make Contact Pre Cuts");
                mcpc.set("contributeto", im.get("CONTACT PRE CUTS"));
                mcpc.setIndex("distance", "2*r_cuff_in_Pitt", 0);
                mcpc.selection("input").named(im.get("CONTACT CROSS SECTION"));

                String iccLabel = "Inner Contact Cutter";
                GeomFeature icc = model.geom(id).create(im.next("cyl",iccLabel), "Cylinder");
                icc.label(iccLabel);
                icc.set("contributeto", im.get("INNER CONTACT CUTTER"));
                icc.set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                icc.set("r", "r_inner_contact");
                icc.set("h", "L_cuff_Pitt");

                String occLabel = "Outer Contact Cutter";
                GeomFeature occ = model.geom(id).create(im.next("cyl",occLabel), "Cylinder");
                occ.label(occLabel);
                occ.set("contributeto", im.get("OUTER CONTACT CUTTER"));
                occ.set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                occ.set("r", "r_outer_contact");
                occ.set("h", "L_cuff_Pitt");

                String coeLabel = "Cut Outer Excess";
                GeomFeature coe = model.geom(id).create(im.next("par",coeLabel), "Partition");
                coe.label(coeLabel);
                coe.set("contributeto", im.get("FINAL CONTACT"));
                coe.selection("input").named(im.get("CONTACT PRE CUTS"));
                coe.selection("tool").named(im.get("OUTER CONTACT CUTTER"));

                String cieLabel = "Cut Inner Excess";
                GeomFeature cie = model.geom(id).create(im.next("par",cieLabel), "Partition");
                cie.label(cieLabel);
                cie.set("contributeto", im.get("FINAL CONTACT"));
                cie.selection("input").named(im.get("CONTACT PRE CUTS"));
                cie.selection("tool").named(im.get("INNER CONTACT CUTTER"));

                String sieLabel = "sel inner excess";
                GeomFeature sie = model.geom(id).create(im.next("ballsel",sieLabel), "BallSelection");
                sie.label(sieLabel);
                sie.set("posx", "(r_inner_contact/2)*cos(rotation_angle)");
                sie.set("posy", "(r_inner_contact/2)*sin(rotation_angle)");
                sie.set("posz", "z_center");
                sie.set("r", 1);
                sie.set("contributeto", im.get("SEL INNER EXCESS CONTACT"));

                String soeLabel = "sel outer excess";
                GeomFeature soe = model.geom(id).create(im.next("ballsel",soeLabel), "BallSelection");
                soe.label(soeLabel);
                soe.set("posx", "((r_outer_contact+2*r_cuff_in_Pitt)/2)*cos(rotation_angle)");
                soe.set("posy", "((r_outer_contact+2*r_cuff_in_Pitt)/2)*sin(rotation_angle)");
                soe.set("posz", "z_center");
                soe.set("r", 1);
                soe.set("contributeto", im.get("SEL OUTER EXCESS CONTACT"));

                String diecLabel = "Delete Inner Excess Contact";
                GeomFeature diec = model.geom(id).create(im.next("del",diecLabel), "Delete");
                diec.label(diecLabel);
                diec.selection("input").init(3);
                diec.selection("input").named(im.get("SEL INNER EXCESS CONTACT"));

                String doecLabel = "Delete Outer Excess Contact";
                GeomFeature doec = model.geom(id).create(im.next("del",doecLabel), "Delete");
                doec.label(doecLabel);
                doec.selection("input").init(3);
                doec.selection("input").named(im.get("SEL OUTER EXCESS CONTACT"));

                String irsLabel = "If Recess";
                GeomFeature irs = model.geom(id).create(im.next("if",irsLabel), "If");
                irs.set("condition", "recess_Pitt>0");
                irs.label(irsLabel);

                String rcsLabel = "Recess Cross Section";
                GeomFeature rcs = model.geom(id).create(im.next("wp",rcsLabel), "WorkPlane");
                rcs.label(rcsLabel);
                rcs.set("contributeto", im.get("RECESS CROSS SECTION"));
                rcs.set("planetype", "transformed");
                rcs.set("workplane", im.get("base plane (pre rotation)"));
                rcs.set("transaxis", new int[]{0, 1, 0});
                rcs.set("transrot", "rotation_angle");
                rcs.set("unite", true);

                String cpfrLabel = "wp CONTACT PRE FILLET";
                rcs.geom().selection().create(im.next("csel",cpfrLabel), "CumulativeSelection");
                rcs.geom().selection(im.get(cpfrLabel)).label(cpfrLabel);

                String cfrLabel = "wp CONTACT FILLETED";
                rcs.geom().selection().create(im.next("csel",cfrLabel), "CumulativeSelection");
                rcs.geom().selection(im.get(cfrLabel)).label(cfrLabel);

                String rpfrLabel = "RECESS PRE FILLET";
                rcs.geom().selection().create(im.next("csel",rpfrLabel), "CumulativeSelection");
                rcs.geom().selection(im.get(rpfrLabel)).label(rpfrLabel);

                String rfrLabel = "RECESS FILLETED";
                rcs.geom().selection().create(im.next("csel",rfrLabel), "CumulativeSelection");
                rcs.geom().selection(im.get(rfrLabel)).label(rfrLabel);

                rcs.geom().create("r1", "Rectangle");
                rcs.geom().feature("r1").label("Recess Pre Fillet Corners");
                rcs.geom().feature("r1").set("contributeto", im.get(rpfrLabel));
                rcs.geom().feature("r1").set("pos", new int[]{0, 0});
                rcs.geom().feature("r1").set("base", "center");
                rcs.geom().feature("r1").set("size", new String[]{"w_contact_Pitt", "z_contact_Pitt"});

                String filletrLabel = "wp Fillet Corners";
                GeomFeature filletr = rcs.geom().create(im.next("fil", filletrLabel), "Fillet");
                filletr.label(filletrLabel);

                filletr.set("contributeto", im.get(rfrLabel));
                filletr.set("radius", "fillet_contact_Pitt");
                filletr.selection("point").named(im.get(rpfrLabel));

                String scalerLabel = "scrLabel";
                GeomFeature scaler = rcs.geom().create(im.next("sca",scalerLabel), "Scale");
                scaler.label(scalerLabel);
                scaler.set("type", "anisotropic");
                scaler.set("factor", new String[]{"1", "scale_morph_w_contact_Pitt"});
                scaler.selection("input").named(im.get(rfrLabel));

                rcs.geom().create("mov1", "Move");
                rcs.geom().feature("mov1").set("disply", "z_center");
                rcs.geom().feature("mov1").selection("input").named(im.get(rfrLabel));

                String mrpc1Label = "Make Recess Pre Cuts 1";
                GeomFeature mrpc1 = model.geom(id).create(im.next("ext", mrpc1Label), "Extrude");
                mrpc1.label(mrpc1Label);
                mrpc1.set("contributeto", im.get("RECESS PRE CUTS"));
                mrpc1.setIndex("distance", "2*r_cuff_in_Pitt", 0);
                mrpc1.selection("input").named(im.get("RECESS CROSS SECTION"));

                String ircLabel = "Inner Recess Cutter";
                GeomFeature irc = model.geom(id).create(im.next("cyl", ircLabel), "Cylinder");
                irc.label(ircLabel);
                irc.set("contributeto", im.get("INNER RECESS CUTTER"));
                irc.set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                irc.set("r", "r_cuff_in_Pitt");
                irc.set("h", "L_cuff_Pitt");

                String orcLabel = "Outer Recess Cutter";
                GeomFeature orc = model.geom(id).create(im.next("cyl",orcLabel), "Cylinder");
                orc.label(orcLabel);
                orc.set("contributeto", im.get("OUTER RECESS CUTTER"));
                orc.set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                orc.set("r", "r_inner_contact");
                orc.set("h", "L_cuff_Pitt");

                String roreLabel = "Remove Outer Recess Excess";
                GeomFeature rore = model.geom(id).create(im.next("par",roreLabel), "Partition");
                rore.label(roreLabel);
                rore.set("contributeto", im.get("FINAL RECESS"));
                rore.selection("input").named(im.get("RECESS PRE CUTS"));
                rore.selection("tool").named(im.get("OUTER RECESS CUTTER"));

                String rireLabel = "Remove Inner Recess Excess";
                GeomFeature rire = model.geom(id).create(im.next("par",rireLabel), "Partition");
                rire.label(rireLabel);
                rire.set("contributeto", im.get("FINAL RECESS"));
                rire.selection("input").named(im.get("RECESS PRE CUTS"));
                rire.selection("tool").named(im.get("INNER RECESS CUTTER"));

                String sie1Label = "sel inner excess 1";
                GeomFeature sie1 = model.geom(id).create(im.next("ballsel",sie1Label), "BallSelection");
                sie1.label(sie1Label);
                sie1.set("posx", "((r_inner_contact+recess_Pitt)/2)*cos(rotation_angle)");
                sie1.set("posy", "((r_inner_contact+recess_Pitt)/2)*sin(rotation_angle)");
                sie1.set("posz", "z_center");
                sie1.set("r", 1);
                sie1.set("contributeto", im.get("SEL INNER EXCESS RECESS"));

                String soe1Label = "sel outer excess 1";
                GeomFeature soe1 = model.geom(id).create(im.next("ballsel",soe1Label), "BallSelection");
                soe1.label(soe1Label);
                soe1.set("posx", "((r_cuff_in_Pitt+2*r_cuff_in_Pitt)/2)*cos(rotation_angle)");
                soe1.set("posy", "((r_cuff_in_Pitt+2*r_cuff_in_Pitt)/2)*sin(rotation_angle)");
                soe1.set("posz", "z_center");
                soe1.set("r", 1);
                soe1.set("contributeto", im.get("SEL OUTER EXCESS RECESS"));

                String dierLabel = "Delete Inner Excess Recess";
                GeomFeature dier = model.geom(id).create(im.next("del",dierLabel), "Delete");
                dier.label(dierLabel);
                dier.selection("input").init(3);
                dier.selection("input").named(im.get("SEL INNER EXCESS RECESS"));

                String doerLabel = "Delete Outer Excess Recess";
                GeomFeature doer = model.geom(id).create(im.next("del",doerLabel), "Delete");
                doer.label(doerLabel);
                doer.selection("input").init(3);
                doer.selection("input").named(im.get("SEL OUTER EXCESS RECESS"));

                model.geom(id).create(im.next("endif"), "EndIf");

                String srcsLabel = "src";
                GeomFeature srcs = model.geom(id).create(im.next("pt",srcsLabel), "Point");
                srcs.label(srcsLabel);
                srcs.set("contributeto", im.get("SRC"));
                srcs.set("p", new String[]{"(r_cuff_in_Pitt+recess_Pitt+(thk_contact_Pitt/2))*cos(rotation_angle)", "(r_cuff_in_Pitt+recess_Pitt+(thk_contact_Pitt/2))*sin(rotation_angle)", "z_center"});
                model.geom(id).run();
                break;
            default:
                throw new  IllegalArgumentException("No implementation for part primitive name: " + pseudonym);
        }

        // TODO: I think we will want to move this elsewhere... also try/catch so if breaks you can see in GUI what is was doing
        try {
            model.save("parts_test");
        } catch (IOException e) {
            e.printStackTrace();
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
//    public static boolean createPartInstance(String id, String pseudonym, ModelWrapper2 mw) throws IllegalArgumentException {
//        return createPartInstance(id, pseudonym, mw, null);
//    }

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

//        model.component("comp1").geom("geom1").create("pi21", "PartInstance");
//        model.component("comp1").geom("geom1").feature("pi21").label("LivaNova 1");
//        model.component("comp1").geom("geom1").feature("pi21").set("part", "part5");

        switch (pseudonym) {
            case "TubeCuff_Primitive":
                // Imports
//                model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepdom", "pi4_csel3.dom", "on");

//                model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel3.dom", "on");

//                model.component("comp1").geom("geom1").feature("pi8").setEntry("selkeepdom", "pi8_csel3.dom", "on");
                break;
            case "RibbonContact_Primitive":
                // Imports
//                model.component("comp1").geom("geom1").feature("pi9").setEntry("selkeepdom", "pi9_csel4.dom", "on");
//                model.component("comp1").geom("geom1").feature("pi9").setEntry("selkeeppnt", "pi9_csel3.pnt", "on");

//                model.component("comp1").geom("geom1").feature("pi10").setEntry("selkeepdom", "pi10_csel4.dom", "on");
//                model.component("comp1").geom("geom1").feature("pi10").setEntry("selkeeppnt", "pi10_csel3.pnt", "on");

//                model.component("comp1").geom("geom1").feature("pi11").setEntry("selkeepdom", "pi11_csel4.dom", "on");
//                model.component("comp1").geom("geom1").feature("pi11").setEntry("selkeeppnt", "pi11_csel3.pnt", "on");

//                model.component("comp1").geom("geom1").feature("pi12").setEntry("selkeepdom", "pi12_csel4.dom", "on");
//                model.component("comp1").geom("geom1").feature("pi12").setEntry("selkeeppnt", "pi12_csel3.pnt", "on");

            case "WireContact_Primitive":
                // Imports
//                model.component("comp1").geom("geom1").feature("pi13").setEntry("selkeepdom", "pi13_csel2.dom", "on");
//                model.component("comp1").geom("geom1").feature("pi13").setEntry("selkeeppnt", "pi13_csel3.pnt", "on");
//
//                model.component("comp1").geom("geom1").feature("pi14").setEntry("selkeepdom", "pi14_csel2.dom", "on");
//                model.component("comp1").geom("geom1").feature("pi14").setEntry("selkeeppnt", "pi14_csel3.pnt", "on");

                break;
            case "CircleContact_Primitive":
                // Imports
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepobj", "pi15_csel12", "off");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepobj", "pi15_csel13", "off");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepobj", "pi15_csel14", "off");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepdom", "pi15_ballsel1", "off");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepdom", "pi15_ballsel2", "off");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepdom", "pi15_csel7.dom", "on");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepdom", "pi15_csel12.dom", "off");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepdom", "pi15_csel14.dom", "off");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepbnd", "pi15_csel12.bnd", "off");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepbnd", "pi15_csel13.bnd", "off");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepbnd", "pi15_csel14.bnd", "off");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepedg", "pi15_csel12.edg", "off");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepedg", "pi15_csel13.edg", "off");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeepedg", "pi15_csel14.edg", "off");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeeppnt", "pi15_csel12.pnt", "off");
//                model.component("comp1").geom("geom1").feature("pi15").setEntry("selkeeppnt", "pi15_csel13.pnt", "off");


                break;
            case "HelicalCuffnContact_Primitive":
                // Imports
//                model.component("comp1").geom("geom1").feature("pi21").setEntry("selkeepdom", "pi21_csel2.dom", "on");
//                model.component("comp1").geom("geom1").feature("pi21").setEntry("selkeepdom", "pi21_csel5.dom", "on");
//                model.component("comp1").geom("geom1").feature("pi21").setEntry("selkeepdom", "pi21_csel6.dom", "on");
//                model.component("comp1").geom("geom1").feature("pi21").setEntry("selkeepdom", "pi21_csel8.dom", "on");
//                model.component("comp1").geom("geom1").feature("pi21").setEntry("selkeeppnt", "pi21_csel10.pnt", "on");

                break;
            case "RectangleContact_Primitive":
                // Imports

                break;
            case "Fascicle":
                // Imports

                break;
            case "Nerve":
                // Imports

                break;
            default:
                throw new IllegalArgumentException("No implementation for part instance name: " + pseudonym);
        }

        return true;
    }
}

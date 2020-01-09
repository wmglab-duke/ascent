package model;

import com.comsol.model.*;
import com.comsol.model.physics.PhysicsFeature;
import org.json.JSONArray;
import org.json.JSONObject;

import java.util.HashMap;

class Part {
    /**
     * Create a defined part primitive. There is a finite number of choices, as seen below in the switch.
     * Fun fact: this method is nearly 1400 lines.
     * @param id the part primitive COMSOL id (unique) --> use mw.im.next in call (part)
     * @param pseudonym the global name for that part, as used in mw.im
     * @param mw the ModelWrapper to act upon
     * @return the local IdentifierManager for THIS PART PRIMITIVE --> save when called in ModelWrapper
     * @throws IllegalArgumentException if an invalid pseudonym is passed in --> there is no such primitive to create
     */
    public static IdentifierManager createEnvironmentPartPrimitive(String id, String pseudonym, ModelWrapper mw) throws IllegalArgumentException {
        Model model = mw.getModel();

        // only used once per method, so ok to define outside the switch
        model.geom().create(id, "Part", 3);
        model.geom(id).label(pseudonym);
        model.geom(id).lengthUnit("\u00b5m");

        // only used once per method, so ok to define outside the switch
        IdentifierManager im = new IdentifierManager();
        ModelParam mp = model.geom(id).inputParam();

        if ("Medium_Primitive".equals(pseudonym)) {
            mp.set("radius", "10 [mm]");
            mp.set("length", "100 [mm]");

            im.labels = new String[]{
                    "MEDIUM" //0

            };

            for (String cselMediumLabel : im.labels) {
                model.geom(id).selection().create(im.next("csel", cselMediumLabel), "CumulativeSelection")
                        .label(cselMediumLabel);

            }

            String mediumLabel = "Medium";
            GeomFeature m = model.geom(id).create(im.next("cyl", mediumLabel), "Cylinder");
            m.label(mediumLabel);
            m.set("r", "radius");
            m.set("h", "length");
            m.set("contributeto", im.get("MEDIUM"));

        } else {
            throw new IllegalArgumentException("No implementation for part primitive name: " + pseudonym);

        }
        return im;

    }

    /**
     * TODO
     */
    public static void createEnvironmentPartInstance(String instanceID, String instanceLabel, String pseudonym, ModelWrapper mw,
                                                     JSONObject instanceParams) throws IllegalArgumentException {
        Model model = mw.getModel();

        GeomFeature partInstance = model.component("comp1").geom("geom1").create(instanceID, "PartInstance");
        partInstance.label(instanceLabel);
        partInstance.set("part", mw.im.get(pseudonym));

        IdentifierManager myIM = mw.getPartPrimitiveIM(pseudonym);
        if (myIM == null) throw new IllegalArgumentException("IdentfierManager not created for name: " + pseudonym);

        String[] myLabels = myIM.labels; // may be null, but that is ok if not used

        if ("Medium_Primitive".equals(pseudonym)) {// set instantiation parameters
            String[] mediumParameters = {
                    "radius",
                    "length"

            };

            JSONObject itemObject = ((JSONObject) ((JSONObject) instanceParams.get("medium")).get("bounds"));
            for (String param : mediumParameters) {

                Object testObject = itemObject.get(param);
                if(testObject instanceof Integer){
                    // if int
                    partInstance.setEntry("inputexpr", param, (Integer) itemObject.get(param));

                } else {
                    // if double
                    partInstance.setEntry("inputexpr", param, (Double) itemObject.get(param));

                }
            }

            // imports
            partInstance.set("selkeepnoncontr", false);
            partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[0]) + ".dom", "on"); // MEDIUM

            partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[0]) + ".bnd", "on"); // MEDIUM

            // assign physics
            String groundLabel = "Ground";
            PhysicsFeature gnd = model.component("comp1").physics("ec").create(mw.im.next("gnd", groundLabel), "Ground", 2);
            gnd.label(groundLabel);
            gnd.selection().named("geom1_" + mw.im.get(instanceLabel) + "_" + myIM.get(myLabels[0]) + "_bnd");

        } else {
            throw new IllegalArgumentException("No implementation for part primitive name: " + pseudonym);

        }
    }

    public static IdentifierManager createCuffPartPrimitive(String id, String pseudonym, ModelWrapper mw) throws IllegalArgumentException {
        Model model = mw.getModel();

        // only used once per method, so ok to define outside the switch
        model.geom().create(id, "Part", 3);
        model.geom(id).label(pseudonym);
        model.geom(id).lengthUnit("\u00b5m");

        // only used once per method, so ok to define outside the switch
        IdentifierManager im = new IdentifierManager();
        ModelParam mp = model.geom(id).inputParam();

        // prepare yourself for 1400 lines of pure COMSOL goodness
        // a true behemoth of a switch
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

                im.labels = new String[]{
                        "INNER CUFF SURFACE", //0
                        "OUTER CUFF SURFACE",
                        "CUFF FINAL",
                        "CUFF wGAP PRE HOLES",
                        "CUFF PRE GAP",
                        "CUFF PRE GAP PRE HOLES", //5
                        "CUFF GAP CROSS SECTION",
                        "CUFF GAP",
                        "CUFF PRE HOLES",
                        "HOLE 1",
                        "HOLE 2", //10
                        "HOLES"

                };

                for (String cselTCLabel: im.labels) {
                    model.geom(id).selection().create(im.next("csel", cselTCLabel), "CumulativeSelection")
                            .label(cselTCLabel);

                }

                String micsLabel = "Make Inner Cuff Surface";
                GeomFeature inner_surf = model.geom(id).create(im.next("cyl", micsLabel), "Cylinder");
                inner_surf.label(micsLabel);
                inner_surf.set("contributeto", im.get(im.labels[0]));
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

                String ifg2hLabel = "If (Gap AND 2 Holes)";
                GeomFeature if_gap2holes = model.geom(id).create(im.next("if", ifg2hLabel), "If");
                if_gap2holes.label(ifg2hLabel);
                if_gap2holes.set("condition", "N_holes==2");

                String econmhs2Label = "Make Hole Shape 2";
                GeomFeature econ_makehole2 = model.geom(id).create(im.next("econ",econmhs2Label), "ECone");
                econ_makehole2.label(econmhs2Label);
                econ_makehole2.set("contributeto", im.get("HOLES"));
                econ_makehole2.set("pos", new String[]{"R_in-Buffer_hole/2", "0", "Center-Pitch_holecenter_holecenter/2"});
                econ_makehole2.set("axis", new int[]{1, 0, 0});
                econ_makehole2.set("semiaxes", new String[]{"D_hole/2", "D_hole/2"});
                econ_makehole2.set("h", "(R_out-R_in)+Buffer_hole");
                econ_makehole2.set("rat", "R_out/R_in");

                String endifg2hLabel = "End If (Gap AND 2 Holes)";
                GeomFeature endifg2h = model.geom(id).create(im.next("endif", endifg2hLabel), "EndIf");
                endifg2h.label(endifg2hLabel);

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

                im.labels = new String[]{
                        "CONTACT CROSS SECTION", //0
                        "RECESS CROSS SECTION",
                        "SRC",
                        "CONTACT FINAL",
                        "RECESS FINAL"

                };

                for (String cselRiCLabel: im.labels) {
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

                im.labels = new String[]{
                        "CONTACT CROSS SECTION",
                        "CONTACT FINAL",
                        "SRC"

                };

                for (String cselWCLabel: im.labels) {
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

                im.labels = new String[]{
                        "CONTACT CUTTER IN", //0
                        "PRE CUT CONTACT",
                        "RECESS FINAL",
                        "RECESS OVERSHOOT",
                        "SRC",
                        "PLANE FOR CONTACT", //5
                        "CONTACT FINAL",
                        "CONTACT CUTTER OUT",
                        "BASE CONTACT PLANE (PRE ROTATION)",
                        "PLANE FOR RECESS",
                        "PRE CUT RECESS", //10
                        "RECESS CUTTER IN",
                        "RECESS CUTTER OUT",
                        "BASE PLANE (PRE ROTATION)"

                };

                for (String cselCCLabel: im.labels) {
                    model.geom(id).selection().create(im.next("csel", cselCCLabel), "CumulativeSelection")
                            .label(cselCCLabel);

                }

                String bpprLabel = "Base Plane (Pre Rrotation)";
                GeomFeature baseplane_prerot = model.geom(id).create(im.next("wp", bpprLabel), "WorkPlane");
                baseplane_prerot.label(bpprLabel);
                baseplane_prerot.set("contributeto", im.get("BASE PLANE (PRE ROTATION)"));
                baseplane_prerot.set("quickplane", "yz");
                baseplane_prerot.set("unite", true);
                baseplane_prerot.set("showworkplane", false);

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
                rco.set("selresult", false);
                rco.set("selresultshow", false);

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
                so.set("selkeep", false);

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
                so1.set("selkeep", false);

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

                im.labels = new String[]{
                        "PC1", //0
                        "Cuffp1",
                        "SEL END P1",
                        "PC2",
                        "SRC",
                        "Cuffp2", //5
                        "Conductorp2",
                        "SEL END P2",
                        "Cuffp3",
                        "PC3",
                        "CUFF FINAL" //10

                };

                for (String cselHCCLabel: im.labels) {
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
                mcp1.selection("diredge").set(im.get(pcp1Label) + "(1)", 1);

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
                hicsp3.selection("face").named(im.get("SEL END P2"));

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

                String uspLabel = "Union Silicone Parts";
                model.geom(id).create(im.next("uni", uspLabel), "Union");
                model.geom(id).feature(im.get(uspLabel)).selection("input").set(im.get(mcp1Label), im.get(mcp2Label), im.get(mcp3Label));
                model.geom(id).selection(im.get("CUFF FINAL")).label("CUFF FINAL");
                model.geom(id).feature(im.get(uspLabel)).set("contributeto", im.get("CUFF FINAL"));

                model.geom(id).run();

                break;

            case "RectangleContact_Primitive":
                model.geom(id).inputParam().set("z_center", "0 [mm]");
                model.geom(id).inputParam().set("rotation_angle", "0 [deg]");
                model.geom(id).inputParam().set("w_contact", "0.475 [mm]");
                model.geom(id).inputParam().set("z_contact", "0.475 [mm]");
                model.geom(id).inputParam().set("fillet_contact", "0.1 [mm]");
                model.geom(id).inputParam().set("scale_morph_w_contact", "w_contact_ext_Pitt/w_contact_Pitt");
                model.geom(id).inputParam().set("L_cuff", "4.1917 [mm]");
                model.geom(id).inputParam().set("r_cuff_in", "d_nerve_Pitt/2");
                model.geom(id).inputParam().set("recess", "0 [mm]");
                model.geom(id).inputParam().set("thk_contact", "0.018 [mm]");

                im.labels = new String[]{
                        "OUTER CONTACT CUTTER", //0
                        "SEL INNER EXCESS CONTACT",
                        "INNER CONTACT CUTTER",
                        "SEL OUTER EXCESS RECESS",
                        "SEL INNER EXCESS RECESS",
                        "OUTER CUTTER", //5
                        "FINAL RECESS",
                        "RECESS CROSS SECTION",
                        "OUTER RECESS CUTTER",
                        "RECESS PRE CUTS",
                        "INNER RECESS CUTTER", //10
                        "FINAL CONTACT",
                        "SEL OUTER EXCESS CONTACT",
                        "SEL OUTER EXCESS",
                        "SEL INNER EXCESS",
                        "BASE CONTACT PLANE (PRE ROTATION)", //15
                        "SRC",
                        "CONTACT PRE CUTS",
                        "CONTACT CROSS SECTION",
                        "INNER CUFF CUTTER",
                        "OUTER CUFF CUTTER", //20
                        "FINAL",
                        "INNER CUTTER"

                };

                for (String cselReCLabel: im.labels) {
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
                mcpc.setIndex("distance", "2*R_in_Pitt", 0);
                mcpc.selection("input").named(im.get("CONTACT CROSS SECTION"));

                String iccLabel = "Inner Contact Cutter";
                GeomFeature icc = model.geom(id).create(im.next("cyl",iccLabel), "Cylinder");
                icc.label(iccLabel);
                icc.set("contributeto", im.get("INNER CONTACT CUTTER"));
                icc.set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                icc.set("r", "R_in_Pitt+recess_Pitt");
                icc.set("h", "L_cuff_Pitt");

                String occLabel = "Outer Contact Cutter";
                GeomFeature occ = model.geom(id).create(im.next("cyl",occLabel), "Cylinder");
                occ.label(occLabel);
                occ.set("contributeto", im.get("OUTER CONTACT CUTTER"));
                occ.set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                occ.set("r", "R_in_Pitt+recess_Pitt+thk_contact_Pitt");
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
                sie.set("posx", "((R_in_Pitt+recess_Pitt)/2)*cos(rotation_angle)");
                sie.set("posy", "((R_in_Pitt+recess_Pitt)/2)*sin(rotation_angle)");
                sie.set("posz", "z_center");
                sie.set("r", 1);
                sie.set("contributeto", im.get("SEL INNER EXCESS CONTACT"));
                sie.set("selkeep", false);

                String soeLabel = "sel outer excess";
                GeomFeature soe = model.geom(id).create(im.next("ballsel",soeLabel), "BallSelection");
                soe.label(soeLabel);
                soe.set("posx", "((2*R_in_Pitt-(R_in_Pitt+recess_Pitt+thk_contact_Pitt))/2+R_in_Pitt+recess_Pitt+thk_contact_Pitt)*cos(rotation_angle)");
                soe.set("posy", "((2*R_in_Pitt-(R_in_Pitt+recess_Pitt+thk_contact_Pitt))/2+R_in_Pitt+recess_Pitt+thk_contact_Pitt)*sin(rotation_angle)");
                soe.set("posz", "z_center");
                soe.set("r", 1);
                soe.set("contributeto", im.get("SEL OUTER EXCESS CONTACT"));
                soe.set("selkeep", false);

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
                mrpc1.setIndex("distance", "2*R_in_Pitt", 0);
                mrpc1.selection("input").named(im.get("RECESS CROSS SECTION"));

                String ircLabel = "Inner Recess Cutter";
                GeomFeature irc = model.geom(id).create(im.next("cyl", ircLabel), "Cylinder");
                irc.label(ircLabel);
                irc.set("contributeto", im.get("INNER RECESS CUTTER"));
                irc.set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                irc.set("r", "R_in_Pitt");
                irc.set("h", "L_cuff_Pitt");

                String orcLabel = "Outer Recess Cutter";
                GeomFeature orc = model.geom(id).create(im.next("cyl",orcLabel), "Cylinder");
                orc.label(orcLabel);
                orc.set("contributeto", im.get("OUTER RECESS CUTTER"));
                orc.set("pos", new String[]{"0", "0", "-L_cuff_Pitt/2+z_center"});
                orc.set("r", "R_in_Pitt+recess_Pitt");
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
                sie1.set("posx", "((R_in_Pitt+recess_Pitt)/2)*cos(rotation_angle)");
                sie1.set("posy", "((R_in_Pitt+recess_Pitt)/2)*sin(rotation_angle)");
                sie1.set("posz", "z_center");
                sie1.set("r", 1);
                sie1.set("contributeto", im.get("SEL INNER EXCESS RECESS"));
                sie1.set("selkeep", false);

                String soe1Label = "sel outer excess 1";
                GeomFeature soe1 = model.geom(id).create(im.next("ballsel",soe1Label), "BallSelection");
                soe1.label(soe1Label);
                soe1.set("posx", "((R_in_Pitt+2*R_in_Pitt)/2)*cos(rotation_angle)");
                soe1.set("posy", "((R_in_Pitt+2*R_in_Pitt)/2)*sin(rotation_angle)");
                soe1.set("posz", "z_center");
                soe1.set("r", 1);
                soe1.set("contributeto", im.get("SEL OUTER EXCESS RECESS"));
                soe1.set("selkeep", false);

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
                srcs.set("p", new String[]{"(R_in_Pitt+recess_Pitt+(thk_contact_Pitt/2))*cos(rotation_angle)", "(R_in_Pitt+recess_Pitt+(thk_contact_Pitt/2))*sin(rotation_angle)", "z_center"});

                model.geom(id).run();

                break;

            case "uContact_Primitive":
                model.geom(id).inputParam().set("z_center", "z_center_U");
                model.geom(id).inputParam().set("R_in", "R_in_U");
                model.geom(id).inputParam().set("Tangent", "Tangent_U");
                model.geom(id).inputParam().set("thk_contact", "thk_contact_U");
                model.geom(id).inputParam().set("z_contact", "z_contact_U");

                im.labels = new String[]{
                        "CONTACT XS", //0
                        "CONTACT FINAL",
                        "SRC"

                };

                for (String cselUContactLabel: im.labels) {
                    model.geom(id).selection().create(im.next("csel", cselUContactLabel), "CumulativeSelection")
                            .label(cselUContactLabel);

                }

                String ucontactxsLabel = "Contact XS";
                GeomFeature ucontactxs = model.geom(id).create(im.next("wp",ucontactxsLabel), "WorkPlane");
                ucontactxs.label(ucontactxsLabel);
                ucontactxs.set("contributeto", im.get("CONTACT XS"));
                ucontactxs.set("quickz", "z_center-z_contact/2");
                ucontactxs.set("unite", true);

                String inLineLabel = "INLINE";
                ucontactxs.geom().selection().create(im.next("csel",inLineLabel), "CumulativeSelection");
                ucontactxs.geom().selection(im.get(inLineLabel)).label(inLineLabel);

                String inLineUnionLabel = "INLINE_UNION";
                ucontactxs.geom().selection().create(im.next("csel",inLineUnionLabel), "CumulativeSelection");
                ucontactxs.geom().selection(im.get(inLineUnionLabel)).label(inLineUnionLabel);

                String outLineLabel = "OUTLINE";
                ucontactxs.geom().selection().create(im.next("csel",outLineLabel), "CumulativeSelection");
                ucontactxs.geom().selection(im.get(outLineLabel)).label(outLineLabel);

                String wpucontactxsLabel = "wpCONTACT XS";
                ucontactxs.geom().selection().create(im.next("csel",wpucontactxsLabel), "CumulativeSelection");
                ucontactxs.geom().selection(im.get(wpucontactxsLabel)).label(wpucontactxsLabel);

                String roundInlineLabel = "Round Inline";
                GeomFeature rIL = ucontactxs.geom().create(im.next("c",roundInlineLabel), "Circle");
                rIL.label(roundInlineLabel);
                rIL.set("contributeto", im.get(inLineLabel));
                rIL.set("r", "R_in");

                String rectInlineLabel = "Rect Inline";
                GeomFeature rectIL = ucontactxs.geom().create(im.next("r",rectInlineLabel), "Rectangle");
                rectIL.label(rectInlineLabel);
                rectIL.set("contributeto", im.get(inLineLabel));
                rectIL.set("pos", new String[]{"Tangent/2", "0"});
                rectIL.set("base", "center");
                rectIL.set("size", new String[]{"Tangent", "2*R_in"});

                String uInlinePLabel = "Union Inline Parts";
                GeomFeature uInline = ucontactxs.geom().create(im.next("uni",uInlinePLabel), "Union");
                uInline.label(uInlinePLabel);
                uInline.set("contributeto", im.get(inLineUnionLabel));
                uInline.set("intbnd", false);
                uInline.selection("input").named(im.get(inLineLabel));

                String roLabel = "Round Outline";
                GeomFeature ro = ucontactxs.geom().create(im.next("c",roLabel), "Circle");
                ro.label(roLabel);
                ro.set("contributeto", im.get(outLineLabel));
                ro.set("r", "R_in+thk_contact");

                String rectoLabel = "Rect Outline";
                GeomFeature urect = ucontactxs.geom().create(im.next("r",rectoLabel), "Rectangle");
                urect.label(rectoLabel);
                urect.set("contributeto", im.get(outLineLabel));
                urect.set("pos", new String[]{"Tangent/2", "0"});
                urect.set("base", "center");
                urect.set("size", new String[]{"Tangent", "2*R_in+2*thk_contact"});

                String uOPLabel = "Union Outline Parts";
                GeomFeature uOP = ucontactxs.geom().create(im.next("uni",uOPLabel), "Union");
                uOP.label(uOPLabel);
                uOP.set("contributeto", im.get(inLineUnionLabel));
                uOP.set("intbnd", false);
                uOP.selection("input").named(im.get(outLineLabel));

                String diff2cxsLabel = "Diff to Contact XS";
                GeomFeature diff2cxs = ucontactxs.geom().create(im.next("dif", diff2cxsLabel), "Difference");
                diff2cxs.label(diff2cxsLabel);
                diff2cxs.selection("input").named(im.get(outLineLabel));
                diff2cxs.selection("input2").named(im.get(inLineLabel));

                String umcLabel = "Make Contact";
                GeomFeature umc = model.geom(id).create(im.next("ext",umcLabel), "Extrude");
                umc.label(umcLabel);
                umc.set("contributeto", im.get("CONTACT FINAL"));
                umc.setIndex("distance", "z_contact", 0);
                umc.selection("input").named(im.get("CONTACT XS"));

                String usrcLabel = "Src";
                GeomFeature usrc = model.geom(id).create(im.next("pt",usrcLabel), "Point");
                usrc.label(usrcLabel);
                usrc.set("contributeto", im.get("SRC"));
                usrc.set("p", new String[]{"-R_in-(thk_contact/2)", "0", "z_center"});

                model.geom(id).run();

                break;

            case "uCuff_Primitive":
                model.geom(id).inputParam().set("z_center", "z_center_U");
                model.geom(id).inputParam().set("R_in", "R_in_U");
                model.geom(id).inputParam().set("Tangent", "Tangent_U");
                model.geom(id).inputParam().set("R_out", "R_out_U");
                model.geom(id).inputParam().set("L", "L_U");

                im.labels = new String[]{
                        "CUFF XS", //0
                        "CUFF FINAL"

                };

                for (String cselUCuffLabel: im.labels) {
                    model.geom(id).selection().create(im.next("csel", cselUCuffLabel), "CumulativeSelection")
                            .label(cselUCuffLabel);

                }

                String ucCXSLabel = "Contact XS";
                GeomFeature ucCXS = model.geom(id).create(im.next("wp",ucCXSLabel), "WorkPlane");
                ucCXS.label(ucCXSLabel);
                ucCXS.set("contributeto", im.get("CUFF XS"));
                ucCXS.set("quickz", "z_center-L/2");
                ucCXS.set("unite", true);

                String ucInlineLabel = "INLINE";
                ucCXS.geom().selection().create(im.next("csel",ucInlineLabel), "CumulativeSelection");
                ucCXS.geom().selection(im.get(ucInlineLabel)).label(ucInlineLabel);

                String ucInlineUnion = "INLINE_UNION";
                ucCXS.geom().selection().create(im.next("csel",ucInlineUnion), "CumulativeSelection");
                ucCXS.geom().selection(im.get(ucInlineUnion)).label(ucInlineUnion);

                String ucOutlineLabel = "OUTLINE";
                ucCXS.geom().selection().create(im.next("csel",ucOutlineLabel), "CumulativeSelection");
                ucCXS.geom().selection(im.get(ucOutlineLabel)).label(ucOutlineLabel);

                String ucContactXSLabel = "CONTACT XS";
                ucCXS.geom().selection().create(im.next("csel",ucContactXSLabel), "CumulativeSelection");
                ucCXS.geom().selection(im.get(ucContactXSLabel)).label(ucContactXSLabel);

                String ucOutlineCuffLabel = "OUTLINE_CUFF";
                ucCXS.geom().selection().create(im.next("csel",ucOutlineCuffLabel), "CumulativeSelection");
                ucCXS.geom().selection(im.get(ucOutlineCuffLabel)).label(ucOutlineCuffLabel);

                String ucCircleInlineLabel = "Round Inline";
                GeomFeature ucCircleInline = ucCXS.geom().create(im.next("c",ucCircleInlineLabel), "Circle");
                ucCircleInline.label(ucCircleInlineLabel);
                ucCircleInline.set("contributeto", im.get(ucInlineLabel));
                ucCircleInline.set("r", "R_in");

                String ucRectInlineLabel = "Rect Inline";
                GeomFeature ucRectInline = ucCXS.geom().create(im.next("r",ucRectInlineLabel), "Rectangle");
                ucRectInline.label(ucRectInlineLabel);
                ucRectInline.set("contributeto", im.get(ucInlineLabel));
                ucRectInline.set("pos", new String[]{"Tangent/2", "0"});
                ucRectInline.set("base", "center");
                ucRectInline.set("size", new String[]{"Tangent", "2*R_in"});

                String ucUnionInlineLabel = "Union Inline Parts";
                GeomFeature ucUnionInline = ucCXS.geom().create(im.next("uni",ucUnionInlineLabel), "Union");
                ucUnionInline.label(ucUnionInlineLabel);
                ucUnionInline.set("contributeto", im.get("INLINE_UNION"));
                ucUnionInline.set("intbnd", false);
                ucUnionInline.selection("input").named(im.get("INLINE"));

                String ucCircleOutlineLabel = "Cuff Outline";
                GeomFeature ucCircleOutline = ucCXS.geom().create(im.next("c",ucCircleOutlineLabel), "Circle");
                ucCircleOutline.label(ucCircleOutlineLabel);
                ucCircleOutline.set("contributeto", im.get("OUTLINE_CUFF"));
                ucCircleOutline.set("r", "R_out");

                String ucDiffLabel = "Diff to Cuff XS";
                GeomFeature ucDiff = ucCXS.geom().create(im.next("dif",ucDiffLabel), "Difference");
                ucDiff.label(ucDiffLabel);
                ucDiff.selection("input").named(im.get("OUTLINE_CUFF"));
                ucDiff.selection("input2").named(im.get("INLINE_UNION"));

                String ucExtLabel = "Make Cuff";
                GeomFeature ucExt = model.geom(id).create(im.next("ext",ucExtLabel), "Extrude");
                ucExt.label(ucExtLabel);
                ucExt.set("contributeto", im.get("CUFF FINAL"));
                ucExt.setIndex("distance", "L", 0);
                ucExt.selection("input").named(im.get("CUFF XS"));

                model.geom(id).run();

                break;

            case "CuffFill_Primitive":
                model.geom(id).inputParam().set("Radius", "0.5 [mm]");
                model.geom(id).inputParam().set("Thk", "100 [um]");
                model.geom(id).inputParam().set("L", "2.5 [mm]");
                model.geom(id).inputParam().set("z_center", "0");

                im.labels = new String[]{
                        "CUFF FILL FINAL" //0

                };

                for (String cselCuffFillLabel: im.labels) {
                    model.geom(id).selection().create(im.next("csel", cselCuffFillLabel), "CumulativeSelection")
                            .label(cselCuffFillLabel);

                }

                String cuffFillLabel = "Cuff Fill";
                GeomFeature cf = model.geom(id).create(im.next("cyl",cuffFillLabel), "Cylinder");
                cf.label(cuffFillLabel);
                cf.set("contributeto", im.get("CUFF FILL FINAL"));
                cf.set("pos", new String[]{"0", "0", "z_center-(L/2)"});
                cf.set("r", "Radius");
                cf.set("h", "L");

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
     * Create instance of an ALREADY CREATED part primitive
     * @param instanceID the part instance COMSOL id (unique) --> use mw.im.next in call (pi)
     * @param instanceLabel the name for this instance --> unique, and NOT the same as pseudonym
     * @param pseudonym which primitive to create (it must have already been created in createCuffPartPrimitive())
     * @param mw the ModelWrapper to act upon
     * @param instanceParams instance parameters as loaded in from the associated JSON configuration (in ModelWrapper)
     * @throws IllegalArgumentException if the primitive specified by pseudonym has not been created
     */
    public static void createCuffPartInstance(String instanceID, String instanceLabel, String pseudonym, ModelWrapper mw,
                                              JSONObject instanceParams, JSONObject modelData) throws IllegalArgumentException {

        Model model = mw.getModel();

        GeomFeature partInstance = model.component("comp1").geom("geom1").create(instanceID, "PartInstance");
        partInstance.label(instanceLabel);
        partInstance.set("part", mw.im.get(pseudonym));

        partInstance.set("displ", new String[]{"cuff_shift_x", "cuff_shift_y", "cuff_shift_z"}); // moves cuff around the nerve
        partInstance.set("rot", "cuff_rot");

        JSONObject itemObject = instanceParams.getJSONObject("def");
        IdentifierManager myIM = mw.getPartPrimitiveIM(pseudonym);
        if (myIM == null) throw new IllegalArgumentException("IdentfierManager not created for name: " + pseudonym);

        String[] myLabels = myIM.labels; // may be null, but that is ok if not used

        // set instantiation parameters and import selections
        switch (pseudonym) {
            case "TubeCuff_Primitive":

                // set instantiation parameters
                String[] tubeCuffParameters = {
                        "N_holes",
                        "Theta",
                        "Center",
                        "R_in",
                        "R_out",
                        "L",
                        "Rot_def",
                        "D_hole",
                        "Buffer_hole",
                        "L_holecenter_cuffseam",
                        "Pitch_holecenter_holecenter"

                };

                for (String param : tubeCuffParameters) {
                    partInstance.setEntry("inputexpr", param, (String) itemObject.get(param));

                }

                // imports
                partInstance.set("selkeepnoncontr", false);
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[2]) + ".dom", "on"); // CUFF FINAL

                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[1]) + ".dom", "off"); // OUTER CUFF SURFACE
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[3]) + ".dom", "off"); // CUFF wGAP PRE HOLES
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[4]) + ".dom", "off"); // CUFF PRE GAP
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[5]) + ".dom", "off"); // CUFF PRE GAP PRE HOLES
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[6]) + ".dom", "off"); // CUFF GAP CROSS SECTION
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[7]) + ".dom", "off"); // CUFF GAP
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[8]) + ".dom", "off"); // CUFF PRE HOLES
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[9]) + ".dom", "off"); // HOLE 1
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[10]) + ".dom", "off"); // HOLE 2
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[11]) + ".dom", "off"); // HOLES

                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[1]) + ".pnt", "off"); // OUTER CUFF SURFACE
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[2]) + ".pnt", "off"); // CUFF FINAL
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[3]) + ".pnt", "off"); // CUFF wGAP PRE HOLES
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[4]) + ".pnt", "off"); // CUFF PRE GAP
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[5]) + ".pnt", "off"); // CUFF PRE GAP PRE HOLES
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[6]) + ".pnt", "off"); // CUFF GAP CROSS SECTION
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[7]) + ".pnt", "off"); // CUFF GAP
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[8]) + ".pnt", "off"); // CUFF PRE HOLES
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[9]) + ".pnt", "off"); // HOLE 1
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[10]) + ".pnt", "off"); // HOLE 2
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[11]) + ".pnt", "off"); // HOLES

                break;

            case "RibbonContact_Primitive":

                // set instantiation parameters
                String[] ribbonContactParameters = {
                        "Thk_elec",
                        "L_elec",
                        "R_in",
                        "Recess",
                        "Center",
                        "Theta_contact",
                        "Rot_def"

                };

                for (String param : ribbonContactParameters) {
                    partInstance.setEntry("inputexpr", param, (String) itemObject.get(param));

                }

                // imports
                partInstance.set("selkeepnoncontr", false);
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[1]) + ".dom", "off"); // RECESS CROSS SECTION
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[2]) + ".dom", "off"); // SRC
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[3]) + ".dom", "on"); // CONTACT FINAL
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[4]) + ".dom", "on"); // RECESS FINAL

                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[1]) + ".pnt", "off"); // RECESS CROSS SECTION
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[2]) + ".pnt", "on"); // SRC
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[3]) + ".pnt", "off"); // CONTACT FINAL
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[4]) + ".pnt", "off"); // RECESS FINAL

                // assign physics
                String ribbon_pcsLabel = instanceLabel + " Current Source";
                mw.im.currentPointers.put(instanceLabel,
                        model.component("comp1").physics("ec").create(mw.im.next("pcs", ribbon_pcsLabel), "PointCurrentSource", 0));

                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).selection().named("geom1_" + mw.im.get(instanceLabel) + "_" + myIM.get(myLabels[2]) + "_pnt"); // SRC
                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).set("Qjp", 0.000);
                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).label(ribbon_pcsLabel);

                break;

            case "WireContact_Primitive":

                // set instantiation parameters
                String[] wireContactParameters = {
                        "R_conductor",
                        "R_in",
                        "Center",
                        "Pitch",
                        "Sep_conductor",
                        "Theta_conductor"

                };

                for (String param : wireContactParameters) {
                    partInstance.setEntry("inputexpr", param, (String) itemObject.get(param));

                }

                // imports
                partInstance.set("selkeepnoncontr", false);
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[1]) + ".dom", "on"); // CONTACT FINAL
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[2]) + ".dom", "off"); // SRC

                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[1]) + ".pnt", "off"); // CONTACT FINAL
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[2]) + ".pnt", "on"); // SRC

                // assign physics
                String wire_pcsLabel = instanceLabel + " Current Source";
                mw.im.currentPointers.put(instanceLabel,
                        model.component("comp1").physics("ec").create(mw.im.next("pcs", wire_pcsLabel), "PointCurrentSource", 0));

                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).selection().named("geom1_" + mw.im.get(instanceLabel) + "_" + myIM.get(myLabels[2]) + "_pnt"); // SRC
                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).set("Qjp", 0.000);
                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).label(wire_pcsLabel);

                break;

            case "CircleContact_Primitive":

                // set instantiation parameters
                String[] circleContactParameters = {
                        "Recess",
                        "Rotation_angle",
                        "Center",
                        "Round_def",
                        "R_in",
                        "Contact_depth",
                        "Overshoot",
                        "A_ellipse_contact",
                        "Diam_contact",
                        "L"

                };

                for (String param : circleContactParameters) {
                    partInstance.setEntry("inputexpr", param, (String) itemObject.get(param));

                }

                // imports
                partInstance.set("selkeepnoncontr", false);
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[1]) + ".dom", "off"); // PRE CUT CONTACT
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[2]) + ".dom", "on"); // RECESS FINAL
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[3]) + ".dom", "off"); // RECESS OVERSHOOT
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[4]) + ".dom", "off"); // SRC
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[5]) + ".dom", "off"); // PLANE FOR CONTACT
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[6]) + ".dom", "on"); // CONTACT FINAL
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[7]) + ".dom", "off"); // CONTACT CUTTER OUT
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[8]) + ".dom", "off"); // BASE CONTACT PLANE (PRE ROTATION)
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[9]) + ".dom", "off"); // PLANE FOR RECESS
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[10]) + ".dom", "off"); // PRE CUT RECESS
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[11]) + ".dom", "off"); // RECESS CUTTER IN
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[12]) + ".dom", "off"); // RECESS CUTTER OUT
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[13]) + ".dom", "off"); // BASE PLANE (PRE ROTATION)

                partInstance.setEntry("selkeepobj", instanceID + "_" + myIM.get(myLabels[4]), "off"); // SRC
                partInstance.setEntry("selkeepobj", instanceID + "_" + myIM.get(myLabels[6]), "off"); // CONTACT FINAL
                partInstance.setEntry("selkeepobj", instanceID + "_" + myIM.get(myLabels[7]), "off"); // CONTACT CUTTER OUT

                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[4]) + ".bnd", "off"); // SRC
                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[6]) + ".bnd", "off"); // CONTACT FINAL
                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[8]) + ".bnd", "off"); // CONTACT CUTTER OUT
                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[12]) + ".bnd", "off"); // RECESS CUTTER OUT
                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[13]) + ".bnd", "off"); // BASE PLANE (PRE ROTATION)

                partInstance.setEntry("selkeepedg", instanceID + "_" + myIM.get(myLabels[4]) + ".edg", "off"); // SRC
                partInstance.setEntry("selkeepedg", instanceID + "_" + myIM.get(myLabels[6]) + ".edg", "off"); // CONTACT FINAL
                partInstance.setEntry("selkeepedg", instanceID + "_" + myIM.get(myLabels[8]) + ".edg", "off"); // CONTACT CUTTER OUT

                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[1]) + ".pnt", "off"); // PRE CUT CONTACT
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[2]) + ".pnt", "off"); // RECESS FINAL
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[4]) + ".pnt", "on"); // CONTACT FINAL
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[5]) + ".pnt", "off"); // PLANE FOR CONTACT
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[6]) + ".pnt", "off"); // CONTACT FINAL
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[7]) + ".pnt", "off"); // CONTACT CUTTER OUT
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[8]) + ".pnt", "off"); // CONTACT CUTTER OUT
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[9]) + ".pnt", "off"); // PLANE FOR RECESS
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[10]) + ".pnt", "off"); // PRE CUT RECESS
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[11]) + ".pnt", "off"); // RECESS CUTTER IN
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[12]) + ".pnt", "off"); // RECESS CUTTER OUT
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[13]) + ".pnt", "off"); // BASE PLANE (PRE ROTATION)

                // assign physics
                String circle_pcsLabel = instanceLabel + " Current Source";
                mw.im.currentPointers.put(instanceLabel,
                        model.component("comp1").physics("ec").create(mw.im.next("pcs", circle_pcsLabel), "PointCurrentSource", 0));

                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).selection().named("geom1_" + mw.im.get(instanceLabel) + "_" + myIM.get(myLabels[4]) + "_pnt"); // SRC
                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).set("Qjp", 0.000);
                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).label(circle_pcsLabel);

                break;
            case "HelicalCuffnContact_Primitive":

                // set instantiation parameters
                String[] helicalCuffnContactParameters = {
                        "Center"

                };

                for (String param : helicalCuffnContactParameters) {
                    partInstance.setEntry("inputexpr", param, (String) itemObject.get(param));

                }

                model.component("comp1").geom("geom1").feature(instanceID).setEntry("inputexpr", "Center", (String) itemObject.get("Center"));

                // imports
                partInstance.set("selkeepnoncontr", false);
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[1]) + ".dom", "off"); // Cuffp1
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[3]) + ".dom", "off"); // PC2
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[4]) + ".dom", "off"); // SRC
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[5]) + ".dom", "off"); // Cuffp2
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[6]) + ".dom", "on"); // Conductorp2
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[8]) + ".dom", "off"); // Cuffp3
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[9]) + ".dom", "off"); // PC3
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[10]) + ".dom", "on"); // CUFF FINAL

                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[1]) + ".pnt", "off"); // Cuffp1
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[3]) + ".pnt", "off"); // PC2
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[4]) + ".pnt", "on"); // SRC
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[5]) + ".pnt", "off"); // Cuffp2
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[6]) + ".pnt", "off"); // Conductorp2
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[8]) + ".pnt", "off"); // Cuffp3
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[9]) + ".pnt", "off"); // PC3
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[10]) + ".pnt", "off"); // CUFF FINAL

                // assign physics
                String helix_pcsLabel = instanceLabel + " Current Source";
                mw.im.currentPointers.put(instanceLabel,
                        model.component("comp1").physics("ec").create(mw.im.next("pcs", helix_pcsLabel), "PointCurrentSource", 0));

                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).selection().named("geom1_" + mw.im.get(instanceLabel) + "_" + myIM.get(myLabels[4]) + "_pnt"); // SRC
                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).set("Qjp", 0.000);
                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).label(helix_pcsLabel);

                break;

            case "RectangleContact_Primitive":

                // set instantiation parameters
                String[] rectangleContactParameters = {
                        "z_center",
                        "rotation_angle",
                        "w_contact",
                        "z_contact",
                        "fillet_contact",
                        "scale_morph_w_contact",
                        "L_cuff",
                        "r_cuff_in",
                        "recess",
                        "thk_contact"

                };

                for (String param : rectangleContactParameters) {
                    partInstance.setEntry("inputexpr", param, (String) itemObject.get(param));

                }

                // imports
                partInstance.set("selkeepnoncontr", false);

                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[1]) + ".dom", "off"); // SEL INNER EXCESS CONTACT
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[2]) + ".dom", "off"); // INNER CONTACT CUTTER
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[3]) + ".dom", "off"); // SEL OUTER EXCESS RECESS
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[4]) + ".dom", "off"); // SEL INNER EXCESS RECESS
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[5]) + ".dom", "off"); // OUTER CUTTER
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[6]) + ".dom", "on"); // FINAL RECESS
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[7]) + ".dom", "off"); // RECESS CROSS SECTION
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[8]) + ".dom", "off"); // OUTER RECESS CUTTER
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[9]) + ".dom", "off"); // RECESS PRE CUTS
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[10]) + ".dom", "off"); // INNER RECESS CUTTER
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[11]) + ".dom", "on"); // FINAL CONTACT
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[12]) + ".dom", "off"); // SEL OUTER EXCESS CONTACT
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[13]) + ".dom", "off"); // SEL OUTER EXCESS
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[14]) + ".dom", "off"); // SEL INNER EXCESS
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[15]) + ".dom", "off"); // BASE CONTACT PLANE (PRE ROTATION)
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[16]) + ".dom", "off"); // SRC
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[17]) + ".dom", "off"); // CONTACT PRE CUTS
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[18]) + ".dom", "off"); // CONTACT CROSS SECTION
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[19]) + ".dom", "off"); // INNER CUFF CUTTER
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[20]) + ".dom", "off"); // OUTER CUFF CUTTER
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[21]) + ".dom", "off"); // FINAL
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[22]) + ".dom", "off"); // INNER CUTTER

                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[2]) + ".pnt", "off"); // INNER CONTACT CUTTER
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[5]) + ".pnt", "off"); // OUTER CUTTER
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[6]) + ".pnt", "off"); // FINAL RECESS
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[7]) + ".pnt", "off"); // RECESS CROSS SECTION
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[8]) + ".pnt", "off"); // OUTER RECESS CUTTER
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[9]) + ".pnt", "off"); // RECESS PRE CUTS
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[10]) + ".pnt", "off"); // INNER RECESS CUTTER
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[11]) + ".pnt", "off"); // FINAL CONTACT
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[16]) + ".pnt", "on"); // SRC
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[13]) + ".pnt", "off"); // SEL OUTER EXCESS
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[14]) + ".pnt", "off"); // SEL INNER EXCESS
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[15]) + ".pnt", "off"); // BASE CONTACT PLANE (PRE ROTATION)
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[17]) + ".pnt", "off"); // CONTACT PRE CUTS
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[18]) + ".pnt", "off"); // CONTACT CROSS SECTION
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[19]) + ".pnt", "off"); // INNER CUFF CUTTER
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[20]) + ".pnt", "off"); // OUTER CUFF CUTTER
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[21]) + ".pnt", "off"); // FINAL
                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[22]) + ".pnt", "off"); // INNER CUTTER

                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[13]) + ".bnd", "off"); // SEL OUTER EXCESS
                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[14]) + ".bnd", "off"); // SEL INNER EXCESS
                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[15]) + ".bnd", "off"); // BASE CONTACT PLANE (PRE ROTATION)
                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[16]) + ".bnd", "off"); // SRC
                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[17]) + ".bnd", "off"); // CONTACT PRE CUTS
                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[18]) + ".bnd", "off"); // CONTACT CROSS SECTION
                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[19]) + ".bnd", "off"); // INNER CUFF CUTTER
                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[20]) + ".bnd", "off"); // OUTER CUFF CUTTER
                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[21]) + ".bnd", "off"); // FINAL
                partInstance.setEntry("selkeepbnd", instanceID + "_" + myIM.get(myLabels[22]) + ".bnd", "off"); // INNER CUTTER

                // assign physics
                String square_pcsLabel = instanceLabel + " Current Source";
                mw.im.currentPointers.put(instanceLabel,
                        model.component("comp1").physics("ec").create(mw.im.next("pcs", square_pcsLabel), "PointCurrentSource", 0));

                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).selection().named("geom1_" + mw.im.get(instanceLabel) + "_" + myIM.get(myLabels[16]) + "_pnt"); // SRC
                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).set("Qjp", 0.000);
                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).label(square_pcsLabel);

                break;

            case "uContact_Primitive":
                // set instantiation parameters
                String[] uContactParameters = {
                        "z_center",
                        "R_in",
                        "Tangent",
                        "thk_contact",
                        "z_contact"

                };

                for (String param : uContactParameters) {
                    partInstance.setEntry("inputexpr", param, (String) itemObject.get(param));

                }

                // imports
                partInstance.set("selkeepnoncontr", false);
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[0]) + ".dom", "off"); // CONTACT XS
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[1]) + ".dom", "on"); // CONTACT FINAL
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[2]) + ".dom", "off"); // SRC

                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[1]) + ".pnt", "off"); // CONTACT FINAL

                // assign physics
                String u_pcsLabel = instanceLabel + " Current Source";
                mw.im.currentPointers.put(instanceLabel,
                        model.component("comp1").physics("ec").create(mw.im.next("pcs", u_pcsLabel), "PointCurrentSource", 0));

                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).selection().named("geom1_" + mw.im.get(instanceLabel) + "_" + myIM.get(myLabels[2]) + "_pnt"); // SRC
                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).set("Qjp", 0.000);
                ((PhysicsFeature) mw.im.currentPointers.get(instanceLabel)).label(u_pcsLabel);

                break;

            case "uCuff_Primitive":
                // set instantiation parameters
                String[] uCuffParameters = {
                        "z_center",
                        "R_in",
                        "Tangent",
                        "R_out",
                        "L"

                };

                for (String param : uCuffParameters) {
                    partInstance.setEntry("inputexpr", param, (String) itemObject.get(param));

                }

                // imports
                partInstance.set("selkeepnoncontr", false);
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[0]) + ".dom", "off"); // CUFF XS
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[1]) + ".dom", "on");  // CUFF FINAL

                partInstance.setEntry("selkeeppnt", instanceID + "_" + myIM.get(myLabels[1]) + ".pnt", "off"); // CUFF FINAL

                break;

            case "CuffFill_Primitive":
                // set instantiation parameters
                String[] cuffFillParameters = {
                        "Radius",
                        "Thk",
                        "L",
                        "z_center"

                };

                for (String param : cuffFillParameters) {
                    partInstance.setEntry("inputexpr", param, (String) itemObject.get(param));

                }

                // imports
                partInstance.set("selkeepnoncontr", false);
                partInstance.setEntry("selkeepdom", instanceID + "_" + myIM.get(myLabels[0]) + ".dom", "on"); // CUFF FILL FINAL

                break;

            default:
                throw new IllegalArgumentException("No implementation for part instance name: " + pseudonym);

        }
    }

    /**
     * Build a part of the nerve.
     * @param pseudonym the type of part to build (i.e. FascicleCI, FascicleMesh, Epineurium)
     * @param index what to call this part (i.e. fascicle# or epi#)
     * @param path the absolute (general) directory which holds the trace data in SECTIONWISE2D format
     * @param mw the ModelWrapper which is acted upon
     * @param tracePaths the relative (specific) paths to the required trace data (two keys: "inners" and "outer")
     * @throws IllegalArgumentException there is not a nerve part to build of that type (for typos probably)
     */
    public static void createNervePartInstance(String pseudonym, int index, String path, ModelWrapper mw,
                                               HashMap<String, String[]> tracePaths, JSONObject sampleData, ModelParamGroup nerveParams) throws IllegalArgumentException {

        Model model = mw.getModel();
        IdentifierManager im = mw.im;

        switch (pseudonym) {
            case "FascicleCI":

                String ci_outer_name = "outer" + index;
                String ci_inner_name = "inner" + index;

                String ci_inner_path = path + "/inners/" + tracePaths.get("inners")[0];
                String ci_outer_path = path + "/outer/" + tracePaths.get("outer")[0];

                String ci_inner = tracePaths.get("inners")[0];
                String ci_inner_index = ci_inner.split("\\.")[0];

                String fascicleCI_Inner_Label = ci_inner_name + "_INNERS_CI";
                String fascicleCI_Endo_Label = ci_inner_name + "_ENDONEURIUM";

                im.labels = new String[]{
                        fascicleCI_Inner_Label, //0
                        fascicleCI_Endo_Label
                };

                for (String cselFascicleCILabel: im.labels) {
                    model.component("comp1").geom("geom1").selection().create(im.next("csel", cselFascicleCILabel), "CumulativeSelection")
                            .label(cselFascicleCILabel);
                }

                JSONObject fascicle = sampleData.getJSONObject("Morphology").getJSONArray("Fascicles").getJSONObject(index);
                String morphology_unit = ((JSONObject) sampleData.get("scale")).getString("scale_bar_unit");

                String fascicleCICXLabel = ci_inner_name + " Inner Geometry";
                GeomFeature fascicleCICX = model.component("comp1").geom("geom1").create(im.next("wp",fascicleCICXLabel), "WorkPlane");
                fascicleCICX.label(fascicleCICXLabel);
                fascicleCICX.set("contributeto", im.get(fascicleCI_Inner_Label));
                fascicleCICX.set("unite", true);

                String icLabel = ci_inner_name + "_IC";
                fascicleCICX.geom().selection().create(im.next("csel",icLabel), "CumulativeSelection");
                fascicleCICX.geom().selection(im.get(icLabel)).label(icLabel);

                String icnameLabel = ci_inner_name + " Inner Trace " + ci_inner_index;
                GeomFeature ic = model.component("comp1").geom("geom1").feature(im.get(fascicleCICXLabel)).geom().create(im.next("ic", icnameLabel), "InterpolationCurve");
                ic.label(icnameLabel);
                ic.set("contributeto", im.get(icLabel));
                ic.set("source", "file");
                ic.set("filename", ci_inner_path);
                ic.set("rtol", 0.02);

                String conv2solidLabel = ci_inner_name + " Inner Surface " + ci_inner_index;
                GeomFeature conv2solid = model.component("comp1").geom("geom1").feature(im.get(fascicleCICXLabel)).geom().create(im.next("csol",conv2solidLabel), "ConvertToSolid");
                conv2solid.label(conv2solidLabel);
                conv2solid.selection("input").named(im.get(icLabel));

                String makefascicleLabel = ci_inner_name + " Make Endoneurium";
                GeomFeature makefascicle = model.component("comp1").geom("geom1").create(im.next("ext",makefascicleLabel), "Extrude");
                makefascicle.label(makefascicleLabel);
                makefascicle.set("contributeto", im.get(fascicleCI_Endo_Label));
                makefascicle.setIndex("distance", "z_nerve", 0);
                makefascicle.selection("input").named(im.get(fascicleCI_Inner_Label));

                // Add fascicle domains to ALL_NERVE_PARTS_UNION and ENDO_UNION for later assigning to materials and mesh
                String[] fascicleCIEndoUnions = {ModelWrapper.ALL_NERVE_PARTS_UNION, ModelWrapper.ENDO_UNION};
                mw.contributeToUnions(im.get(makefascicleLabel), fascicleCIEndoUnions);

                // Add physics
                String ciLabel = ci_inner_name + " ContactImpedance";
                PhysicsFeature ci =  model.component("comp1").physics("ec").create(im.next("ci",ciLabel), "ContactImpedance", 2);
                ci.label(ciLabel);
                ci.selection().named("geom1_" + im.get(fascicleCI_Endo_Label) + "_bnd");
                ci.set("spec_type", "surfimp");
                // if inners only
                String mask_input_mode = sampleData.getJSONObject("modes").getString("mask_input");

                String separate = "INNER_AND_OUTER_SEPARATE";
                String compiled = "INNER_AND_OUTER_COMPILED";
                String inners = "INNERS";
                String outers = "OUTERS";

                if ((mask_input_mode.compareTo(separate)) == 0 || (mask_input_mode.compareTo(compiled)) == 0) {
                    String name_area_inner = ci_inner_name + "_area";
                    String name_area_outer = ci_outer_name + "_area";

                    Double inner_area = ((JSONObject) fascicle.getJSONArray("inners").get(0)).getDouble("area");
                    Double outer_area = ((JSONObject) fascicle.get("outer")).getDouble("area");

                    nerveParams.set(name_area_inner, inner_area + " [" + morphology_unit + "^2]", ci_inner_path);
                    nerveParams.set(name_area_outer, outer_area + " [" + morphology_unit + "^2]", ci_outer_path);

                    String rhos = "(1/sigma_perineurium)*(sqrt(" + name_area_outer  + "/pi) - sqrt(" + name_area_inner  + "/pi))"; // A = pi*r^2; r = sqrt(A/pi); thk = sqrt(A_out/pi)-sqrt(A_in/pi); Rm = rho*thk
                    ci.set("rhos", rhos);

                } else if (mask_input_mode.compareTo(inners) == 0) {
                    String name_area_inner = ci_inner_name + "_area";

                    Double inner_area = ((JSONObject) fascicle.getJSONArray("inners").get(0)).getDouble("area");

                    nerveParams.set(name_area_inner, inner_area + " [" + morphology_unit + "^2]", ci_inner_path);

                    String rhos = "(1/sigma_perineurium)*(ci_a*2*sqrt(" + name_area_inner  + "/pi)+ci_b)"; // A = pi*r^2; r = sqrt(A/pi); d = 2*sqrt(A/pi); thk = 0.03*2*sqrt(A/pi); Rm = rho*thk
                    ci.set("rhos", rhos);

                } else if (mask_input_mode.compareTo(outers) == 0) {
                    System.out.println("OUTERS ONLY NOT IMPLEMENTED - NO PERI CONTACT IMPEDANCE SET");

                }

                break;

            case "FascicleMesh":

                String mesh_name = "outer" + index;

                String fascicleMesh_Inners_Label = mesh_name + "_INNERS";
                String fascicleMesh_Outer_Label = mesh_name + "_OUTER";
                String fascicleMesh_Peri_Label = mesh_name + "_PERINEURIUM";
                String fascicleMesh_Endo_Label = mesh_name + "_ENDONEURIUM";

                im.labels = new String[]{
                        fascicleMesh_Inners_Label, //0
                        fascicleMesh_Outer_Label,
                        fascicleMesh_Peri_Label,
                        fascicleMesh_Endo_Label
                };

                for (String cselFascicleMeshLabel: im.labels) {
                    model.component("comp1").geom("geom1").selection().create(im.next("csel", cselFascicleMeshLabel), "CumulativeSelection")
                            .label(cselFascicleMeshLabel);
                }

                String innersPlaneLabel = "outer" + index + " Inners Geometry";
                GeomFeature innersPlane = model.component("comp1").geom("geom1").create(im.next("wp",innersPlaneLabel), "WorkPlane");
                innersPlane.set("contributeto", im.get(fascicleMesh_Inners_Label));
                innersPlane.set("selresult", true);
                innersPlane.set("unite", true);
                innersPlane.label(innersPlaneLabel);

                String innersselLabel = "outer" + index + " inners_all";
                innersPlane.geom().selection().create(im.next("csel",innersselLabel), "CumulativeSelection");
                innersPlane.geom().selection(im.get(innersselLabel)).label(innersselLabel);

                // loop over inners (make IC, convert to solid, add to inners_all)
                for (String inner: tracePaths.get("inners")) {
                    String mesh_inner_path = path + "/inners/" + inner;
                    String mesh_inner_index = inner.split("\\.")[0];

                    String icselLabel = "outer" + index + " IC" + mesh_inner_index;
                    innersPlane.geom().selection().create(im.next("csel",icselLabel), "CumulativeSelection");
                    innersPlane.geom().selection(im.get(icselLabel)).label(icselLabel);

                    String icTraceLabel = "outer" + index + " Inner Trace " + mesh_inner_index;
                    GeomFeature icMesh = innersPlane.geom().create(im.next("ic",icTraceLabel), "InterpolationCurve");
                    icMesh.label(icTraceLabel);
                    icMesh.set("contributeto", im.get(icselLabel));
                    icMesh.set("source", "file");
                    icMesh.set("filename", mesh_inner_path);
                    icMesh.set("rtol", 0.02);

                    String icSurfLabel = "outer" + index + " Inner Surface " + mesh_inner_index;
                    GeomFeature icSurf = innersPlane.geom().create(im.next("csol",icSurfLabel), "ConvertToSolid");
                    icSurf.label(icSurfLabel);
                    icSurf.set("contributeto", im.get(innersselLabel));
                    icSurf.set("keep", false);
                    icSurf.selection("input").named(im.get(icselLabel));
                }

                String outerPlaneLabel = "outer" + index + " Outer Geometry";
                GeomFeature outerPlane = model.component("comp1").geom("geom1").create(im.next("wp",outerPlaneLabel), "WorkPlane");
                outerPlane.label(outerPlaneLabel);
                outerPlane.set("contributeto", im.get(fascicleMesh_Outer_Label));
                outerPlane.set("unite", true);

                String oc1Label = "outer" + index + " OC";
                outerPlane.geom().selection().create(im.next("csel",oc1Label), "CumulativeSelection");
                outerPlane.geom().selection(im.get(oc1Label)).label(oc1Label);

                String outerselLabel = "outer" + index + " sel";
                outerPlane.geom().selection().create(im.next("csel",outerselLabel), "CumulativeSelection");
                outerPlane.geom().selection(im.get(outerselLabel)).label(outerselLabel);

                String mesh_outer_path = path + "/outer/" + tracePaths.get("outer")[0];
                String outeric1Label = "outer" + index + " Outer Trace";
                GeomFeature outeric1 = outerPlane.geom().create(im.next("ic",outeric1Label), "InterpolationCurve");
                outeric1.label(outeric1Label);
                outeric1.set("contributeto", im.get(oc1Label));
                outeric1.set("source", "file");
                outeric1.set("filename", mesh_outer_path);
                outeric1.set("rtol", 0.02);

                String outericSurfaceLabel = "outer" + index + " Outer Surface";
                outerPlane.geom().create(im.next("csol",outericSurfaceLabel), "ConvertToSolid");
                outerPlane.geom().feature(im.get(outericSurfaceLabel)).set("keep", false);
                outerPlane.geom().feature(im.get(outericSurfaceLabel)).selection("input").named(im.get(oc1Label));
                outerPlane.geom().feature(im.get(outericSurfaceLabel)).set("contributeto", im.get(outerselLabel));
                outerPlane.geom().feature(im.get(outericSurfaceLabel)).label(outericSurfaceLabel);

                String makePeriLabel = "outer" + index + " Make Perineurium";
                GeomFeature makePeri = model.component("comp1").geom("geom1").create(im.next("ext",makePeriLabel), "Extrude");
                makePeri.label(makePeriLabel);
                makePeri.set("contributeto", im.get(fascicleMesh_Peri_Label));
                makePeri.set("workplane", im.get(outerPlaneLabel));
                makePeri.setIndex("distance", "z_nerve", 0);
                makePeri.selection("input").named(im.get(fascicleMesh_Outer_Label));

                // Add fascicle domains to ALL_NERVE_PARTS_UNION and ENDO_UNION for later assigning to materials and mesh
                String[] fascicleMeshPeriUnions = {ModelWrapper.ALL_NERVE_PARTS_UNION, ModelWrapper.PERI_UNION};
                mw.contributeToUnions(im.get(makePeriLabel), fascicleMeshPeriUnions);

                String makeEndoLabel = "outer" + index + " Make Endoneurium";
                GeomFeature makeEndo = model.component("comp1").geom("geom1").create(im.next("ext",makeEndoLabel), "Extrude");
                makeEndo.label(makeEndoLabel);
                makeEndo.set("contributeto", im.get(fascicleMesh_Endo_Label));
                makeEndo.set("workplane", im.get(innersPlaneLabel));
                makeEndo.setIndex("distance", "z_nerve", 0);
                makeEndo.selection("input").named(im.get(fascicleMesh_Inners_Label));

                // Add fascicle domains to ALL_NERVE_PARTS_UNION and ENDO_UNION for later assigning to materials and mesh
                String[] fascicleMeshEndoUnions = {ModelWrapper.ALL_NERVE_PARTS_UNION, ModelWrapper.ENDO_UNION};
                mw.contributeToUnions(im.get(makeEndoLabel), fascicleMeshEndoUnions);

                break;

            case "Epineurium":
                im.labels = new String[]{
                        "EPINEURIUM", //0
                        "EPIXS"

                };

                for (String cselEpineuriumLabel: im.labels) {
                    model.component("comp1").geom("geom1").selection().create(im.next("csel", cselEpineuriumLabel), "CumulativeSelection")
                            .label(cselEpineuriumLabel);
                }

                String epineuriumXsLabel = "Epineurium Cross Section";
                GeomFeature epineuriumXs = model.component("comp1").geom("geom1").create(im.next("wp",epineuriumXsLabel), "WorkPlane");
                epineuriumXs.label("Epineurium Cross Section");
                epineuriumXs.set("contributeto", im.get("EPIXS"));
                epineuriumXs.set("unite", true);
                epineuriumXs.geom().create("e1", "Ellipse");
                epineuriumXs.geom().feature("e1").set("semiaxes", new String[]{"r_nerve", "r_nerve"}); // TODO make these 'nerve_a' and 'nerve_b'

                String epiLabel = "Make Epineurium";
                GeomFeature epi = model.component("comp1").geom("geom1").create(im.next("ext",epiLabel), "Extrude");
                epi.label(epiLabel);
                epi.set("contributeto", im.get("EPINEURIUM"));
                epi.setIndex("distance", "z_nerve", 0);
                epi.selection("input").named(im.get("EPIXS"));

                // Add epi domains to ALL_NERVE_PARTS_UNION for later assigning to materials and mesh
                String[] epiUnions = {ModelWrapper.ALL_NERVE_PARTS_UNION};
                mw.contributeToUnions(im.get(epiLabel), epiUnions);

                break;

            default:
                throw new IllegalArgumentException("No implementation for part instance name: " + pseudonym);

        }
    }

    /**
     * Create a material!
     * @param materialID the material COMSOL id (unique) --> use mw.im.next in call (mat#)
     * @param function the "pseudonym" for that material, matching the name in master.json TODO
     * @param config JSON data from master.json
     * @param mw the ModelWrapper to act upon
     */
    public static void defineMaterial(String materialID, String function, JSONObject modelData, JSONObject config,
                                      ModelWrapper mw, ModelParamGroup materialParams) {

        Model model = mw.getModel();
        model.material().create(materialID, "Common", "");
        model.material(materialID).label(function);

        JSONObject sigma;
        String material;
        String materialDescription;

        // if the material is defined explicitly in the model.json file, then the program will use the value stored in
        // model.json, otherwise it will use the conductivity value stored in the materials.json file. This ties material
        // parameters used to a specific model.
        if (modelData.getJSONObject("conductivities").getJSONObject("defaults").has(function)) {
            material = modelData.getJSONObject("conductivities").getJSONObject("defaults").getString(function);
            sigma = config.getJSONObject("conductivities").getJSONObject(material);
            materialDescription = "default: " + material;
        } else {
            sigma = modelData.getJSONObject("conductivities").getJSONObject("custom").getJSONObject(function);
            materialDescription = "custom: " + sigma.getString("label");
        }
        String entry = sigma.getString("value");

        if (entry.equals("anisotropic")) {
            String entry_x = sigma.getString("sigma_x");
            String entry_y = sigma.getString("sigma_y");
            String entry_z = sigma.getString("sigma_z");

            materialParams.set("sigma_" + function + "_x", "(" + entry_x + ")", materialDescription);
            materialParams.set("sigma_" + function + "_y", "(" + entry_y + ")", materialDescription);
            materialParams.set("sigma_" + function + "_z", "(" + entry_z + ")", materialDescription);

            model.material(materialID).propertyGroup("def").set("electricconductivity", new String[]{
                    "sigma_endoneurium_x", "0", "0",
                    "0", "sigma_endoneurium_y", "0",
                    "0", "0", "sigma_endoneurium_z"
            });
        } else {
            String unit = sigma.getString("unit");
            materialParams.set("sigma_" + function, "(" + entry + ")" + " " + unit, materialDescription);
            model.material(materialID).propertyGroup("def").set("electricconductivity", "sigma_" + function);
        }
    }

    public static void addCuffPartMaterialAssignment(String instanceLabel, String pseudonym, ModelWrapper mw,
            JSONObject instanceParams) throws IllegalArgumentException {

        Model model = mw.getModel();

        IdentifierManager myIM = mw.getPartPrimitiveIM(pseudonym);
        if (myIM == null) throw new IllegalArgumentException("IdentfierManager not created for name: " + pseudonym);

        String[] myLabels = myIM.labels; // may be null, but that is ok if not used

        // assign cuff materials
        JSONArray materials = instanceParams.getJSONArray("materials");
        for(Object o: materials) {

            int label_index = ((JSONObject) o).getInt("label_index");
            String selection = myLabels[label_index];
            String info = ((JSONObject) o).getString("info");

            if(myIM.hasPseudonym(selection)) {
                String linkLabel = String.join("/", new String[]{instanceLabel, selection, info});
                Material mat = model.component("comp1").material().create(mw.im.next("matlnk", linkLabel), "Link"); // TODO
                mat.label(linkLabel);
                mat.set("link", mw.im.get(info));
                mat.selection().named("geom1_" + mw.im.get(instanceLabel) + "_" + myIM.get(selection) + "_dom");

            }
        }
    }
}

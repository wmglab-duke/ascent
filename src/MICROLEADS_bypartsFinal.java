/*
 * MICROLEADS_bypartsFinal.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Oct 25 2019, 18:17 by COMSOL 5.4.0.388. */
public class MICROLEADS_bypartsFinal {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model.modelPath("D:\\Documents\\MicroLeads");

    model.label("MICROLEADS_bypartsFinal.mph");

    model.param().set("R_out_U", "0.5 [mm]");
    model.param().set("L_U", "2.5 [mm]", "Ask Gabe");
    model.param().set("R_in_U", "138 [um]");
    model.param().set("Tangent_U", "322 [um]");
    model.param().set("z_center_U", "0");
    model.param().set("thk_contact_U", "0.02 [mm]");
    model.param().set("z_contact_U", "0.7 [mm]");
    model.param().set("Pitch_U", "0.8 [mm]");

    model.component().create("comp1", true);

    model.component("comp1").geom().create("geom1", 3);

    model.component("comp1").mesh().create("mesh1");

    model.geom().create("part1", "Part", 3);
    model.geom().create("part2", "Part", 3);
    model.geom("part1").label("uContact");

    model.geom("part1").inputParam().set("z_center", "z_center_U");
    model.geom("part1").inputParam().set("R_in", "R_in_U");
    model.geom("part1").inputParam().set("Tangent", "Tangent_U");
    model.geom("part1").inputParam().set("thk_contact", "thk_contact_U");
    model.geom("part1").inputParam().set("z_contact", "z_contact_U");

    model.geom("part1").selection().create("csel1", "CumulativeSelection");
    model.geom("part1").selection("csel1").label("CONTACT XS");
    model.geom("part1").selection().create("csel2", "CumulativeSelection");
    model.geom("part1").selection("csel2").label("CONTACT FINAL");
    model.geom("part1").selection().create("csel3", "CumulativeSelection");
    model.geom("part1").selection("csel3").label("SRC");

    model.geom("part1").create("wp1", "WorkPlane");
    model.geom("part1").feature("wp1").label("Contact XS");
    model.geom("part1").feature("wp1").set("contributeto", "csel1");
    model.geom("part1").feature("wp1").set("quickz", "z_center-z_contact/2");
    model.geom("part1").feature("wp1").set("unite", true);
    model.geom("part1").feature("wp1").geom().selection().create("csel1", "CumulativeSelection");
    model.geom("part1").feature("wp1").geom().selection("csel1").label("INLINE");
    model.geom("part1").feature("wp1").geom().selection().create("csel2", "CumulativeSelection");
    model.geom("part1").feature("wp1").geom().selection("csel2").label("INLINE_UNION");
    model.geom("part1").feature("wp1").geom().selection().create("csel3", "CumulativeSelection");
    model.geom("part1").feature("wp1").geom().selection("csel3").label("OUTLINE");
    model.geom("part1").feature("wp1").geom().selection().create("csel4", "CumulativeSelection");
    model.geom("part1").feature("wp1").geom().selection("csel4").label("CONTACT XS");
    model.geom("part1").feature("wp1").geom().create("c1", "Circle");
    model.geom("part1").feature("wp1").geom().feature("c1").label("Round Inline");
    model.geom("part1").feature("wp1").geom().feature("c1").set("contributeto", "csel1");
    model.geom("part1").feature("wp1").geom().feature("c1").set("r", "R_in");
    model.geom("part1").feature("wp1").geom().create("r1", "Rectangle");
    model.geom("part1").feature("wp1").geom().feature("r1").label("Rect Inline");
    model.geom("part1").feature("wp1").geom().feature("r1").set("contributeto", "csel1");
    model.geom("part1").feature("wp1").geom().feature("r1").set("pos", new String[]{"Tangent/2", "0"});
    model.geom("part1").feature("wp1").geom().feature("r1").set("base", "center");
    model.geom("part1").feature("wp1").geom().feature("r1").set("size", new String[]{"Tangent", "2*R_in"});
    model.geom("part1").feature("wp1").geom().create("uni1", "Union");
    model.geom("part1").feature("wp1").geom().feature("uni1").label("Union Inline Parts");
    model.geom("part1").feature("wp1").geom().feature("uni1").set("contributeto", "csel2");
    model.geom("part1").feature("wp1").geom().feature("uni1").set("intbnd", false);
    model.geom("part1").feature("wp1").geom().feature("uni1").selection("input").named("csel1");
    model.geom("part1").feature("wp1").geom().create("c2", "Circle");
    model.geom("part1").feature("wp1").geom().feature("c2").label("Round Outline");
    model.geom("part1").feature("wp1").geom().feature("c2").set("contributeto", "csel3");
    model.geom("part1").feature("wp1").geom().feature("c2").set("r", "R_in+thk_contact");
    model.geom("part1").feature("wp1").geom().create("r2", "Rectangle");
    model.geom("part1").feature("wp1").geom().feature("r2").label("Rect Outline");
    model.geom("part1").feature("wp1").geom().feature("r2").set("contributeto", "csel3");
    model.geom("part1").feature("wp1").geom().feature("r2").set("pos", new String[]{"Tangent/2", "0"});
    model.geom("part1").feature("wp1").geom().feature("r2").set("base", "center");
    model.geom("part1").feature("wp1").geom().feature("r2")
         .set("size", new String[]{"Tangent", "2*R_in+2*thk_contact"});
    model.geom("part1").feature("wp1").geom().create("uni2", "Union");
    model.geom("part1").feature("wp1").geom().feature("uni2").label("Union Outline Parts");
    model.geom("part1").feature("wp1").geom().feature("uni2").set("contributeto", "csel2");
    model.geom("part1").feature("wp1").geom().feature("uni2").set("intbnd", false);
    model.geom("part1").feature("wp1").geom().feature("uni2").selection("input").named("csel3");
    model.geom("part1").feature("wp1").geom().create("dif1", "Difference");
    model.geom("part1").feature("wp1").geom().feature("dif1").label("Diff to Contact XS");
    model.geom("part1").feature("wp1").geom().feature("dif1").selection("input").named("csel3");
    model.geom("part1").feature("wp1").geom().feature("dif1").selection("input2").named("csel1");
    model.geom("part1").create("ext1", "Extrude");
    model.geom("part1").feature("ext1").label("Make Contact");
    model.geom("part1").feature("ext1").set("contributeto", "csel2");
    model.geom("part1").feature("ext1").setIndex("distance", "z_contact", 0);
    model.geom("part1").feature("ext1").selection("input").named("csel1");
    model.geom("part1").create("pt1", "Point");
    model.geom("part1").feature("pt1").label("Src");
    model.geom("part1").feature("pt1").set("contributeto", "csel3");
    model.geom("part1").feature("pt1").set("p", new String[]{"-R_in-(thk_contact/2)", "0", "z_center"});
    model.geom("part1").run();


    model.geom("part2").label("uCuff");
    model.geom("part2").inputParam().set("z_center", "z_center_U");
    model.geom("part2").inputParam().set("R_in", "R_in_U");
    model.geom("part2").inputParam().set("Tangent", "Tangent_U");
    model.geom("part2").inputParam().set("R_out", "R_out_U");
    model.geom("part2").inputParam().set("L", "L_U");

    model.geom("part2").selection().create("csel1", "CumulativeSelection");
    model.geom("part2").selection("csel1").label("CUFF XS");
    model.geom("part2").selection().create("csel2", "CumulativeSelection");
    model.geom("part2").selection("csel2").label("CUFF FINAL");

    model.geom("part2").create("wp1", "WorkPlane");
    model.geom("part2").feature("wp1").label("Contact XS");
    model.geom("part2").feature("wp1").set("contributeto", "csel1");
    model.geom("part2").feature("wp1").set("quickz", "z_center-L/2");
    model.geom("part2").feature("wp1").set("unite", true);
    model.geom("part2").feature("wp1").geom().selection().create("csel1", "CumulativeSelection");
    model.geom("part2").feature("wp1").geom().selection("csel1").label("INLINE");
    model.geom("part2").feature("wp1").geom().selection().create("csel2", "CumulativeSelection");
    model.geom("part2").feature("wp1").geom().selection("csel2").label("INLINE_UNION");
    model.geom("part2").feature("wp1").geom().selection().create("csel3", "CumulativeSelection");
    model.geom("part2").feature("wp1").geom().selection("csel3").label("OUTLINE");
    model.geom("part2").feature("wp1").geom().selection().create("csel4", "CumulativeSelection");
    model.geom("part2").feature("wp1").geom().selection("csel4").label("CONTACT XS");
    model.geom("part2").feature("wp1").geom().selection().create("csel5", "CumulativeSelection");
    model.geom("part2").feature("wp1").geom().selection("csel5").label("OUTLINE_CUFF");
    model.geom("part2").feature("wp1").geom().create("c1", "Circle");
    model.geom("part2").feature("wp1").geom().feature("c1").label("Round Inline");
    model.geom("part2").feature("wp1").geom().feature("c1").set("contributeto", "csel1");
    model.geom("part2").feature("wp1").geom().feature("c1").set("r", "R_in");
    model.geom("part2").feature("wp1").geom().create("r1", "Rectangle");
    model.geom("part2").feature("wp1").geom().feature("r1").label("Rect Inline");
    model.geom("part2").feature("wp1").geom().feature("r1").set("contributeto", "csel1");
    model.geom("part2").feature("wp1").geom().feature("r1").set("pos", new String[]{"Tangent/2", "0"});
    model.geom("part2").feature("wp1").geom().feature("r1").set("base", "center");
    model.geom("part2").feature("wp1").geom().feature("r1").set("size", new String[]{"Tangent", "2*R_in"});
    model.geom("part2").feature("wp1").geom().create("uni1", "Union");
    model.geom("part2").feature("wp1").geom().feature("uni1").label("Union Inline Parts");
    model.geom("part2").feature("wp1").geom().feature("uni1").set("contributeto", "csel2");
    model.geom("part2").feature("wp1").geom().feature("uni1").set("intbnd", false);
    model.geom("part2").feature("wp1").geom().feature("uni1").selection("input").named("csel1");
    model.geom("part2").feature("wp1").geom().create("c2", "Circle");
    model.geom("part2").feature("wp1").geom().feature("c2").label("Cuff Outline");
    model.geom("part2").feature("wp1").geom().feature("c2").set("contributeto", "csel5");
    model.geom("part2").feature("wp1").geom().feature("c2").set("r", "R_out");
    model.geom("part2").feature("wp1").geom().create("dif1", "Difference");
    model.geom("part2").feature("wp1").geom().feature("dif1").label("Diff to Cuff XS");
    model.geom("part2").feature("wp1").geom().feature("dif1").selection("input").named("csel5");
    model.geom("part2").feature("wp1").geom().feature("dif1").selection("input2").named("csel2");
    model.geom("part2").create("ext1", "Extrude");
    model.geom("part2").feature("ext1").label("Make Cuff");
    model.geom("part2").feature("ext1").set("contributeto", "csel2");
    model.geom("part2").feature("ext1").setIndex("distance", "L", 0);
    model.geom("part2").feature("ext1").selection("input").named("csel1");

    model.geom("part2").run();
    model.component("comp1").geom("geom1").create("pi1", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi1").label("uCuff 1");
    model.component("comp1").geom("geom1").feature("pi1").set("part", "part2");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("inputexpr", "z_center", "z_center_U");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("inputexpr", "R_in", "R_in_U");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("inputexpr", "Tangent", "Tangent_U");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("inputexpr", "R_out", "R_out_U");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("inputexpr", "L", "L_U");
    model.component("comp1").geom("geom1").feature("pi1").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").create("pi2", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "z_center", "z_center_U-Pitch_U/2");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "R_in", "R_in_U");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "Tangent", "Tangent_U");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "thk_contact", "thk_contact_U");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "z_contact", "z_contact_U");
    model.component("comp1").geom("geom1").feature("pi2").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi2").setEntry("selkeeppnt", "pi2_csel3.pnt", "on");
    model.component("comp1").geom("geom1").create("pi3", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "z_center", "z_center_U+Pitch_U/2");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "R_in", "R_in_U");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "Tangent", "Tangent_U");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "thk_contact", "thk_contact_U");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "z_contact", "z_contact_U");
    model.component("comp1").geom("geom1").feature("pi3").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel3.pnt", "on");
    model.component("comp1").geom("geom1").run();
    model.component("comp1").geom("geom1").run("fin");

    model.component("comp1").physics().create("ec", "ConductiveMedia", "geom1");
    model.component("comp1").physics("ec").create("pcs1", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs1").selection().named("geom1_pi2_csel3_pnt");
    model.component("comp1").physics("ec").create("pcs2", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs2").selection().named("geom1_pi3_csel3_pnt");

    model.component("comp1").view("view1").set("transparency", true);
    model.view("view2").set("transparency", true);
    model.view("view4").axis().set("xmin", -1.709999778540805E-4);
    model.view("view4").axis().set("xmax", 3.3500001882202923E-4);
    model.view("view4").axis().set("ymin", -1.7667598149273545E-4);
    model.view("view4").axis().set("ymax", 1.7667598149273545E-4);
    model.view("view5").axis().set("xmin", -0.0015752000035718083);
    model.view("view5").axis().set("xmax", 0.0015752000035718083);
    model.view("view5").axis().set("ymin", -0.0010999999940395355);
    model.view("view5").axis().set("ymax", 0.0010999999940395355);

    model.study().create("std1");
    model.study("std1").create("stat", "Stationary");

    return model;
  }

  public static void main(String[] args) {
    run();
  }

}

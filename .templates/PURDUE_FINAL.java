/*
 * PURDUE_FINAL.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Aug 22 2019, 18:07 by COMSOL 5.4.0.388. */
public class PURDUE_FINAL {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model.modelPath("D:\\Documents\\ModularCuffs");

    model.label("PURDUE_FINAL.mph");

    model.param().set("r_cuff_in_pre", "317.5 [um]");
    model.param().set("r_nerve", "0.3 [mm]");
    model.param().set("thk_medium_gap_internal", "0");
    model.param().set("r_conductor", "37.5 [um]");
    model.param().set("sep_conductor", "10 [um]");
    model.param().set("r_cuff_in", "max(r_nerve+thk_medium_gap_internal+2*r_conductor+sep_conductor,r_cuff_in_pre)");
    model.param().set("percent_circ_cuff_pre", "1");
    model.param().set("percent_circ_cuff", "percent_circ_cuff_pre*(r_cuff_in_pre/r_cuff_in)");
    model.param().set("thk_cuff", "0.279 [mm]");
    model.param().set("r_cuff_out", "r_cuff_in+thk_cuff");
    model.param().set("L_cuff", "3.5 [mm]");
    model.param().set("pitch", "1.5 [mm]");
    model.param().set("z_nerve", "20 [mm]");
    model.param().set("percent_circ_conductor_pre", "0.8");
    model.param()
         .set("percent_circ_conductor", "percent_circ_conductor_pre*((r_cuff_in_pre-sep_conductor-2*r_conductor)/(r_cuff_in-sep_conductor-2*r_conductor))");
    model.param().set("theta_cuff", "percent_circ_cuff*360 [deg]");
    model.param().set("theta_cuff_pre", "360 [deg]");
    model.param().set("zw_rot", "0");
    model.param().set("theta_conductor_pre", "percent_circ_conductor_pre*360 [deg]");
    model.param().set("theta_conductor", "percent_circ_conductor*360 [deg]");
    model.param().set("thk_saline", "0.1 [mm]");
    model.param().set("r_ground", "5 [mm]");

    model.component().create("comp1", true);

    model.component("comp1").geom().create("geom1", 3);

    model.component("comp1").mesh().create("mesh1");

    model.geom().create("part1", "Part", 3);
    model.geom().create("part2", "Part", 3);
    model.geom().create("part3", "Part", 3);
    model.geom().create("part4", "Part", 3);
    model.geom("part1").label("Cuff");
    model.geom("part1").lengthUnit("\u00b5m");
    model.geom("part1").inputParam().set("z_center", "0");
    model.geom("part1").inputParam().set("rotation_angle", "0");
    model.geom("part1").selection().create("csel1", "CumulativeSelection");
    model.geom("part1").selection("csel1").label("INNER CUFF SURFACE");
    model.geom("part1").selection().create("csel2", "CumulativeSelection");
    model.geom("part1").selection("csel2").label("OUTER CUFF SURFACE");
    model.geom("part1").selection().create("csel3", "CumulativeSelection");
    model.geom("part1").selection("csel3").label("INNER CUFF PRE CUT GAP");
    model.geom("part1").selection().create("csel4", "CumulativeSelection");
    model.geom("part1").selection("csel4").label("INNER CUFF GAP CUT CROSS SECTION");
    model.geom("part1").selection().create("csel5", "CumulativeSelection");
    model.geom("part1").selection("csel5").label("INNER CUFF CUT");
    model.geom("part1").selection().create("csel6", "CumulativeSelection");
    model.geom("part1").selection("csel6").label("INNER CUFF FINAL");
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
    model.geom("part1").feature("cyl2").set("r", "r_cuff_in+thk_cuff");
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
    model.geom("part1").feature("wp1").set("contributeto", "csel4");
    model.geom("part1").feature("wp1").set("quickplane", "xz");
    model.geom("part1").feature("wp1").set("unite", true);
    model.geom("part1").feature("wp1").geom().create("r1", "Rectangle");
    model.geom("part1").feature("wp1").geom().feature("r1").label("Inner Cuff Gap Cut Cross Section");
    model.geom("part1").feature("wp1").geom().feature("r1")
         .set("pos", new String[]{"r_cuff_in+(thk_cuff/2)", "z_center"});
    model.geom("part1").feature("wp1").geom().feature("r1").set("base", "center");
    model.geom("part1").feature("wp1").geom().feature("r1").set("size", new String[]{"thk_cuff", "L_cuff"});
    model.geom("part1").create("rev1", "Revolve");
    model.geom("part1").feature("rev1").label("Make Cuff Pre Cut Gap");
    model.geom("part1").feature("rev1").set("contributeto", "csel5");
    model.geom("part1").feature("rev1").set("angle1", "theta_cuff+rotation_angle");
    model.geom("part1").feature("rev1").set("angle2", "360+rotation_angle");
    model.geom("part1").feature("rev1").selection("input").set("wp1");
    model.geom("part1").create("dif2", "Difference");
    model.geom("part1").feature("dif2").label("Cut Gap");
    model.geom("part1").feature("dif2").selection("input").named("csel3");
    model.geom("part1").feature("dif2").selection("input2").named("csel5");
    model.geom("part1").create("endif1", "EndIf");
    model.geom("part1").run();
    model.geom("part2").label("Contact");
    model.geom("part2").lengthUnit("\u00b5m");
    model.geom("part2").inputParam().set("z_center", "0");
    model.geom("part2").inputParam().set("rotation_angle", "0");
    model.geom("part2").selection().create("csel1", "CumulativeSelection");
    model.geom("part2").selection("csel1").label("SRC");
    model.geom("part2").selection().create("csel2", "CumulativeSelection");
    model.geom("part2").selection("csel2").label("CONTACT FINAL");
    model.geom("part2").create("wp1", "WorkPlane");
    model.geom("part2").feature("wp1").label("Contact Radial Cross Section");
    model.geom("part2").feature("wp1").set("quickplane", "zx");
    model.geom("part2").feature("wp1").set("unite", true);
    model.geom("part2").feature("wp1").geom().selection().create("csel1", "CumulativeSelection");
    model.geom("part2").feature("wp1").geom().selection("csel1").label("CONTACT RADIAL CROSS SECTION");
    model.geom("part2").feature("wp1").geom().create("c1", "Circle");
    model.geom("part2").feature("wp1").geom().feature("c1").label("Contact Radial Cross Section");
    model.geom("part2").feature("wp1").geom().feature("c1").set("contributeto", "csel1");
    model.geom("part2").feature("wp1").geom().feature("c1")
         .set("pos", new String[]{"z_center", "r_cuff_in-r_conductor-sep_conductor"});
    model.geom("part2").feature("wp1").geom().feature("c1").set("r", "r_conductor");
    model.geom("part2").create("rev1", "Revolve");
    model.geom("part2").feature("rev1").label("Make Contact");
    model.geom("part2").feature("rev1").set("contributeto", "csel2");
    model.geom("part2").feature("rev1").set("angle1", "rotation_angle-(theta_conductor/2)");
    model.geom("part2").feature("rev1").set("angle2", "rotation_angle+(theta_conductor/2)");
    model.geom("part2").feature("rev1").set("axis", new int[]{1, 0});
    model.geom("part2").feature("rev1").selection("input").set("wp1");
    model.geom("part2").create("pt1", "Point");
    model.geom("part2").feature("pt1").label("src");
    model.geom("part2").feature("pt1").set("contributeto", "csel1");
    model.geom("part2").feature("pt1")
         .set("p", new String[]{"(r_cuff_in-r_conductor-sep_conductor)*cos(rotation_angle)", "(r_cuff_in-r_conductor-sep_conductor)*sin(rotation_angle)", "z_center"});
    model.geom("part2").run();
    model.geom("part3").label("Cuff Fill");
    model.geom("part3").inputParam().set("z_center", "0");
    model.geom("part3").selection().create("csel1", "CumulativeSelection");
    model.geom("part3").selection("csel1").label("CUFF FILL");
    model.geom("part3").create("cyl1", "Cylinder");
    model.geom("part3").feature("cyl1").label("Cuff Fill");
    model.geom("part3").feature("cyl1").set("contributeto", "csel1");
    model.geom("part3").feature("cyl1").set("pos", new String[]{"0", "0", "z_center-(L_cuff/2)-thk_saline"});
    model.geom("part3").feature("cyl1").set("r", "r_cuff_in+thk_cuff+thk_saline");
    model.geom("part3").feature("cyl1").set("h", "L_cuff+2*thk_saline");
    model.geom("part3").run();
    model.geom("part4").label("Distant Ground");
    model.geom("part4").inputParam().set("z_center", "z_nerve/2");
    model.geom("part4").selection().create("csel1", "CumulativeSelection");
    model.geom("part4").selection("csel1").label("DISTANT GROUND");
    model.geom("part4").create("cyl1", "Cylinder");
    model.geom("part4").feature("cyl1").label("Distant Ground");
    model.geom("part4").feature("cyl1").set("contributeto", "csel1");
    model.geom("part4").feature("cyl1").set("r", "r_ground");
    model.geom("part4").feature("cyl1").set("h", "z_nerve");
    model.geom("part4").run();
    model.component("comp1").geom("geom1").lengthUnit("\u00b5m");
    model.component("comp1").geom("geom1").create("pi5", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi5").label("Distant Ground 1");
    model.component("comp1").geom("geom1").feature("pi5").set("part", "part4");
    model.component("comp1").geom("geom1").feature("pi5").setIndex("inputexpr", "z_nerve/2", 0);
    model.component("comp1").geom("geom1").feature("pi5").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepdom", "pi5_csel1.dom", "on");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepbnd", "pi5_csel1.bnd", "on");
    model.component("comp1").geom("geom1").create("pi1", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("inputexpr", "z_center", "z_nerve/2");
    model.component("comp1").geom("geom1").feature("pi1")
         .setEntry("inputexpr", "rotation_angle", "-((theta_cuff-theta_conductor)/2)");
    model.component("comp1").geom("geom1").feature("pi1").set("rot", "zw_rot");
    model.component("comp1").geom("geom1").feature("pi1").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi1").setEntry("selkeepdom", "pi1_csel3.dom", "on");
    model.component("comp1").geom("geom1").create("pi2", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi2").label("Contact 1");
    model.component("comp1").geom("geom1").feature("pi2").set("part", "part2");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("inputexpr", "z_center", "(z_nerve/2)+(pitch/2)");
    model.component("comp1").geom("geom1").feature("pi2")
         .setEntry("inputexpr", "rotation_angle", "(theta_conductor/2)");
    model.component("comp1").geom("geom1").feature("pi2").set("rot", "zw_rot");
    model.component("comp1").geom("geom1").feature("pi2").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi2").setEntry("selkeepdom", "pi2_csel2.dom", "on");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("selkeeppnt", "pi2_csel1.pnt", "on");
    model.component("comp1").geom("geom1").create("pi3", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi3").label("Contact 2");
    model.component("comp1").geom("geom1").feature("pi3").set("part", "part2");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("inputexpr", "z_center", "(z_nerve/2)-(pitch/2)");
    model.component("comp1").geom("geom1").feature("pi3")
         .setEntry("inputexpr", "rotation_angle", "(theta_conductor/2)");
    model.component("comp1").geom("geom1").feature("pi3").set("rot", "zw_rot");
    model.component("comp1").geom("geom1").feature("pi3").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel2.dom", "on");
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeeppnt", "pi3_csel1.pnt", "on");
    model.component("comp1").geom("geom1").create("pi4", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi4").label("Cuff Fill 1");
    model.component("comp1").geom("geom1").feature("pi4").set("part", "part3");
    model.component("comp1").geom("geom1").feature("pi4").setIndex("inputexpr", "(z_nerve/2)", 0);
    model.component("comp1").geom("geom1").feature("pi4").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepdom", "pi4_csel1.dom", "on");
    model.component("comp1").geom("geom1").run();
    model.component("comp1").geom("geom1").run("fin");

    model.view("view6").tag("view61");
    model.view("view4").tag("view6");
    model.view("view7").tag("view71");
    model.view("view5").tag("view7");
    model.view("view61").tag("view5");
    model.view("view71").tag("view4");

    model.component("comp1").material().create("matlnk5", "Link");
    model.component("comp1").material().create("matlnk4", "Link");
    model.component("comp1").material().create("matlnk3", "Link");
    model.component("comp1").material().create("matlnk1", "Link");
    model.material().create("mat1", "Common", "");
    model.material().create("mat2", "Common", "");
    model.material().create("mat3", "Common", "");
    model.material().create("mat4", "Common", "");
    model.component("comp1").material().create("matlnk2", "Link");
    model.component("comp1").material("matlnk5").selection().named("geom1_pi5_csel1_dom");
    model.component("comp1").material("matlnk4").selection().named("geom1_pi4_csel1_dom");
    model.component("comp1").material("matlnk3").selection().named("geom1_pi1_csel3_dom");
    model.component("comp1").material("matlnk1").selection().named("geom1_pi2_csel2_dom");
    model.component("comp1").material("matlnk2").selection().named("geom1_pi3_csel2_dom");

    model.component("comp1").physics().create("ec", "ConductiveMedia", "geom1");
    model.component("comp1").physics("ec").create("pcs1", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs1").selection().named("geom1_pi2_csel1_pnt");
    model.component("comp1").physics("ec").create("pcs2", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs2").selection().named("geom1_pi3_csel1_pnt");
    model.component("comp1").physics("ec").create("gnd1", "Ground", 2);
    model.component("comp1").physics("ec").feature("gnd1").selection().named("geom1_pi5_csel1_bnd");

    model.component("comp1").mesh("mesh1").create("ftet1", "FreeTet");

    model.component("comp1").view("view1").set("renderwireframe", true);
    model.component("comp1").view("view1").set("transparency", true);
    model.view("view3").set("transparency", true);
    model.view("view4").label("View 4.1");
    model.view("view4").axis().set("xmin", -7.289636414498091E-4);
    model.view("view4").axis().set("xmax", 7.289636414498091E-4);
    model.view("view4").axis().set("ymin", -3.20388819091022E-4);
    model.view("view4").axis().set("ymax", 3.228143905289471E-4);
    model.view("view5").label("View 5.1");
    model.view("view5").axis().set("xmin", -5990.36767578125);
    model.view("view5").axis().set("xmax", 5990.36767578125);
    model.view("view5").axis().set("ymin", -4758.78173828125);
    model.view("view5").axis().set("ymax", 4758.78173828125);
    model.view("view6").label("View 6");
    model.view("view7").label("View 7");

    model.component("comp1").material("matlnk5").label("Medium is Muscle");
    model.component("comp1").material("matlnk5").set("link", "mat4");
    model.component("comp1").material("matlnk4").label("Cuff Fill is Saline");
    model.component("comp1").material("matlnk4").set("link", "mat2");
    model.component("comp1").material("matlnk3").label("Cuff is Silicone");
    model.component("comp1").material("matlnk3").set("link", "mat1");
    model.component("comp1").material("matlnk1").label("Conductor 1 is Platinum");
    model.component("comp1").material("matlnk1").set("link", "mat3");
    model.material("mat1").label("Silicone");
    model.material("mat1").propertyGroup("def")
         .set("electricconductivity", new String[]{"10^(-12)", "0", "0", "0", "10^(-12)", "0", "0", "0", "10^(-12)"});
    model.material("mat2").label("Saline");
    model.material("mat2").propertyGroup("def")
         .set("electricconductivity", new String[]{"1.76", "0", "0", "0", "1.76", "0", "0", "0", "1.76"});
    model.material("mat3").label("Platinum");
    model.material("mat3").propertyGroup("def")
         .set("electricconductivity", new String[]{"9.43*10^6", "0", "0", "0", "9.43*10^6", "0", "0", "0", "9.43*10^6"});
    model.material("mat4").label("Muscle");
    model.material("mat4").propertyGroup("def")
         .set("electricconductivity", new String[]{"0.086", "0", "0", "0", "0.086", "0", "0", "0", "0.35"});
    model.component("comp1").material("matlnk2").label("Conductor 2 is Platinum");
    model.component("comp1").material("matlnk2").set("link", "mat3");

    model.component("comp1").physics("ec").feature("pcs1").set("Qjp", 0.001);
    model.component("comp1").physics("ec").feature("pcs2").set("Qjp", -0.001);

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

    model.label("PURDUE_FINAL.mph");

    model.component("comp1").view("view1").set("renderwireframe", false);

    model.label("PURDUE_FINAL.mph");

    return model;
  }

  public static void main(String[] args) {
    run();
  }

}

/*
 * LIVANOVA_FINAL.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Aug 22 2019, 18:08 by COMSOL 5.4.0.388. */
public class LIVANOVA_FINAL {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model.modelPath("D:\\Documents\\ModularCuffs");

    model.label("LIVANOVA_FINAL.mph");

    model.param().set("w_cuff", "1.4 [mm]");
    model.param().set("thk_cuff", "0.9 [mm]");
    model.param().set("w_elec", "0.75 [mm]");
    model.param().set("thk_elec", "0.05 [mm]");
    model.param().set("S", "0.2 [mm]");
    model.param().set("rev_BD", "2.5");
    model.param().set("p", "w_cuff+S");
    model.param().set("sep_elec", "8 [mm]");
    model.param().set("L_cuff", "rev_cuff*p");
    model.param().set("z_nerve", "50 [mm]");
    model.param().set("R_HigherMesh", "4 [mm]");
    model.param().set("r_ground", "5 [mm]");
    model.param().set("scar_thk", "100 [micrometer]");
    model.param().set("d_nerve", "r_nerve*2");
    model.param().set("ID_30220", "2 [mm]");
    model.param().set("ID_30230", "3 [mm]");
    model.param().set("thk_medium_gap_internal", "0");
    model.param()
         .set("rev_cuff", "2.5*((r_nerve+thk_medium_gap_internal)<(ID_30220/2))+((rev_BD)*(sqrt((p^2+pi^2*(ID_cuff+thk_cuff)^2)/(p^2+pi^2*(d_nerve+2*scar_thk+thk_cuff)^2))))*((r_nerve+thk_medium_gap_internal)>=(ID_30220/2))");
    model.param().set("r_nerve", "0.8 [mm]");
    model.param().set("r_cuff_in_pre", "0.5*ID_cuff");
    model.param().set("r_cuff_in", "max(r_nerve+thk_medium_gap_internal,r_cuff_in_pre)");
    model.param()
         .set("ID_cuff", "ID_30220*((r_nerve+thk_medium_gap_internal)<(ID_30230/2))+ID_30230*((r_nerve+thk_medium_gap_internal)>=(ID_30230/2))");
    model.param().set("zw_rot1", "0");
    model.param().set("zw_rot2", "0");

    model.component().create("comp1", true);

    model.component("comp1").geom().create("geom1", 3);

    model.component("comp1").mesh().create("mesh1");

    model.geom().create("part1", "Part", 3);
    model.geom().create("part3", "Part", 3);
    model.geom().create("part4", "Part", 3);
    model.geom("part1").label("Helical Cuff Electrode");
    model.geom("part1").lengthUnit("\u00b5m");
    model.geom("part1").inputParam().set("z_center", "0");
    model.geom("part1").selection().create("csel1", "CumulativeSelection");
    model.geom("part1").selection("csel1").label("PC1");
    model.geom("part1").selection().create("csel2", "CumulativeSelection");
    model.geom("part1").selection("csel2").label("Cuffp1");
    model.geom("part1").selection().create("csel3", "CumulativeSelection");
    model.geom("part1").selection("csel3").label("SEL END P1");
    model.geom("part1").selection().create("csel4", "CumulativeSelection");
    model.geom("part1").selection("csel4").label("PC2");
    model.geom("part1").selection().create("csel10", "CumulativeSelection");
    model.geom("part1").selection("csel10").label("SRC");
    model.geom("part1").selection().create("csel5", "CumulativeSelection");
    model.geom("part1").selection("csel5").label("Cuffp2");
    model.geom("part1").selection().create("csel6", "CumulativeSelection");
    model.geom("part1").selection("csel6").label("Conductorp2");
    model.geom("part1").selection().create("csel7", "CumulativeSelection");
    model.geom("part1").selection("csel7").label("SEL END P2");
    model.geom("part1").selection().create("csel8", "CumulativeSelection");
    model.geom("part1").selection("csel8").label("Cuffp3");
    model.geom("part1").selection().create("csel9", "CumulativeSelection");
    model.geom("part1").selection("csel9").label("PC3");
    model.geom("part1").create("wp1", "WorkPlane");
    model.geom("part1").feature("wp1").label("Helical Insulator Cross Section Part 1");
    model.geom("part1").feature("wp1").set("quickplane", "xz");
    model.geom("part1").feature("wp1").set("unite", true);
    model.geom("part1").feature("wp1").geom().selection().create("csel1", "CumulativeSelection");
    model.geom("part1").feature("wp1").geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION");
    model.geom("part1").feature("wp1").geom().selection().create("csel2", "CumulativeSelection");
    model.geom("part1").feature("wp1").geom().selection("csel2").label("HELICAL INSULATOR CROSS SECTION P1");
    model.geom("part1").feature("wp1").geom().create("r1", "Rectangle");
    model.geom("part1").feature("wp1").geom().feature("r1").label("Helical Insulator Cross Section Part 1");
    model.geom("part1").feature("wp1").geom().feature("r1").set("contributeto", "csel2");
    model.geom("part1").feature("wp1").geom().feature("r1")
         .set("pos", new String[]{"r_cuff_in+(thk_cuff/2)", "z_center-(L_cuff/2)"});
    model.geom("part1").feature("wp1").geom().feature("r1").set("base", "center");
    model.geom("part1").feature("wp1").geom().feature("r1").set("size", new String[]{"thk_cuff", "w_cuff"});
    model.geom("part1").create("pc1", "ParametricCurve");
    model.geom("part1").feature("pc1").label("Parametric Curve Part 1");
    model.geom("part1").feature("pc1").set("contributeto", "csel1");
    model.geom("part1").feature("pc1").set("parmax", "rev_cuff*(0.75/2.5)");
    model.geom("part1").feature("pc1")
         .set("coord", new String[]{"cos(2*pi*s)*((thk_cuff/2)+r_cuff_in)", "sin(2*pi*s)*((thk_cuff/2)+r_cuff_in)", "z_center+(L_cuff)*(s/rev_cuff)-(L_cuff/2)"});
    model.geom("part1").create("swe1", "Sweep");
    model.geom("part1").feature("swe1").label("Make Cuff Part 1");
    model.geom("part1").feature("swe1").set("contributeto", "csel2");
    model.geom("part1").feature("swe1").set("crossfaces", true);
    model.geom("part1").feature("swe1").set("keep", false);
    model.geom("part1").feature("swe1").set("includefinal", false);
    model.geom("part1").feature("swe1").set("twistcomp", false);
    model.geom("part1").feature("swe1").selection("face").named("wp1_csel2");
    model.geom("part1").feature("swe1").selection("edge").named("csel1");
    model.geom("part1").feature("swe1").selection("diredge").set("pc1(1)", 1);
    model.geom("part1").create("ballsel1", "BallSelection");
    model.geom("part1").feature("ballsel1").set("entitydim", 2);
    model.geom("part1").feature("ballsel1").label("Select End Face Part 1");
    model.geom("part1").feature("ballsel1").set("posx", "cos(2*pi*rev_cuff*((0.75)/2.5))*((thk_cuff/2)+r_cuff_in)");
    model.geom("part1").feature("ballsel1").set("posy", "sin(2*pi*rev_cuff*((0.75)/2.5))*((thk_cuff/2)+r_cuff_in)");
    model.geom("part1").feature("ballsel1")
         .set("posz", "z_center+(L_cuff)*(rev_cuff*((0.75)/2.5)/rev_cuff)-(L_cuff/2)");
    model.geom("part1").feature("ballsel1").set("r", 1);
    model.geom("part1").feature("ballsel1").set("contributeto", "csel3");
    model.geom("part1").create("wp2", "WorkPlane");
    model.geom("part1").feature("wp2").label("Helical Insulator Cross Section Part 2");
    model.geom("part1").feature("wp2").set("planetype", "faceparallel");
    model.geom("part1").feature("wp2").set("unite", true);
    model.geom("part1").feature("wp2").selection("face").named("csel3");
    model.geom("part1").feature("wp2").geom().selection().create("csel1", "CumulativeSelection");
    model.geom("part1").feature("wp2").geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION P2");
    model.geom("part1").feature("wp2").geom().selection().create("csel2", "CumulativeSelection");
    model.geom("part1").feature("wp2").geom().selection("csel2").label("HELICAL CONDUCTOR CROSS SECTION P2");
    model.geom("part1").feature("wp2").geom().create("r1", "Rectangle");
    model.geom("part1").feature("wp2").geom().feature("r1").label("Helical Insulator Cross Section Part 2");
    model.geom("part1").feature("wp2").geom().feature("r1").set("contributeto", "csel1");
    model.geom("part1").feature("wp2").geom().feature("r1").set("base", "center");
    model.geom("part1").feature("wp2").geom().feature("r1").set("size", new String[]{"thk_cuff", "w_cuff"});
    model.geom("part1").create("wp3", "WorkPlane");
    model.geom("part1").feature("wp3").label("Helical Conductor Cross Section Part 2");
    model.geom("part1").feature("wp3").set("planetype", "faceparallel");
    model.geom("part1").feature("wp3").set("unite", true);
    model.geom("part1").feature("wp3").selection("face").named("csel3");
    model.geom("part1").feature("wp3").geom().selection().create("csel1", "CumulativeSelection");
    model.geom("part1").feature("wp3").geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION P2");
    model.geom("part1").feature("wp3").geom().selection().create("csel2", "CumulativeSelection");
    model.geom("part1").feature("wp3").geom().selection("csel2").label("HELICAL CONDUCTOR CROSS SECTION P2");
    model.geom("part1").feature("wp3").geom().create("r2", "Rectangle");
    model.geom("part1").feature("wp3").geom().feature("r2").label("Helical Conductor Cross Section Part 2");
    model.geom("part1").feature("wp3").geom().feature("r2").set("contributeto", "csel2");
    model.geom("part1").feature("wp3").geom().feature("r2").set("pos", new String[]{"(thk_elec-thk_cuff)/2", "0"});
    model.geom("part1").feature("wp3").geom().feature("r2").set("base", "center");
    model.geom("part1").feature("wp3").geom().feature("r2").set("size", new String[]{"thk_elec", "w_elec"});
    model.geom("part1").create("pc2", "ParametricCurve");
    model.geom("part1").feature("pc2").label("Parametric Curve Part 2");
    model.geom("part1").feature("pc2").set("contributeto", "csel4");
    model.geom("part1").feature("pc2").set("parmin", "rev_cuff*(0.75/2.5)");
    model.geom("part1").feature("pc2").set("parmax", "rev_cuff*((0.75+1)/2.5)");
    model.geom("part1").feature("pc2")
         .set("coord", new String[]{"cos(2*pi*s)*((thk_cuff/2)+r_cuff_in)", "sin(2*pi*s)*((thk_cuff/2)+r_cuff_in)", "z_center+(L_cuff)*(s/rev_cuff)-(L_cuff/2)"});
    model.geom("part1").create("swe2", "Sweep");
    model.geom("part1").feature("swe2").label("Make Cuff Part 2");
    model.geom("part1").feature("swe2").set("contributeto", "csel5");
    model.geom("part1").feature("swe2").set("crossfaces", true);
    model.geom("part1").feature("swe2").set("includefinal", false);
    model.geom("part1").feature("swe2").set("twistcomp", false);
    model.geom("part1").feature("swe2").selection("face").named("wp2_csel1");
    model.geom("part1").feature("swe2").selection("edge").named("csel4");
    model.geom("part1").feature("swe2").selection("diredge").set("pc2(1)", 1);
    model.geom("part1").create("swe3", "Sweep");
    model.geom("part1").feature("swe3").label("Make Conductor Part 2");
    model.geom("part1").feature("swe3").set("contributeto", "csel6");
    model.geom("part1").feature("swe3").set("crossfaces", true);
    model.geom("part1").feature("swe3").set("includefinal", false);
    model.geom("part1").feature("swe3").set("twistcomp", false);
    model.geom("part1").feature("swe3").selection("face").named("wp3_csel2");
    model.geom("part1").feature("swe3").selection("edge").named("csel4");
    model.geom("part1").feature("swe3").selection("diredge").set("pc2(1)", 1);
    model.geom("part1").create("ballsel2", "BallSelection");
    model.geom("part1").feature("ballsel2").set("entitydim", 2);
    model.geom("part1").feature("ballsel2").label("Select End Face Part 2");
    model.geom("part1").feature("ballsel2")
         .set("posx", "cos(2*pi*rev_cuff*((0.75+1)/2.5))*((thk_cuff/2)+r_cuff_in)");
    model.geom("part1").feature("ballsel2")
         .set("posy", "sin(2*pi*rev_cuff*((0.75+1)/2.5))*((thk_cuff/2)+r_cuff_in)");
    model.geom("part1").feature("ballsel2")
         .set("posz", "z_center+(L_cuff)*(rev_cuff*((0.75+1)/2.5)/rev_cuff)-(L_cuff/2)");
    model.geom("part1").feature("ballsel2").set("r", 1);
    model.geom("part1").feature("ballsel2").set("contributeto", "csel7");
    model.geom("part1").create("wp4", "WorkPlane");
    model.geom("part1").feature("wp4").label("Helical Insulator Cross Section Part 3");
    model.geom("part1").feature("wp4").set("planetype", "faceparallel");
    model.geom("part1").feature("wp4").set("unite", true);
    model.geom("part1").feature("wp4").selection("face").named("csel7");
    model.geom("part1").feature("wp4").geom().selection().create("csel1", "CumulativeSelection");
    model.geom("part1").feature("wp4").geom().selection("csel1").label("HELICAL INSULATOR CROSS SECTION P3");
    model.geom("part1").feature("wp4").geom().create("r1", "Rectangle");
    model.geom("part1").feature("wp4").geom().feature("r1").label("Helical Insulator Cross Section Part 3");
    model.geom("part1").feature("wp4").geom().feature("r1").set("contributeto", "csel1");
    model.geom("part1").feature("wp4").geom().feature("r1").set("base", "center");
    model.geom("part1").feature("wp4").geom().feature("r1").set("size", new String[]{"thk_cuff", "w_cuff"});
    model.geom("part1").create("pc3", "ParametricCurve");
    model.geom("part1").feature("pc3").label("Parametric Curve Part 3");
    model.geom("part1").feature("pc3").set("contributeto", "csel9");
    model.geom("part1").feature("pc3").set("parmin", "rev_cuff*((0.75+1)/2.5)");
    model.geom("part1").feature("pc3").set("parmax", "rev_cuff");
    model.geom("part1").feature("pc3")
         .set("coord", new String[]{"cos(2*pi*s)*((thk_cuff/2)+r_cuff_in)", "sin(2*pi*s)*((thk_cuff/2)+r_cuff_in)", "z_center+(L_cuff)*(s/rev_cuff)-(L_cuff/2)"});
    model.geom("part1").create("swe4", "Sweep");
    model.geom("part1").feature("swe4").label("Make Cuff Part 3");
    model.geom("part1").feature("swe4").set("contributeto", "csel8");
    model.geom("part1").feature("swe4").set("crossfaces", true);
    model.geom("part1").feature("swe4").set("includefinal", false);
    model.geom("part1").feature("swe4").set("twistcomp", false);
    model.geom("part1").feature("swe4").selection("face").named("wp4_csel1");
    model.geom("part1").feature("swe4").selection("edge").named("csel9");
    model.geom("part1").feature("swe4").selection("diredge").set("pc3(1)", 1);
    model.geom("part1").create("pt1", "Point");
    model.geom("part1").feature("pt1").label("src");
    model.geom("part1").feature("pt1").set("contributeto", "csel10");
    model.geom("part1").feature("pt1")
         .set("p", new String[]{"cos(2*pi*rev_cuff*(1.25/2.5))*((thk_elec/2)+r_cuff_in)", "sin(2*pi*rev_cuff*(1.25/2.5))*((thk_elec/2)+r_cuff_in)", "z_center"});
    model.geom("part1").run();
    model.geom("part3").label("Electrode Fill");
    model.geom("part3").inputParam().set("z_center", "0");
    model.geom("part3").selection().create("csel1", "CumulativeSelection");
    model.geom("part3").selection("csel1").label("CUFF FILL");
    model.geom("part3").create("cyl1", "Cylinder");
    model.geom("part3").feature("cyl1").label("Cuff Fill");
    model.geom("part3").feature("cyl1").set("contributeto", "csel1");
    model.geom("part3").feature("cyl1").set("pos", new String[]{"0", "0", "z_center"});
    model.geom("part3").feature("cyl1").set("r", "r_cuff_in+thk_cuff+scar_thk");
    model.geom("part3").feature("cyl1").set("h", "L_cuff+w_cuff+2*scar_thk");
    model.geom("part3").run();
    model.geom("part4").label("Distant Ground");
    model.geom("part4").selection().create("csel1", "CumulativeSelection");
    model.geom("part4").selection("csel1").label("DISTANT GROUND");
    model.geom("part4").create("cyl1", "Cylinder");
    model.geom("part4").feature("cyl1").label("Distant Ground");
    model.geom("part4").feature("cyl1").set("contributeto", "csel1");
    model.geom("part4").feature("cyl1").set("r", "r_ground");
    model.geom("part4").feature("cyl1").set("h", "z_nerve");
    model.geom("part4").run();
    model.component("comp1").geom("geom1").create("pi5", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi5").label("Distant Ground 1");
    model.component("comp1").geom("geom1").feature("pi5").set("part", "part4");
    model.component("comp1").geom("geom1").feature("pi5").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepdom", "pi5_csel1.dom", "on");
    model.component("comp1").geom("geom1").feature("pi5").setEntry("selkeepbnd", "pi5_csel1.bnd", "on");
    model.component("comp1").geom("geom1").create("pi1", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi1").label("Helical Silicone 1");
    model.component("comp1").geom("geom1").feature("pi1").setIndex("inputexpr", "(z_nerve/2)-(sep_elec/2)", 0);
    model.component("comp1").geom("geom1").feature("pi1").set("rot", "zw_rot1");
    model.component("comp1").geom("geom1").feature("pi1").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi1").setEntry("selkeepdom", "pi1_csel2.dom", "on");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("selkeepdom", "pi1_csel5.dom", "on");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("selkeepdom", "pi1_csel6.dom", "on");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("selkeepdom", "pi1_csel8.dom", "on");
    model.component("comp1").geom("geom1").feature("pi1").setEntry("selkeeppnt", "pi1_csel10.pnt", "on");
    model.component("comp1").geom("geom1").create("pi2", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi2").label("Helical Silicone 2");
    model.component("comp1").geom("geom1").feature("pi2").setIndex("inputexpr", "(z_nerve/2)+(sep_elec/2)", 0);
    model.component("comp1").geom("geom1").feature("pi2").set("rot", "zw_rot2");
    model.component("comp1").geom("geom1").feature("pi2").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi2").setEntry("selkeepdom", "pi2_csel2.dom", "on");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("selkeepdom", "pi2_csel5.dom", "on");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("selkeepdom", "pi2_csel6.dom", "on");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("selkeepdom", "pi2_csel8.dom", "on");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("selkeepdom", "pi2_csel10.dom", "on");
    model.component("comp1").geom("geom1").feature("pi2").setEntry("selkeeppnt", "pi2_csel10.pnt", "on");
    model.component("comp1").geom("geom1").create("pi3", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi3").label("Electrode Fill 1");
    model.component("comp1").geom("geom1").feature("pi3").set("part", "part3");
    model.component("comp1").geom("geom1").feature("pi3")
         .setIndex("inputexpr", "(z_nerve/2)-(sep_elec/2)-(L_cuff/2)-(w_cuff/2)-scar_thk", 0);
    model.component("comp1").geom("geom1").feature("pi3").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi3").setEntry("selkeepdom", "pi3_csel1.dom", "on");
    model.component("comp1").geom("geom1").create("pi4", "PartInstance");
    model.component("comp1").geom("geom1").feature("pi4").label("Electrode Fill 2");
    model.component("comp1").geom("geom1").feature("pi4").set("part", "part3");
    model.component("comp1").geom("geom1").feature("pi4")
         .setIndex("inputexpr", "(z_nerve/2)+(sep_elec/2)-(L_cuff/2)-(w_cuff/2)-scar_thk", 0);
    model.component("comp1").geom("geom1").feature("pi4").set("selkeepnoncontr", false);
    model.component("comp1").geom("geom1").feature("pi4").setEntry("selkeepdom", "pi4_csel1.dom", "on");
    model.component("comp1").geom("geom1").run();
    model.component("comp1").geom("geom1").run("fin");

    model.view("view4").tag("view41");
    model.view("view3").tag("view4");
    model.view("view5").tag("view51");
    model.view("view41").tag("view5");
    model.view("view6").tag("view61");
    model.view("view51").tag("view6");
    model.view("view61").tag("view9");
    model.view("view7").tag("view10");
    model.view("view8").tag("view11");

    model.component("comp1").material().create("matlnk11", "Link");
    model.component("comp1").material().create("matlnk9", "Link");
    model.component("comp1").material().create("matlnk10", "Link");
    model.material().create("mat1", "Common", "");
    model.material().create("mat2", "Common", "");
    model.component("comp1").material().create("matlnk1", "Link");
    model.component("comp1").material().create("matlnk3", "Link");
    model.component("comp1").material().create("matlnk4", "Link");
    model.component("comp1").material().create("matlnk2", "Link");
    model.component("comp1").material().create("matlnk5", "Link");
    model.component("comp1").material().create("matlnk6", "Link");
    model.component("comp1").material().create("matlnk7", "Link");
    model.component("comp1").material().create("matlnk8", "Link");
    model.material().create("mat3", "Common", "");
    model.material().create("mat4", "Common", "");
    model.component("comp1").material("matlnk11").selection().named("geom1_pi5_csel1_dom");
    model.component("comp1").material("matlnk9").selection().named("geom1_pi3_csel1_dom");
    model.component("comp1").material("matlnk10").selection().named("geom1_pi4_csel1_dom");
    model.component("comp1").material("matlnk1").selection().named("geom1_pi1_csel2_dom");
    model.component("comp1").material("matlnk3").selection().named("geom1_pi1_csel5_dom");
    model.component("comp1").material("matlnk4").selection().named("geom1_pi1_csel8_dom");
    model.component("comp1").material("matlnk2").selection().named("geom1_pi1_csel6_dom");
    model.component("comp1").material("matlnk5").selection().named("geom1_pi2_csel2_dom");
    model.component("comp1").material("matlnk6").selection().named("geom1_pi2_csel5_dom");
    model.component("comp1").material("matlnk7").selection().named("geom1_pi2_csel8_dom");
    model.component("comp1").material("matlnk8").selection().named("geom1_pi2_csel6_dom");

    model.component("comp1").physics().create("ec", "ConductiveMedia", "geom1");
    model.component("comp1").physics("ec").create("pcs1", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs1").selection().named("geom1_pi1_csel10_pnt");
    model.component("comp1").physics("ec").create("pcs2", "PointCurrentSource", 0);
    model.component("comp1").physics("ec").feature("pcs2").selection().named("geom1_pi2_csel10_pnt");
    model.component("comp1").physics("ec").create("gnd1", "Ground", 2);
    model.component("comp1").physics("ec").feature("gnd1").selection().named("geom1_pi5_csel1_bnd");

    model.component("comp1").mesh("mesh1").create("ftet1", "FreeTet");

    model.component("comp1").view("view1").set("transparency", true);
    model.view("view2").set("transparency", true);
    model.view("view4").label("View 4.1");
    model.view("view5").label("View 5.1");
    model.view("view6").label("View 6.1");
    model.view("view6").axis().set("xmin", -3728.476806640625);
    model.view("view6").axis().set("xmax", 3728.421142578125);
    model.view("view6").axis().set("ymin", -2835.000732421875);
    model.view("view6").axis().set("ymax", 2835.036865234375);
    model.view("view9").label("View 9");
    model.view("view9").axis().set("xmin", -0.003956920932978392);
    model.view("view9").axis().set("xmax", 0.0010691271163523197);
    model.view("view9").axis().set("ymin", -0.0023950841277837753);
    model.view("view9").axis().set("ymax", 0.0015976362628862262);
    model.view("view10").label("View 10");
    model.view("view10").axis().set("xmin", -1.2814021110534668);
    model.view("view10").axis().set("xmax", 1.2813220024108887);
    model.view("view10").axis().set("ymin", -1.0187280178070068);
    model.view("view10").axis().set("ymax", 1.0171141624450684);
    model.view("view11").label("View 11");
    model.view("view11").axis().set("xmin", -0.004172593355178833);
    model.view("view11").axis().set("xmax", 0.001284637488424778);
    model.view("view11").axis().set("ymin", -0.0010165583807975054);
    model.view("view11").axis().set("ymax", 0.003318695817142725);

    model.component("comp1").material("matlnk11").label("Medium is Muscle");
    model.component("comp1").material("matlnk11").set("link", "mat4");
    model.component("comp1").material("matlnk9").label("CuffFill1 is Scar");
    model.component("comp1").material("matlnk9").set("link", "mat3");
    model.component("comp1").material("matlnk10").label("CuffFill2 is Scar");
    model.component("comp1").material("matlnk10").set("link", "mat3");
    model.material("mat1").label("Silicone");
    model.material("mat1").propertyGroup("def")
         .set("electricconductivity", new String[]{"10^(-12)", "0", "0", "0", "10^(-12)", "0", "0", "0", "10^(-12)"});
    model.material("mat2").label("Platinum");
    model.material("mat2").propertyGroup("def")
         .set("electricconductivity", new String[]{"9.43*10^6", "0", "0", "0", "9.43*10^6", "0", "0", "0", "9.43*10^6"});
    model.component("comp1").material("matlnk1").label("Cuff1p1 is Silicone");
    model.component("comp1").material("matlnk3").label("Cuff1p2 is Silicone");
    model.component("comp1").material("matlnk4").label("Cuff1p3 is Silicone");
    model.component("comp1").material("matlnk2").label("Conductor1p2 is Platinum");
    model.component("comp1").material("matlnk2").set("link", "mat2");
    model.component("comp1").material("matlnk5").label("Cuff2p1 is Silicone 1");
    model.component("comp1").material("matlnk6").label("Cuff1p2 is Silicone 1");
    model.component("comp1").material("matlnk7").label("Cuff1p3 is Silicone 1");
    model.component("comp1").material("matlnk8").label("Conductor1p2 is Platinum 1");
    model.component("comp1").material("matlnk8").set("link", "mat2");
    model.material("mat3").label("Scar");
    model.material("mat3").propertyGroup("def")
         .set("electricconductivity", new String[]{"0.15873", "0", "0", "0", "0.15873", "0", "0", "0", "0.15873"});
    model.material("mat4").label("Muscle");
    model.material("mat4").propertyGroup("def")
         .set("electricconductivity", new String[]{"0.086", "0", "0", "0", "0.086", "0", "0", "0", "0.35"});

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

    model.label("LIVANOVA_FINAL.mph");

    return model;
  }

  public static void main(String[] args) {
    run();
  }

}

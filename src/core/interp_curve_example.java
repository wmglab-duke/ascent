/*
 * interp_curve_example.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

public class interp_curve_example {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model.modelPath("D:\\Documents\\access\\src\\core");

    model.label("interp_curve_example.mph");

    model.component().create("comp1", true);

    model.component("comp1").geom().create("geom1", 3);
    model.component("comp1").mesh().create("mesh1");

    model.component("comp1").geom("geom1").lengthUnit("\u00b5m");
    model.component("comp1").geom("geom1").selection().create("csel4", "CumulativeSelection");
    model.component("comp1").geom("geom1").selection("csel4").label("Nerve");

    model.component("comp1").geom("geom1").create("ic4", "InterpolationCurve");
    model.component("comp1").geom("geom1").feature("ic4").label("306 Nerve");
    model.component("comp1").geom("geom1").feature("ic4").set("contributeto", "csel4");
    model.component("comp1").geom("geom1").feature("ic4").set("type", "closed");
    model.component("comp1").geom("geom1").feature("ic4").set("source", "file");
    model.component("comp1").geom("geom1").feature("ic4").set("filename", "C:\\Users\\edm23\\Downloads\\1.txt");
    model.component("comp1").geom("geom1").feature("ic4").set("struct", "sectionwise");
    model.component("comp1").geom("geom1").feature("ic4").set("rtol", 0.005);

    model.component("comp1").geom("geom1").run();

    model.component("comp1").physics().create("ec", "ConductiveMedia", "geom1");

    model.common("cminpt").label("Common model inputs 1");

    model.component("comp1").physics("ec").prop("MeshControl").set("EnableMeshControl", false);

    model.study().create("std1");
    model.study("std1").create("stat", "Stationary");

    return model;
  }

  public static void main(String[] args) {
    run();
  }

}

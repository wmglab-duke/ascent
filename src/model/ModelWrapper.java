package model;

import com.comsol.model.*;
import com.comsol.model.physics.PhysicsFeature;
import com.comsol.model.util.ModelUtil;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Objects;

/**
 * model.ModelWrapper
 *
 * Master high-level class for managing a model, its metadata, and various critical operations such as creating parts
 * and extracting potentials. This class houses the "meaty" operations of actually interacting with the model object
 * when creating parts in the static class model.Parts.
 */
public class ModelWrapper {


    // UNION pseudonym constants
    public static final String ALL_NERVE_PARTS_UNION = "allNervePartsUnion";
    public static final String ENDO_UNION = "endoUnion";
    public static final String PERI_UNION = "periUnion";

    public static final String[] ALL_UNIONS = new String[]{
            ModelWrapper.ENDO_UNION,
            ModelWrapper.ALL_NERVE_PARTS_UNION,
            ModelWrapper.PERI_UNION
    };

    // associated union contributors for above constants
    private HashMap<String, ArrayList<String>> unionContributors = new HashMap<>();

    // INSTANCE VARIABLES

    // model
    private Model model;

    // top level identifier manager
    public IdentifierManager im = new IdentifierManager();

    // managing parts within COMSOL
    private HashMap<String, IdentifierManager> partPrimitiveIMs = new HashMap<>();

    // directory structure
    private String root;
    private String dest;


    // CONSTRUCTORS

    /**
     * Default constructor (minimum of 2 arguments)
     * @param model com.comsol.model.Model object is REQUIRED
     * @param projectRoot the root directory of the project (might remove if unnecessary)
     */
    ModelWrapper(Model model, String projectRoot) {
        this.model = model;
        this.root = projectRoot;
        this.initUnionContributors();
    }

    /**
     * Overloaded constructor for passing in save directory
     * @param model com.comsol.model.Model object is REQUIRED
     * @param projectRoot the root directory of the project (might remove if unnecessary)
     * @param defaultSaveDestination directory in which to save (relative to project root)
     */
    ModelWrapper(Model model, String projectRoot, String defaultSaveDestination) {
        this(model, projectRoot);
        this.dest = defaultSaveDestination;
    }


    // ACCESSOR/MUTATOR METHODS

    /**
     * @return the model
     */
    public Model getModel() {
        return model;
    }

    /**
     * @return the root of the project (String path)
     */
    public String getRoot() {
        return root;
    }

    /**
     * @return the destination path to which to save the model
     */
    public String getDest() {
        return dest;
    }

    /**
     * @param root set the project root (String path)
     */
    public void setRoot(String root) {
        this.root = root;
    }

    /**
     * @param dest set the destination path to which to save the model
     */
    public void setDest(String dest) {
        this.dest = dest;
    }

    // OTHER METHODS

    /**
     * call method on im (IdentifierManager)... see class for details
     */
    public String next(String key) {
        return this.im.next(key);
    }

    /**
     * call method on im (IdentifierManager)... see class for details
     */
    public String next(String key, String pseudonym) {
        return this.im.next(key, pseudonym);
    }

    /**
     * call method on im (IdentifierManager)... see class for details
     */
    public String get(String psuedonym) {
        return this.im.get(psuedonym);
    }

    /**
     * @param partPrimitiveLabel the name of the part primitive (i.e. "TubeCuff_Primitive")
     * @return the associated IdentifierManager, for correct intra-part indexing
     */
    public IdentifierManager getPartPrimitiveIM(String partPrimitiveLabel) {
        return this.partPrimitiveIMs.get(partPrimitiveLabel);
    }

    /**
     * @param destination full path to save to
     * @return success indicator
     */
    public boolean save(String destination) {
        try {
            this.model.save(destination);
            return true;
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
    }

    /**
     * Convenience method for saving to relative directory (this.dest) wrt the project directory (root)
     * @return success indicator
     */
    public boolean save() {
        if (this.dest != null) return save(String.join("/", new String[]{this.root, this.dest}));
        else {
            System.out.println("Save directory not initialized");
            return false;
        }
    }

    /**
     * Create the required primitives for a given cuff json
     * @param name json filename WITH extension (i.e. "LivaNova.json")
     * @return success indicator
     */
    public boolean addCuffPartPrimitives(String name) {
        // extract data from json
        try {
            JSONObject data = new JSONReader(String.join("/",
                    new String[]{this.root, "config", "system", "cuffs", name})).getData();

            // get the id for the next "par" (i.e. parameters section), and give it a name from the JSON file name
            String id = this.next("par", name);
            model.param().group().create(id);
            model.param(id).label(name.split("\\.")[0] + " Parameters");

            // loop through all parameters in file, and set in parameters
            for (Object item : (JSONArray) data.get("params")) {
                JSONObject itemObject = (JSONObject) item;

                model.param(id).set(
                        (String) itemObject.get("name"),
                        (String) itemObject.get("expression"),
                        (String) itemObject.get("description")
                );
            }

            // for each required part primitive, create it (if not already existing)
            for (Object item: (JSONArray) data.get("instances")) {
                JSONObject itemObject = (JSONObject) item;
                String partPrimitiveName = (String) itemObject.get("type"); // quick cast to String

                // create the part primitive if it has not already been created
                if (! this.im.hasPseudonym(partPrimitiveName)) {
                    // get next available (TOP LEVEL) "part" id
                    String partID = this.im.next("part", partPrimitiveName);
                    try {
                        // TRY to create the part primitive (catch error if no existing implementation)
                        IdentifierManager partPrimitiveIM = Part.createCuffPartPrimitive(partID, partPrimitiveName, this);

                        // add the returned id manager to the HashMap of IMs with the partName as its key
                        this.partPrimitiveIMs.put(partPrimitiveName, partPrimitiveIM);

                    } catch (IllegalArgumentException e) {
                        e.printStackTrace();
                        return false;

                    }
                }
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
            return false;
        }
        return true;
    }

    /**
     * Instantiate required primitives for given cuff
     * NOTE: addCuffPartPrimitives() MUST be called first or there will be no primitives to instantiate
     * @param name same formatting as in addCuffPartPrimitives()
     * @param modelData
     * @return success indicator
     */
    public boolean addCuffPartInstances(String name, JSONObject modelData) {
        // extract data from json
        // name is something like Enteromedics.json
        try {
            JSONObject data = new JSONReader(String.join("/",
                    new String[]{this.root, "config", "system", "cuffs", name})).getData();

            // loop through all part instances
            for (Object item: (JSONArray) data.get("instances")) {
                JSONObject itemObject = (JSONObject) item;

                String instanceLabel = (String) itemObject.get("label");
                String instanceID = this.im.next("pi", instanceLabel);
                String type = (String) itemObject.get("type");
                Part.createCuffPartInstance(instanceID, instanceLabel, type , this, itemObject, modelData);
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
            return false;
        }
        return true;

    }

    /**
     * TODO
     */
    public boolean addCuffPartMaterialAssignments(JSONObject cuffData) {
        // extract data from json
        // name is something like Enteromedics.json
        // loop through all part instances
        for (Object item: (JSONArray) cuffData.get("instances")) {
            JSONObject itemObject = (JSONObject) item;

            String instanceLabel = (String) itemObject.get("label");
            String type = (String) itemObject.get("type");
            Part.addCuffPartMaterialAssignment(instanceLabel, type, this, itemObject);
        }
        return true;

    }

    /**
     * Create materials necessary for fascicles, nerve, surrounding media, etc. --- always called!
     * @return success indicator
     */
    public boolean addMaterialDefinitions(ArrayList<String> materials, JSONObject modelData, ModelParamGroup materialParams) {
        // extract data from json
        try {
            JSONObject materialsData = new JSONReader(String.join("/",
                    new String[]{this.root, "config", "system", "materials.json"})).getData();

            for (String function:materials) {
                if (! this.im.hasPseudonym(function)) {
                    String materialID = this.im.next("mat", function);
                    Part.defineMaterial(materialID, function, modelData, materialsData, this, materialParams);
                }
            }

        } catch (FileNotFoundException e) {
            e.printStackTrace();
            return false;
        }
        return true;
    }

    /**
     * TODO: UNFINISHED!!!!
     * @param json_path to output from fiber_manager.py (see TEST_JSON_OUTPUT.json if exists)
     * @return success indicator
     */
    public boolean extractPotentials(String json_path) {

        // see todos below (unrelated to this method hahahah - HILARIOUS! ROFL!)
        // TODO: Simulation folders; sorting through configuration files VIA PYTHON
        // TODO: FORCE THE USER TO STAGE/COMMIT CHANGES BEFORE RUNNING; add Git Commit ID/number to config file
        try {
            JSONObject json_data = new JSONReader(String.join("/", new String[]{root, json_path})).getData();

            double[][] coordinates = new double[3][5];
            String id = this.next("interp");

            model.result().numerical().create(id, "Interp");
            model.result().numerical(id).set("expr", "V");
            model.result().numerical(id).setInterpolationCoordinates(coordinates);

            double[][][] data = model.result().numerical(id).getData();

            System.out.println("data.toString() = " + Arrays.deepToString(data));
        } catch (FileNotFoundException e) {
            e.printStackTrace();
            return false;
        }

        return true;
    }

    /**
     * Add all fascicles to model.
     * TODO: finish implementation of meshing in the Part class
     * @return success indicator
     */
    public boolean addNerve(String sample, ModelParamGroup nerveParams) {

        // define global nerve part names (MUST BE IDENTICAL IN Part)
        String[] fascicleTypes = new String[]{"FascicleCI", "FascicleMesh"};

        // Load configuration file
        try {
            JSONObject sampleData = new JSONReader(String.join("/", new String[]{
                    this.root,
                    "samples",
                    sample,
                    "sample.json"
            })).getData();

            // Build path to fascicles
            String fasciclesPath = String.join("/", new String[]{
                    this.root,
                    "samples",
                    sample,
                    "slides",
                    "0", // these 0's are temporary (for 3d models will need to change)
                    "0",
                    (String) ((JSONObject) sampleData.get("modes")).get("write"),
                    "fascicles"
            });

            // Add epineurium
            String nerveMode = (String) sampleData.getJSONObject("modes").get("nerve");
            if (nerveMode.equals("PRESENT")) {
                Part.createNervePartInstance("Epineurium", 0,
                        null, this, null, sampleData, nerveParams);
            }

            // Loop over all fascicle dirs
            String[] dirs = new File(fasciclesPath).list();
            if (dirs != null) {
                for (String dir: dirs) {
                    if (! dir.contains(".")) {
                        int index = Integer.parseInt(dir);
                        // Initialize data to send to Part.createPartInstance
                        HashMap<String, String[]> data = new HashMap<>();

                        // Add inners and outer files to array
                        String path = String.join("/", new String[]{fasciclesPath, dir});
                        for (String type: new String[]{"inners", "outer"}) {
                            data.put(type,
                                    new File(
                                            String.join("/", new String[]{path, type})
                                    ).list()
                            );
                        }

                        // Quick loop to make sure there are at least one of each inner and outer
                        for (String[] arr: data.values()) {
                            if (arr.length < 1) throw new IllegalStateException("There must be at least one of each inner and outer for fascicle " + index);
                        }

                        // do FascicleCI if only one inner, FascicleMesh otherwise
                        String fascicleType = data.get("inners").length == 1 ? fascicleTypes[0] : fascicleTypes[1];

                        // hand off to Part to build instance of fascicle
                        Part.createNervePartInstance(fascicleType, index, path, this, data, sampleData, nerveParams);

                    }
                }
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();

        }

        return true;
    }

    /**
     * Pre-built for-loop to iterate through all current sources in model (added in Part)
     * Can be super useful for quickly setting different currents and possibly sweeping currents
     */
    public void loopCurrents(JSONObject modelData, String projectPath, String sample, String modelStr) {

        long runSolStartTime = System.nanoTime();
        for(String key_on: this.im.currentPointers.keySet()) {

            System.out.println("Current pointer: " + key_on);

            PhysicsFeature current_on = (PhysicsFeature) this.im.currentPointers.get(key_on);
            String src = current_on.tag();
            current_on.set("Qjp", 0.001); // turn on current

            model.sol("sol1").runAll();

            String mphFile = String.join("/", new String[]{
                    projectPath,
                    "samples",
                    sample,
                    "models",
                    modelStr,
                    "bases",
                    src + ".mph"
            });

            try {
                System.out.println("Saving MPH (mesh and solution) file to: " + mphFile);
                model.save(mphFile);
            } catch (IOException e) {
                e.printStackTrace();
            }

            current_on.set("Qjp", 0.000); // reset current

        }

        JSONObject solution = modelData.getJSONObject("solution");
        long estimatedRunSolTime = System.nanoTime() - runSolStartTime;
        solution.put("sol_time", estimatedRunSolTime/Math.pow(10,6)); // convert nanos to millis
        solution.put("time_units", "ms"); // convert nanos to millis
        modelData.put("solution", solution);
    }

    /**
     * Call only from initializer!
     * Initialize the ArrayLists in the unionContributors HashMap
     */
    public void initUnionContributors() {
        for(String unionLabel : ModelWrapper.ALL_UNIONS) {
            this.unionContributors.put(unionLabel, new ArrayList<>());
        }
    }

    /**
     * Add string id for COMSOL element to the listed unions (which have not be "created" in COMSOL yet)
     * @param contributor the string id to add (use actual id, not pseudonym)
     * @param unions which unions to add it to  (use static pseudonym constants at top of class)
     */
    public void contributeToUnions(String contributor, String[] unions) {
        for (String union: unions) {
            this.unionContributors.get(union).add(contributor);
        }
    }

    /**
     * @param union which union to from of which to get the contributors
     * @return String array of the COMSOL id's of contributors (likely ext# or csel#)
     */
    public String[] getUnionContributors(String union) {
        if (! this.unionContributors.containsKey(union)) throw new IllegalArgumentException("No such union: " + union);
        return this.unionContributors.get(union).toArray(new String[0]);
    }

    /**
     * Actually create the unions by looping through all defined ArrayLists and adding contents to a new union.
     * Will not create a union of no elements in associated ArrayList (i.e. no Peri union if only contact impedance)
     */
    public void createUnions() {
        for (String union: ModelWrapper.ALL_UNIONS) {
            String[] contributors = this.getUnionContributors(union);

            if (contributors.length > 0) {
                model.component("comp1").geom("geom1").create(im.next("uni", union), "Union");

                model.component("comp1").geom("geom1").feature(im.get(union)).set("keep", true);
                model.component("comp1").geom("geom1").feature(im.get(union)).selection("input").set(contributors);
                model.component("comp1").geom("geom1").feature(im.get(union)).label(union);

                String unionCselLabel = union + "Csel";
                model.component("comp1").geom("geom1").selection().create(im.next("csel",unionCselLabel), "CumulativeSelection");
                model.component("comp1").geom("geom1").selection(im.get(unionCselLabel)).label(unionCselLabel);
                model.component("comp1").geom("geom1").feature(im.get(union)).set("contributeto", im.get(unionCselLabel));

            }
        }
    }

    /**
     * Master procedure to run!
     * @param args
     */
    public static void main(String[] args) throws FileNotFoundException {

        // Take projectPath input to ModelWrapper and assign to string.
        String projectPath = args[0];

        // Take runPath input to ModelWrapper and assign to string
        String runPath = args[1];

        // Start COMSOL Instance
        ModelUtil.connect("localhost", 2036);
        ModelUtil.initStandalone(false);
//        ModelUtil.showProgress(null); // if you want to see COMSOL progress (as it makes all geometry, runs, etc.)

        // Load RUN configuration data
        JSONObject run = null;
        try {
            run = new JSONReader(runPath).getData();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

        // Load SAMPLE configuration data
        String sample = String.valueOf(Objects.requireNonNull(run).getInt("sample"));

        String sampleFile = String.join("/", new String[]{
                "samples",
                sample,
                "sample.json"
        });

        JSONObject sampleData = null;
        try {
            sampleData = new JSONReader(projectPath + "/" + sampleFile).getData();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

        JSONArray models_list = run.getJSONArray("models");

        // loop models
        for (int model_index = 0; model_index < models_list.length(); model_index++) {
            System.out.println("Making model index: " + model_index);
            String modelStr = String.valueOf(models_list.get(model_index));

            // Load MODEL configuration data
            String modelFile = String.join("/", new String[]{
                    "samples",
                    sample,
                    "models",
                    modelStr,
                    "model.json"
            });

            JSONObject modelData = null;
            try {
                modelData = new JSONReader(projectPath + "/" + modelFile).getData();
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            }

            // TODO: insert optimization logic here
            /* pseudo-code

            if optimizing:
                if prev is not null AND prev is mesh match:

                    current model config = prev model config (copy unnecessary)
                    current mph = prev mph COPY
                    current IDM = prev IDM COPY

                    skip mesh = true

                else:
                    search via recursive dir dive:

                        if no mesh match:

                            skip mesh = false

                        else: (found mesh match)

                            current model config = found model config
                            current mph = found mesh mph
                            current IDM = found mesh IDM

                            prev model config = found model config (copy unnecessary)
                            prev mph = found mesh COPY
                            prev IDM = found mesh IDM COPY



             */

            // Define model object
            Model model = ModelUtil.create("Model");
            // Add component node 1
            model.component().create("comp1", true);
            // Add 3D geom to component node 1
            model.component("comp1").geom().create("geom1", 3);
            // Set default length units to micron
            model.component("comp1").geom("geom1").lengthUnit("\u00b5m");
            // Add materials node to component node 1
            model.component("comp1").physics().create("ec", "ConductiveMedia", "geom1");
            // and mesh node to component node 1
            model.component("comp1").mesh().create("mesh1");

            // Define ModelWrapper class instance for model and projectPath
            ModelWrapper mw = new ModelWrapper(model, projectPath);

            // FEM MODEL GEOMETRY
            // Set NERVE MORPHOLOGY parameters
            JSONObject morphology = (JSONObject) sampleData.get("Morphology");
            String morphology_unit = ((JSONObject) sampleData.get("scale")).getString("scale_bar_unit");

            String nerveParamsLabal = "Nerve Parameters";
            ModelParamGroup nerveParams = model.param().group().create(nerveParamsLabal);
            nerveParams.label(nerveParamsLabal);

            if (morphology.isNull("Nerve")) {
                nerveParams.set("a_nerve", "NaN");
                nerveParams.set("r_nerve", "NaN");
            } else {
                JSONObject nerve = (JSONObject) morphology.get("Nerve");
                nerveParams.set("a_nerve", nerve.get("area") + " [" + morphology_unit + "^2]");
                nerveParams.set("r_nerve", "sqrt(a_nerve/pi)");
            }

            JSONObject CICoeffs = modelData.getJSONObject("ci_perineurium_thickness").getJSONObject("coefficients");
            nerveParams.set("ci_a", CICoeffs.getDouble("a") + " [" + CICoeffs.getString("unit") + "/" + CICoeffs.getString("unit") + "]");
            nerveParams.set("ci_b", CICoeffs.getDouble("b") + " [" + CICoeffs.getString("unit") + "]");

            // Set CUFF POSITIONING parameters
            String cuffConformationParamsLabel = "Cuff Conformation Parameters";
            ModelParamGroup cuffConformationParams = model.param().group().create(cuffConformationParamsLabel);
            cuffConformationParams.label(cuffConformationParamsLabel);

            String cuff_shift_unit = modelData.getJSONObject("cuff").getJSONObject("shift").getString("unit");
            String cuff_rot_unit = modelData.getJSONObject("cuff").getJSONObject("rotate").getString("unit");
            Integer cuff_shift_x = modelData.getJSONObject("cuff").getJSONObject("shift").getInt("x");
            Integer cuff_shift_y = modelData.getJSONObject("cuff").getJSONObject("shift").getInt("y");
            Integer cuff_shift_z = modelData.getJSONObject("cuff").getJSONObject("shift").getInt("z");
            Integer cuff_rot = modelData.getJSONObject("cuff").getJSONObject("rotate").getInt("ang");

            cuffConformationParams.set("cuff_shift_x", cuff_shift_x + " " + cuff_shift_unit);
            cuffConformationParams.set("cuff_shift_y", cuff_shift_y + " " + cuff_shift_unit);
            cuffConformationParams.set("cuff_shift_z", cuff_shift_z + " " + cuff_shift_unit);
            cuffConformationParams.set("cuff_rot",  cuff_rot + " " + cuff_rot_unit);

            // Set MEDIUM parameters
            String mediumParamsLabel = "Medium Parameters";
            ModelParamGroup mediumParams = model.param().group().create(mediumParamsLabel);
            mediumParams.label(mediumParamsLabel);

            String bounds_unit = ((JSONObject) ((JSONObject) modelData.get("medium")).get("bounds")).getString("unit");

            // Length of the FEM - will want to converge thresholds for this
            double length = ((JSONObject) ((JSONObject) modelData.get("medium")).get("bounds")).getDouble("length");
            mediumParams.set("z_nerve", length + " " + bounds_unit);

            // Radius of the FEM - will want to converge thresholds for this
            double radius = ((JSONObject) ((JSONObject) modelData.get("medium")).get("bounds")).getDouble("radius");
            mediumParams.set("r_ground", radius + " " + bounds_unit);

            // Create PART PRIMITIVE for MEDIUM
            String mediumString = "Medium_Primitive";
            String partID = mw.im.next("part", mediumString);
            try {
                IdentifierManager partPrimitiveIM = Part.createEnvironmentPartPrimitive(partID, mediumString, mw);
                mw.partPrimitiveIMs.put(mediumString, partPrimitiveIM);
            } catch (IllegalArgumentException e) {
                e.printStackTrace();
            }

            // Create PART INSTANCE for MEDIUM
            String instanceLabel = "Medium";
            String instanceID = mw.im.next("pi", instanceLabel);
            try {
                Part.createEnvironmentPartInstance(instanceID, instanceLabel, mediumString, mw, modelData);
            } catch (IllegalArgumentException e) {
                e.printStackTrace();
            }

            // Read cuff to build from model.json (cuff.preset) which links to JSON containing instantiations of parts
            JSONObject cuffObject = (JSONObject) modelData.get("cuff");
            String cuff = cuffObject.getString("preset");

            // add PART PRIMITIVES for CUFF
            mw.addCuffPartPrimitives(cuff);

            // add PART INSTANCES for cuff
            mw.addCuffPartInstances(cuff, modelData);

            // add NERVE (Fascicles CI/MESH and EPINEURIUM)
            // there are no primitives/instances for nerve parts, just build them
            mw.addNerve(sample, nerveParams);

            // create UNIONS
            mw.createUnions();

            // BUILD GEOMETRY
            System.out.println("Building the FEM geometry.");

            // Saved model pre-run geometry for debugging
            String geomFile = String.join("/", new String[]{
                    projectPath,
                    "samples",
                    sample,
                    "models",
                    modelStr,
                    "model.mph"
            });

            try {
                System.out.println("Saving MPH (pre-geom_run) file to: " + geomFile);
                model.save(geomFile);
            } catch (IOException e) {
                e.printStackTrace();
            }

            model.component("comp1").geom("geom1").run("fin");

            // MESH
            // define MESH for NERVE
            String meshNerveSweLabel = "Mesh Nerve";
            MeshFeature meshNerve = model.component("comp1").mesh("mesh1").create(mw.im.next("swe",meshNerveSweLabel), "Sweep");
            meshNerve.selection().geom("geom1", 3);
            meshNerve.selection().named("geom1" + "_" + mw.im.get("allNervePartsUnionCsel") + "_dom");
            meshNerve.set("facemethod", "tri");
            meshNerve.label(meshNerveSweLabel);

            String meshNerveSizeInfoLabel = "Mesh Nerve Size Info";
            MeshFeature meshNerveSizeInfo = meshNerve.create(mw.im.next("size",meshNerveSizeInfoLabel), "Size");
            meshNerveSizeInfo.label(meshNerveSizeInfoLabel);

            JSONObject nerveMeshParams = modelData.getJSONObject("mesh").getJSONObject("nerve");
            meshNerveSizeInfo.set("custom", true);
            meshNerveSizeInfo.set("hmaxactive", true);
            meshNerveSizeInfo.set("hmax", nerveMeshParams.getDouble("hmax"));
            meshNerveSizeInfo.set("hminactive", true);
            meshNerveSizeInfo.set("hmin", nerveMeshParams.getDouble("hmin"));
            meshNerveSizeInfo.set("hgradactive", true);
            meshNerveSizeInfo.set("hgrad", nerveMeshParams.getDouble("hgrad"));
            meshNerveSizeInfo.set("hcurveactive", true);
            meshNerveSizeInfo.set("hcurve", nerveMeshParams.getDouble("hcurve"));
            meshNerveSizeInfo.set("hnarrowactive", true);
            meshNerveSizeInfo.set("hnarrow", nerveMeshParams.getDouble("hnarrow"));

            String meshRestFtetLabel = "Mesh Rest";
            MeshFeature meshRest = model.component("comp1").mesh("mesh1").create(mw.im.next("ftet",meshRestFtetLabel), "FreeTet");
            meshRest.selection().geom("geom1", 3);
            meshRest.selection().remaining();
            meshRest.label(meshRestFtetLabel);

            String meshRestSizeInfoLabel = "Mesh Rest Size Info";
            MeshFeature meshRestSizeInfo = meshRest.create(mw.im.next("size",meshRestSizeInfoLabel), "Size");
            meshRestSizeInfo.label(meshRestSizeInfoLabel);

            JSONObject restMeshParams = modelData.getJSONObject("mesh").getJSONObject("rest");
            meshRestSizeInfo.set("custom", true);
            meshRestSizeInfo.set("hmaxactive", true);
            meshRestSizeInfo.set("hmax", restMeshParams.getDouble("hmax"));
            meshRestSizeInfo.set("hminactive", true);
            meshRestSizeInfo.set("hmin", restMeshParams.getDouble("hmin"));
            meshRestSizeInfo.set("hgradactive", true);
            meshRestSizeInfo.set("hgrad", restMeshParams.getDouble("hgrad"));
            meshRestSizeInfo.set("hcurveactive", true);
            meshRestSizeInfo.set("hcurve", restMeshParams.getDouble("hcurve"));
            meshRestSizeInfo.set("hnarrowactive", true);
            meshRestSizeInfo.set("hnarrow", restMeshParams.getDouble("hnarrow"));

            // Saved model pre-mesh for debugging
            try {
                System.out.println("Saving MPH (pre-mesh) file to: " + geomFile);
                model.save(geomFile);
            } catch (IOException e) {
                e.printStackTrace();
            }

            System.out.println("Meshing nerve parts... will take a while");

            long nerveMeshStartTime = System.nanoTime();
            model.component("comp1").mesh("mesh1").run(mw.im.get(meshNerveSweLabel));
            long estimatedNerveMeshTime = System.nanoTime() - nerveMeshStartTime;
            nerveMeshParams.put("mesh_time",estimatedNerveMeshTime/Math.pow(10,6)); // convert nanos to millis

            System.out.println("Meshing the rest... will also take a while");

            long restMeshStartTime = System.nanoTime();
            model.component("comp1").mesh("mesh1").run(mw.im.get(meshRestFtetLabel));
            long estimatedRestMeshTime = System.nanoTime() - restMeshStartTime;
            restMeshParams.put("mesh_time",estimatedRestMeshTime/Math.pow(10,6)); // convert nanos to millis

            String quality_measure = "vollength";
            model.component("comp1").mesh("mesh1").stat().setQualityMeasure(quality_measure);
            // could instead use: skewness, maxangle, volcircum, vollength, condition, growth...

            Integer number_elements = model.component("comp1").mesh("mesh1").getNumElem("all");
            Double min_quality = model.component("comp1").mesh("mesh1").getMinQuality("all");
            Double mean_quality = model.component("comp1").mesh("mesh1").getMeanQuality("all");
            Double min_volume = model.component("comp1").mesh("mesh1").getMinVolume("all");
            Double volume = model.component("comp1").mesh("mesh1").getVolume("all");

            JSONObject meshStats = modelData.getJSONObject("mesh").getJSONObject("stats");
            meshStats.put("number_elements", number_elements);
            meshStats.put("min_quality", min_quality);
            meshStats.put("mean_quality", mean_quality);
            meshStats.put("min_volume", min_volume);
            meshStats.put("volume", volume);
            meshStats.put("quality_measure", quality_measure);

            // put nerve to mesh, rest to mesh, mesh to modelData
            JSONObject mesh = modelData.getJSONObject("mesh");
            mesh.put("nerve", nerveMeshParams);
            mesh.put("rest", restMeshParams);
            mesh.put("stats", meshStats);
            modelData.put("mesh", mesh);

            System.out.println("DONE MESHING");

            try {
                System.out.println("Saving MPH (post-mesh) file to: " + geomFile);
                model.save(geomFile);
            } catch (IOException e) {
                e.printStackTrace();
            }

            // add MATERIAL DEFINITIONS
            String materialParamsLabel = "Material Parameters";
            ModelParamGroup materialParams = model.param().group().create(materialParamsLabel);
            materialParams.label(materialParamsLabel);

            String nerveMode = (String) sampleData.getJSONObject("modes").get("nerve");
            ArrayList<String> bio_materials = new ArrayList<>(Arrays.asList("medium", "perineurium", "endoneurium"));
            if (nerveMode.equals("PRESENT")) {
                bio_materials.add("epineurium");
            }
            mw.addMaterialDefinitions(bio_materials, modelData, materialParams);

            JSONObject cuffData = new JSONReader(String.join("/",
                    new String[]{mw.root, "config", "system", "cuffs", cuff})).getData();

            ArrayList<String> cuff_materials = new ArrayList<>();
            // loop through all part instances
            for (Object item: (JSONArray) cuffData.get("instances")) {
                JSONObject itemObject = (JSONObject) item;
                for (Object function: itemObject.getJSONArray("materials")) {
                    JSONObject functionObject = (JSONObject) function;
                    cuff_materials.add(functionObject.getString("info"));
                }
            }
            mw.addMaterialDefinitions(cuff_materials, modelData, materialParams);

            // Add material assignments (links)
            // DOMAIN
            String mediumMaterial = mw.im.get("medium");
            IdentifierManager myIM = mw.getPartPrimitiveIM(mediumString);
            if (myIM == null) throw new IllegalArgumentException("IdentfierManager not created for name: " + mediumString);
            String[] myLabels = myIM.labels; // may be null, but that is ok if not used
            String selection = myLabels[0];
            String linkLabel = String.join("/", new String[]{instanceLabel, selection, "medium"});
            Material mat = model.component("comp1").material().create(mw.im.next("matlnk", linkLabel), "Link");
            mat.label(linkLabel);
            mat.set("link", mediumMaterial);
            mat.selection().named("geom1_" + mw.im.get(instanceLabel) + "_" + myIM.get(selection) + "_dom");

            // CUFF
            mw.addCuffPartMaterialAssignments(cuffData);

            // NERVE
            // Add epineurium only if NerveMode == PRESENT
            if (nerveMode.equals("PRESENT")) {
                String epineuriumMatLinkLabel = "epineurium material";
                PropFeature epineuriumMatLink = model.component("comp1").material().create(mw.im.next("matlnk",epineuriumMatLinkLabel), "Link");
                epineuriumMatLink.selection().named("geom1" +"_" + mw.im.get("EPINEURIUM") + "_dom");
                epineuriumMatLink.label(epineuriumMatLinkLabel);
                epineuriumMatLink.set("link", mw.im.get("epineurium"));
            }

            // Add perineurium material only if there are any fascicles being meshed
            if (mw.im.get("periUnionCsel") != null) {
                String perineuriumMatLinkLabel = "perineurium material";
                PropFeature perineuriumMatLink = model.component("comp1").material().create(mw.im.next("matlnk",perineuriumMatLinkLabel), "Link");
                perineuriumMatLink.selection().named("geom1" +"_" + mw.im.get("periUnionCsel") + "_dom");
                perineuriumMatLink.label(perineuriumMatLinkLabel);
                perineuriumMatLink.set("link", mw.im.get("perineurium"));
            }

            // Will always need to add endoneurium material
            String fascicleMatLinkLabel = "endoneurium material";
            PropFeature fascicleMatLink = model.component("comp1").material().create(mw.im.next("matlnk",fascicleMatLinkLabel), "Link");
            fascicleMatLink.selection().named("geom1" +"_" + mw.im.get("endoUnionCsel") + "_dom");
            fascicleMatLink.label(fascicleMatLinkLabel);
            fascicleMatLink.set("link", mw.im.get("endoneurium"));

            // Solve
            JSONObject solver = modelData.getJSONObject("solver");
            String version = ModelUtil.getComsolVersion(); //The getComsolVersion method returns the current COMSOL Multiphysics
            solver.put("name",version);
            modelData.put("solver", solver);

            model.study().create("std1");
            model.study("std1").setGenConv(true);
            model.study("std1").create("stat", "Stationary");
            model.study("std1").feature("stat").activate("ec", true);

            model.sol().create("sol1");
            model.sol("sol1").study("std1");

            model.study("std1").feature("stat").set("notlistsolnum", 1);
            model.study("std1").feature("stat").set("notsolnum", "1");
            model.study("std1").feature("stat").set("listsolnum", 1);
            model.study("std1").feature("stat").set("solnum", "1");

            model.sol("sol1").create("st1", "StudyStep");
            model.sol("sol1").feature("st1").set("study", "std1");
            model.sol("sol1").feature("st1").set("studystep", "stat");
            model.sol("sol1").create("v1", "Variables");
            model.sol("sol1").feature("v1").set("control", "stat");

            model.sol("sol1").create("s1", "Stationary");
            model.sol("sol1").feature("s1").create("fc1", "FullyCoupled");
            model.sol("sol1").feature("s1").create("i1", "Iterative");
            model.sol("sol1").feature("s1").feature("i1").set("linsolver", "cg");
            model.sol("sol1").feature("s1").feature("i1").create("mg1", "Multigrid");
            model.sol("sol1").feature("s1").feature("i1").feature("mg1").set("prefun", "amg");
            model.sol("sol1").feature("s1").feature("fc1").set("linsolver", "i1");
            model.sol("sol1").feature("s1").feature().remove("fcDef");
            model.sol("sol1").attach("std1");

            model.result().create("pg1", "PlotGroup3D");
            model.result("pg1").label("Electric Potential (ec)");
            model.result("pg1").set("frametype", "spatial");
            model.result("pg1").set("data", "dset1");
            model.result("pg1").feature().create("mslc1", "Multislice");
            model.result("pg1").feature("mslc1").set("colortable", "RainbowLight");
            model.result("pg1").feature("mslc1").set("data", "parent");

            model.result("pg1").run();
            model.result("pg1").set("data", "dset1");

            // Saved meshed model
            String mphFile = String.join("/", new String[]{
                    projectPath,
                    "samples",
                    sample,
                    "models",
                    modelStr,
                    "model.mph"
            });

            try {
                System.out.println("Saving MPH (mesh only) file to: " + mphFile);
                model.save(mphFile);
            } catch (IOException e) {
                e.printStackTrace();
            }

            mw.loopCurrents(modelData, projectPath, sample, modelStr);

            try (FileWriter file = new FileWriter("../" + modelFile)) {
                String output = modelData.toString(2);
                file.write(output);

            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        ModelUtil.disconnect();
        System.out.println("Disconnected from COMSOL Server");
    }
}

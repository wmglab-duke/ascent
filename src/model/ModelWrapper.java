package model;

import com.comsol.model.MeshFeature;
import com.comsol.model.Model;
import com.comsol.model.physics.PhysicsFeature;
import com.comsol.model.util.ModelUtil;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;

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
     * TODO: UNFINISHED
     * Examples of parts: cuff, fascicle, etc.
     * The method will automatically create required part primitives and pass the HashMap with their id's to model.Part
     * @param name the name of the JSON configuration (same as unique indicator) for a given part
     * @return success indicator (might remove this later)
     */

    /**
     * Create the required primitives for a given cuff json
     * @param name json filename WITH extension (i.e. "LivaNova.json")
     * @return success indicator
     */
    public boolean addCuffPartPrimitives(String name) {
        // extract data from json
        try {
            JSONObject data = new JSONReader(String.join("/",
                    new String[]{this.root, ".templates", name})).getData();

            // get the id for the next "par" (i.e. parameters section), and give it a name from the JSON file name
            String id = this.next("par", name);
            model.param().group().create(id);
            model.param(id).label(name.split("\\.")[0]);

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
                        IdentifierManager partPrimitiveIM = Part.createPartPrimitive(partID, partPrimitiveName, this);

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
     * @return success indicator
     */
    public boolean addCuffPartInstances(String name) {
        // extract data from json
        // name is something like Enteromedics.json
        try {
            JSONObject data = new JSONReader(String.join("/",
                    new String[]{this.root, ".templates", name})).getData();

            // loop through all part instances
            for (Object item: (JSONArray) data.get("instances")) {
                JSONObject itemObject = (JSONObject) item;

                String instanceLabel = (String) itemObject.get("label");
                String instanceID = this.im.next("pi", instanceLabel);
                String type = (String) itemObject.get("type");
                Part.createCuffPartInstance(instanceID, instanceLabel, type , this, itemObject);
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
            return false;
        }
        return true;
    }

    /**
     * Create materials for the given CUFF. The material parameters can be found in master.json
     * NOTE: this does not create materials required for the nerve, fascicles, etc. --- see addBioMaterialDefinitions()
     * @param name same formatting as addCuffPartPrimitives
     * @return success indicator
     */
    public boolean addCuffMaterialDefinitions(String name) {
        // extract data from json
        try {
            JSONObject data = new JSONReader(String.join("/",
                    new String[]{this.root, ".templates", name})).getData();

            JSONObject master = new JSONReader(String.join("/",
                    new String[]{this.root, ".config", "master.json"})).getData();

            // for each material definition, create it (if not already existing)
            for (Object item: (JSONArray) data.get("instances")) {
                JSONObject itemObject = (JSONObject) item;
                JSONArray materials = itemObject.getJSONArray("materials");

                for(Object o: materials) {
                    String materialName = ((JSONObject) o).getString("type");

                    // create the material definition if it has not already been created
                    if (! this.im.hasPseudonym(materialName)) {
                        // get next available (TOP LEVEL) "material" id
                        String materialID = this.im.next("mat", materialName);

                        try {
                            // TRY to create the material definition (catch error if no existing implementation)
                            Part.defineMaterial(materialID, materialName, master, this);
                        } catch (IllegalArgumentException e) {
                            e.printStackTrace();
                            return false;

                        }
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
     * Create materials necessary for fascicles, nerve, surrounding media, etc. --- always called!
     * @return success indicator
     */
    public boolean addBioMaterialDefinitions() {
        // extract data from json



        try {
            JSONObject master = new JSONReader(String.join("/",
                    new String[]{this.root, ".config", "master.json"})).getData();

            // define medium based on the preset defined in the medium block in master.json
            String mediumMaterial = ((JSONObject) master.get("medium")).getString("material");
            String mediumMaterialID = this.im.next("mat", mediumMaterial);
            Part.defineMaterial(mediumMaterialID, mediumMaterial, master, this);

            String periMaterialID = this.im.next("mat", "perineurium_DC"); // todo for freq of interest
            Part.defineMaterial(periMaterialID, "perineurium_DC", master, this);

            String endoMaterialID = this.im.next("mat", "endoneurium");
            Part.defineMaterial(endoMaterialID, "endoneurium", master, this);

            String epiMaterialID = this.im.next("mat", "epineurium"); // todo if compound nerve
            Part.defineMaterial(epiMaterialID, "epineurium", master, this);

            // Medium (muscle or fat?)

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
    public boolean addFascicles() {

        // define global nerve part names (MUST BE IDENTICAL IN Part)
        String[] partPrimitiveNames = new String[]{"FascicleCI", "FascicleMesh"};

        // Load configuration file
        try {
            JSONObject json_data = new JSONReader(String.join("/", new String[]{
                    this.root,
                    ".config",
                    "master.json"
            })).getData();

            JSONObject morphology_data = new JSONReader(String.join("/", new String[]{
                    this.root,
                    "data",
                    "samples",
                    (String) json_data.get("sample"),
                    "morphology.json"
            })).getData();

            // Build path to fascicles
            String fasciclesPath = String.join("/", new String[]{
                    this.root,
                    "data",
                    "samples",
                    (String) json_data.get("sample"),
                    "0", // these 0's are temporary (for 3d models will need to change)
                    "0",
                    (String) ((JSONObject) json_data.get("modes")).get("write"),
                    "fascicles"
            });

            // Loop over all fascicle dirs
            String[] dirs = new File(fasciclesPath).list();
            if (dirs != null) {
                for (String dir: dirs) {
                    if (! dir.contains(".")) {
                        int index = Integer.parseInt(dir);
//                        String fascicleName = String.valueOf(index);
                        String fascicleName = "fascicle" + (index);

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
                        String fascicleType = data.get("inners").length == 1 ? partPrimitiveNames[0] : partPrimitiveNames[1];

                        // hand off to Part to build instance of fascicle
                        Part.createNervePartInstance(fascicleType, index, path, this, data, morphology_data, json_data);
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
    public void loopCurrents() {
        for(String key: this.im.currentPointers.keySet()) {
            System.out.println("Current pointer: " + key);
            PhysicsFeature current = (PhysicsFeature) this.im.currentPointers.get(key);

            current.set("Qjp", 0.001);
        }
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
     * @param args do not use
     */
    public static void main(String[] args) {

        // Take projectPath input to ModelWrapper and assign to string.
        String projectPath = args[0];

        // Load configuration data
        String configFile = "/.config/master.json";
        JSONObject configData = null;
        try {
            configData = new JSONReader(projectPath + configFile).getData();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

        // Load morphology data
        String morphologyFile = String.join("/", new String[]{
                "data",
                "samples",
                (String) configData.get("sample"),
                "morphology.json"
        });
        JSONObject morphologyData = null;
        try {
            morphologyData = new JSONReader(projectPath + "/" + morphologyFile).getData();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

        // Start COMSOL Instance
        ModelUtil.connect("localhost", 2036);
        ModelUtil.initStandalone(false);

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

        // Set generic parameters - todo these are for compound nerves, what about single fascicle????
        JSONObject nerve = (JSONObject) morphologyData.get("Nerve");
        model.param().set("a_nerve", nerve.get("area") + " [micrometer^2]");
        model.param().set("r_nerve", "sqrt(a_nerve/pi)");
        model.param().set("rho_peri", "1149 [ohm*m]");


        Double length = ((JSONObject) configData.get("medium")).getDouble("length");
        model.param().set("z_nerve", length);

        Double radius = ((JSONObject) configData.get("medium")).getDouble("radius");
        model.param().set("r_ground", radius);

        String mediumString = "Medium_Primitive";
        String partID = mw.im.next("part", mediumString);
        try {
            IdentifierManager partPrimitiveIM = Part.createEnvironmentPartPrimitive(partID, mediumString, mw);
            mw.partPrimitiveIMs.put(mediumString, partPrimitiveIM);
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        }

        String instanceLabel = "Medium";
        String instanceID = mw.im.next("pi", instanceLabel);
        try {
        Part.createEnvironmentPartInstance(instanceID, instanceLabel, mediumString, mw, configData);
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        }

        // Read cuffs to build from master.json (cuff.preset) which links to JSON containing instantiations of parts
        JSONObject cuffObject = (JSONObject) configData.get("cuff");
        JSONArray cuffs = (JSONArray) cuffObject.get("preset");

        // Build cuffs
        for (int i = 0; i < cuffs.length(); i++) {
            // make list of cuffs in model
            String cuff = cuffs.getString(i);
            // add part primitives for cuff
            mw.addCuffPartPrimitives(cuff);
            // add material definitions for cuff
            mw.addCuffMaterialDefinitions(cuff);
            // add part instances for cuff
            mw.addCuffPartInstances(cuff);
        }

        // Add biological material definitions
        mw.addBioMaterialDefinitions();
        // Add epineurium
        Part.createNervePartInstance("Epineurium", 0, null, mw, null, morphologyData, configData);
        // Add fascicles
        mw.addFascicles();
        // Create unions
        mw.createUnions();

        // Add materials
//        String perineuriumMatLinkLabel = "perineurium_DC material"; // TODO frequency dependence
//        model.component("comp1").material().create(mw.im.next("matlnk",perineuriumMatLinkLabel), "Link");
//        model.component("comp1").material(mw.im.get(perineuriumMatLinkLabel)).selection().named("geom1" +"_" + mw.im.get("periUnionCsel") + "_dom");
//        model.component("comp1").material(mw.im.get(perineuriumMatLinkLabel)).label(perineuriumMatLinkLabel);
//        model.component("comp1").material(mw.im.get(perineuriumMatLinkLabel)).set("link", mw.im.get("perineurium_DC"));

        String epineuriumMatLinkLabel = "epineurium material";
        model.component("comp1").material().create(mw.im.next("matlnk",epineuriumMatLinkLabel), "Link");
        model.component("comp1").material(mw.im.get(epineuriumMatLinkLabel)).selection().named("geom1" +"_" + mw.im.get("EPINEURIUM") + "_dom");
        model.component("comp1").material(mw.im.get(epineuriumMatLinkLabel)).label(epineuriumMatLinkLabel);
        model.component("comp1").material(mw.im.get(epineuriumMatLinkLabel)).set("link", mw.im.get("epineurium"));

        String fascicleMatLinkLabel = "endoneurium material";
        model.component("comp1").material().create(mw.im.next("matlnk",fascicleMatLinkLabel), "Link");
        model.component("comp1").material(mw.im.get(fascicleMatLinkLabel)).selection().named("geom1" +"_" + mw.im.get("endoUnionCsel") + "_dom");
        model.component("comp1").material(mw.im.get(fascicleMatLinkLabel)).label(fascicleMatLinkLabel);
        model.component("comp1").material(mw.im.get(fascicleMatLinkLabel)).set("link", mw.im.get("endoneurium"));

        try {
            model.save("parts_test"); // TODO this dir needs to change
        } catch (IOException e) {
            e.printStackTrace();
        }

        // Build the geometry
        model.component("comp1").geom("geom1").run("fin");

        // Define mesh for nerve
        String meshFascLabel = "Mesh Nerve";
        String meshFascSweLabel = "Mesh Nerve Sweep";
        MeshFeature meshFasc = model.component("comp1").mesh(mw.im.next("mesh",meshFascLabel)).create(mw.im.next("swe",meshFascSweLabel), "Sweep");
        meshFasc.selection().geom("geom1", 3);
        meshFasc.selection().named("geom1" + "_" + mw.im.get("allNervePartsUnionCsel") + "_dom");
        model.component("comp1").mesh(mw.im.get(meshFascLabel)).feature("size").set("hauto", 1); // TODO load in mesh params from master
        //model.component("comp1").mesh(mw.im.get(meshFascLabel)).run(mw.im.get(meshFascSweLabel)); // commented out for dev

        // Define mesh for remaining geometry (cuff, cuff fill, and medium)
        // TODO

        // Run mesh
        // TODO
        // Save

        // Solve
        // Adjust current sources
        // TODO
        // Save

        // TODO, save time to process trace, build FEM Geometry, mesh, solve, extract potentials "TimeKeeper"

        mw.loopCurrents();

        try {
            model.save("parts_test"); // TODO this dir needs to change
        } catch (IOException e) {
            e.printStackTrace();
        }

        ModelUtil.disconnect();

        System.out.println("Disconnected from COMSOL Server");
    }
}

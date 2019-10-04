package model;

import com.comsol.model.Model;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;

/**
 * model.ModelWrapper
 *
 * NOTE: Eventually, call this class ModelWrapper (NOT ModelWrapper2).
 *
 * Master high-level class for managing a model, its metadata, and various critical operations such as creating parts
 * and extracting potentials. This class houses the "meaty" operations of actually interacting with the model object
 * when creating parts in the static class model.Parts.
 *
 * Up for consideration: where to house the meshing/solving/extracting code?
 */
public class ModelWrapper2 {

    // INSTANCE VARIABLES

    // main model
    private Model model;

    // top level indentifier manager
    private IdentifierManager im = new IdentifierManager();

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
    ModelWrapper2(Model model, String projectRoot) {
        this.model = model;
        this.root = projectRoot;
    }

    /**
     * Overloaded constructor for passing in save directory
     * @param model com.comsol.model.Model object is REQUIRED
     * @param projectRoot the root directory of the project (might remove if unnecessary)
     * @param defaultSaveDestination directory in which to save (relative to project root)
     */
    ModelWrapper2(Model model, String projectRoot, String defaultSaveDestination) {
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
     *
     * @param destination full path to save to
     * @return success indicator
     */
    public boolean save(String destination) {
        try {
            this.model.save(destination);
            return true;
        } catch (IOException e) {
            System.out.println("Failed to save to destination: " + destination);
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
    public boolean addPart(String name) {

        // extract data from json
        JSONObject data = new JSONReader(String.join("/",
                new String[]{this.root,".templates", name + ".json"})).getData();

        // get the id for the next "par" (i.e. parameters section)
        String id = this.next("par", name);

        // loop through all parameters in file, and set in parameters
        for (Object item : (JSONArray) data.get("params")) {
            JSONObject itemObject = (JSONObject) item;
            model.param(id).set(
                    (String) itemObject.get("name"),
                    (String) itemObject.get("expression"),
                    (String) itemObject.get("description")
            );
        }

        // for each required part, create it (if not already existing)
        // then  initialize that part
        for (Object item: (JSONArray) data.get("parts")) {
            String partName = (String) item; // quick cast to String

            // create the part if it has not already been created
            if (! this.im.hasPseudonym(partName)) {
                // get next available (TOP LEVEL) "part" id
                String partID = this.im.next("part", partName);
                // TRY to create that part, assuming there is an existing implementation (catch error if not)
                try {
                    IdentifierManager partIM = Part.createPartPrimitive(partID, partName, this);
                    // add the returned id manager to the HashMap of IMs with the partName as its key
                    this.partPrimitiveIMs.put(partName, partIM);
                } catch (IllegalArgumentException e) {
                    e.printStackTrace();
                }
            }

            // initialize that part!
//            Part.createPartInstance(this.next())
        }

        return true;
    }

    public boolean extractPotentials(String json_path) {

        // TODO: Simulation folders; sorting through configuration files VIA PYTHON
        // TODO: FORCE THE USER TO STAGE/COMMIT CHANGES BEFORE RUNNING; add Git Commit ID/number to config file

        JSONObject json_data = new JSONReader(String.join("/", new String[]{root, json_path})).getData();

        double[][] coordinates = new double[3][5];
        String id = this.next("interp");

        model.result().numerical().create(id, "Interp");
        model.result().numerical(id).set("expr", "V");
        model.result().numerical(id).setInterpolationCoordinates(coordinates);

        double[][][] data = model.result().numerical(id).getData();

        System.out.println("data.toString() = " + Arrays.deepToString(data));

        return true;
    }

    public static void main(String[] args) {
        ModelWrapper2 mw = new ModelWrapper2(null, "/Users/jakecariello/Box/Documents/Pipeline/access");


    }
}

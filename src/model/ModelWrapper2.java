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

    // managing identifiers within COMSOL
    private HashMap<String, Integer> identifierStates = new HashMap<>();
    private HashMap<String, String> identifierPseudonyms = new HashMap<>();

    // managing parts within COMSOL
    private HashMap<String, String> partPrimitives = new HashMap<>();
    private HashMap<String, String> partInstances = new HashMap<>();

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

    public Model getModel() {
        return model;
    }

    public String getRoot() {
        return root;
    }

    public String getDest() {
        return dest;
    }

    public void setRoot(String root) {
        this.root = root;
    }

    public void setDest(String dest) {
        this.dest = dest;
    }

    public HashMap<String, String> getPartInstances() {
        return partInstances;
    }

    public HashMap<String, String> getPartPrimitives() {
        return partPrimitives;
    }

    // OTHER METHODS

    /**
     *
     * @param key type of id to get the next index for
     * @return a string in the form of [id][N], where id is the key passed in and N is the next available index
     */
    public String nextID(String key) {
        // default next index to 1 (assume first call of key)
        int nextIndex = 1;
        // if the key already exists, set
        if (identifierStates.containsKey(key)) nextIndex = identifierStates.get(key) + 1;
        // update identifiers index
        identifierStates.put(key, nextIndex);
        return key + nextIndex;
    }

    /**
     * Overloaded method if saving the acquired id as a pseudonym (to be accessible later by that pseudonym)
     * @param key the type of id to get the next index for
     * @param pseudonym the name to give that id
     * @return string in form [id][N] (id is key passed in, N is next available index); null (pseudonym already used)
     */
    public String nextID(String key, String pseudonym) {
        // get next key using base method
        String id = this.nextID(key);
        // put into map as key, value pair
        if (! identifierPseudonyms.containsKey(pseudonym)) {
            identifierPseudonyms.put(pseudonym, id);
            return id; // pseudonym was NOT already in use!
        }
        return null; // pseudonym was already in use!
    }

    /**
     *
     * @param psuedonym previously assigned using nextID(String, String)
     * @return associated id (from the HashMap)
     */
    public String getID(String psuedonym) {
        if (identifierPseudonyms.containsKey(psuedonym)) return identifierPseudonyms.get(psuedonym);
        return null;
    }

    /**
     *
     * @param destination full path to save to
     * @return success indicator
     */
    public boolean saveModel(String destination) {
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
    public boolean saveModel() {
        if (this.dest != null) return saveModel(String.join("/", new String[]{this.root, this.dest}));
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
        String id = this.nextID("par", name);

        // loop through all parameters in file, and set in parameters
        for (Object item : (JSONArray) data.get("params")) {
            JSONObject itemObject = (JSONObject) item;
            model.param(id).set(
                    (String) itemObject.get("name"),
                    (String) itemObject.get("expression"),
                    (String) itemObject.get("description")
            );
        }

        return true;
    }

    public boolean extractPotentials(String json_path) {

        JSONObject json_data = new JSONReader(json_path).getData();

        double[][] coordinates = new double[3][5];
        String id = this.nextID("interp");

        model.result().numerical().create(id, "Interp");
        model.result().numerical(id).set("expr", "V");
        model.result().numerical(id).setInterpolationCoordinates(coordinates);

        double[][][] data = model.result().numerical(id).getData();

        System.out.println("data.toString() = " + Arrays.deepToString(data));

        return true;
    }
}

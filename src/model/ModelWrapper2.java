package model;

import com.comsol.model.Model;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.util.HashMap;

public class ModelWrapper2 {

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


    ModelWrapper2(Model model, String projectRoot) {
        this.model = model;
        this.root = projectRoot;
    }

    ModelWrapper2(Model model, String projectRoot, String defaultSaveDestination) {
        this(model, projectRoot);
        this.dest = defaultSaveDestination;
    }

    public String nextID(String key) {
        // default next index to 1 (assume first call of key)
        int nextIndex = 1;
        // if the key already exists, set
        if (identifierStates.containsKey(key)) nextIndex = identifierStates.get(key) + 1;
        // update identifiers index
        identifierStates.put(key, nextIndex);
        return key + nextIndex;
    }

    public String nextID(String key, String pseudonym) {
        // get next key using base method
        String id = this.nextID(key);
        // put into map as key, value pair
        identifierPseudonyms.put(pseudonym, id);
        return id;
    }

    public String getID(String psuedonym) {
        if (identifierPseudonyms.containsKey(psuedonym)) return identifierPseudonyms.get(psuedonym);
        return null;
    }

    public boolean saveModel(String destination) {
        try {
            this.model.save(destination);
            return true;
        } catch (IOException e) {
            System.out.println("Failed to save to destination: " + destination);
            return false;
        }
    }

    public boolean saveModel() {
        if (this.dest != null) return saveModel(this.dest);
        else {
            System.out.println("Save directory not initialized");
            return false;
        }
    }

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

}

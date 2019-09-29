package model;

import com.comsol.model.Model;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;

public class ModelWrapper2 {

    private Model model;

    private HashMap<String, Integer> identifierStates = new HashMap<>();
    private HashMap<String, String> identifierPseudonyms = new HashMap<>();

    private ArrayList<Part> parts = new ArrayList<>();

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
        identifierPseudonyms.put(id, pseudonym);
        return id;
    }

    public boolean save(String destination) {
        try {
            this.model.save(destination);
            return true;
        } catch (IOException e) {
            System.out.println("Failed to save to destination: " + destination);
            return false;
        }
    }

    public boolean save() {
        if (this.dest != null) return save(this.dest);
        else {
            System.out.println("Save directory not initialized");
            return false;
        }
    }

}

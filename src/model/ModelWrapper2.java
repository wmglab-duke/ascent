package model;

import com.comsol.model.Model;

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

    public next(String key, String pseudonym) {
        String id = this.next(key);
        identifierPseudonyms.put(id, pseudonym);
    }

    public String next(String key) {
        // default next index to 1 (assume first call of key)
        int nextIndex = 1;

        // if the key already exists, set
        if (identifierStates.containsKey(key)) {
            nextIndex = identifierStates.get(key) + 1;
        }

        // update identifiers index
        identifierStates.put(key, nextIndex);

        // return String version (i.e. "keyN")
        return key + nextIndex;
    }
}

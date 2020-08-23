package model;

import org.json.JSONObject;

import java.util.*;

public class IdentifierManager {

    private HashMap<String, Integer> identifierStates = new HashMap<>();
    private HashMap<String, String> identifierPseudonyms = new HashMap<>();

    public String[] labels = null;
    public LinkedHashMap<String, String> currentIDs = new LinkedHashMap<>();

    /**
     * @param identifierStates set
     */
    public void setIdentifierStates(HashMap<String, Integer> identifierStates) {
        this.identifierStates = identifierStates;
    }

    /**
     * @param identifierPseudonyms set
     */
    public void setIdentifierPseudonyms(HashMap<String, String> identifierPseudonyms) {
        this.identifierPseudonyms = identifierPseudonyms;
    }

    /**
     *
     * @param key type of id to get the next index for
     * @return a string in the form of [id][N], where id is the key passed in and N is the next available index
     */
    public String next(String key) {
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
    public String next(String key, String pseudonym) {
        // get next key using base method
        String id = this.next(key);
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
    public String get(String psuedonym) {
        if (identifierPseudonyms.containsKey(psuedonym)) return identifierPseudonyms.get(psuedonym);

        System.out.println("Attempted to fetch id for id-less pseudonym: " + psuedonym);

        return null;
    }

    /**
     * @return the amount of
     */
    public int count() {
        int result = 0;
        for (String key: this.identifierStates.keySet()) {
            result += this.identifierStates.get(key);
        }
        return result;
    }

    /**
     * @param pseudonym the pseudonym to check
     * @return true if the pseudonym has already been used
     */
    public boolean hasPseudonym(String pseudonym) {
        return this.identifierPseudonyms.containsKey(pseudonym);
    }

    /**
     * @param jsonObject data that PERFECTLY matches structure of IM in a Map fashion (see implementation)
     * @return constructed IM
     */
    public static IdentifierManager fromJSONObject(JSONObject jsonObject) {
        Map<String, Object> map = jsonObject.toMap();
        IdentifierManager im = new IdentifierManager();

        assert map.get("identifierStates") instanceof HashMap;
        im.setIdentifierStates((HashMap<String, Integer>) map.get("identifierStates"));
        assert map.get("identifierPseudonyms") instanceof HashMap;
        im.setIdentifierPseudonyms((HashMap<String, String>) map.get("identifierPseudonyms"));
        assert map.get("labels") instanceof String[];
        Object[] buffer = ((ArrayList<Object>) map.get("labels")).toArray(new Object[0]);
        im.labels = new String[buffer.length];
        for (int i = 0; i < buffer.length; i += 1) {
            im.labels[i] = (String) buffer[i];
        }
        assert map.get("currentIDs") instanceof HashMap;
        im.currentIDs = (LinkedHashMap<String, String>) map.get("currentIDs");

        return im;
    }

    /**
     *
     * @return JSONObject where all the instance variables have been entered as values with their names as keys
     */
    public JSONObject toJSONObject() {
        Map<String, Object> map = new HashMap<>();
        map.put("identifierStates", this.identifierStates);
        map.put("identifierPseudonyms", this.identifierPseudonyms);
        map.put("labels", this.labels);
        map.put("currentIDs", this.currentIDs);
        return new JSONObject(map);
    }
}
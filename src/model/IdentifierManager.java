package model;

import java.util.*;

public class IdentifierManager {

    private HashMap<String, Integer> identifierStates = new HashMap<>();
    private HashMap<String, String> identifierPseudonyms = new HashMap<>();

    public String[] labels = null;

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
}
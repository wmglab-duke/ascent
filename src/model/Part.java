package model;

import com.comsol.model.Model;

import java.util.HashMap;

class Part {


    public static boolean createPartPrimitive(String id, String psuedonym, Model model) {

        return createPartPrimitive(id, psuedonym, model, null);
    }

    public static boolean createPartInstance(String id, String psuedonym, Model model,
                                             HashMap<String, String> partPrimitives) {
        return createPartInstance(id, psuedonym, model, partPrimitives, null);
    }

    /**
     *
     * @param id
     * @param psuedonym
     * @param model
     * @param data
     * @return
     */
    public static boolean createPartPrimitive(String id, String psuedonym, Model model,
                                              HashMap<String, Object> data) {


        switch (psuedonym) {



        }

        return true;
    }

    /**
     *
     * @param id
     * @param psuedonym
     * @param model
     * @param partPrimitives
     * @param data
     * @return
     */
    public static boolean createPartInstance(String id, String psuedonym, Model model,
                                             HashMap<String, String> partPrimitives, HashMap<String, Object> data) {

        switch (psuedonym) {



        }

        return true;
    }
}

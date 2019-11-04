package model;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;


/*
Inspired by code from https://crunchify.com/how-to-read-json-object-from-file-in-java/
 */

public class JSONReader {

    private JSONObject jsonObject;

    public JSONReader(String filepath) throws FileNotFoundException {
        String text = new Scanner(new File(filepath)).useDelimiter("\\A").next();
        jsonObject = new JSONObject(text);
    }

    public JSONObject getData() {
        return jsonObject;
    }

    // example usage for looping over parameters in a file from .templates (top level list)
    public static void main(String[] args) {
        // NOTE: "/" can be used on any OS in Java! HYPE!
        try {
            JSONObject data = new JSONReader(".templates/CorTec.json").getData();
            for (Object item: (JSONArray) data.get("data")) {
                JSONObject itemObject = (JSONObject) item;
                System.out.println("expression: " + itemObject.get("expression"));
                System.out.println("name: " + itemObject.get("name"));
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    }
}

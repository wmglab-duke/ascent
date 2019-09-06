package utils;

import org.json.JSONArray;
import org.json.JSONObject;

import java.nio.file.Files;
import java.nio.file.Paths;


/*
Inspired by code from https://crunchify.com/how-to-read-json-object-from-file-in-java/
 */

public class JSONReader {

    private JSONObject jsonObject;

    public JSONReader(String filepath) {
        try {
            String text = new String(Files.readAllBytes(Paths.get(filepath)));
            jsonObject = new JSONObject(text);
        } catch (Exception e) {
            // tell user if fails (likely because wrong path or wrong file type)
            e.printStackTrace();
        }
    }

    public JSONObject getData() {
        return jsonObject;
    }

    // example usage for looping over parameters in a file from .templates (top level list)
    public static void main(String[] args) {
        // NOTE: "/" can be used on any OS in Java! HYPE!
        JSONObject data = new JSONReader(".templates/CorTec.json").getData();
        for (Object item: (JSONArray) data.get("data")) {
            JSONObject itemObject = (JSONObject) item;
            System.out.println("expression: " + itemObject.get("expression"));
            System.out.println("name: " + itemObject.get("name"));
            System.out.println("");
        }
    }
}

package model;

import org.json.JSONObject;

import java.io.*;
import java.util.Scanner;

public class JSONio {

    public static JSONObject read(String filepath) {
        try {
            return new JSONObject(new Scanner(new File(filepath)).useDelimiter("\\A").next());
        } catch (FileNotFoundException e) {
            e.printStackTrace();
            return null;
        }
    }

    public static void write(String filepath, JSONObject data) throws IOException {
        BufferedWriter writer = new BufferedWriter(new FileWriter(filepath));
        writer.write(data.toString());
        writer.close();
    }

}

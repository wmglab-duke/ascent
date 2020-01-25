package model;

import com.comsol.model.Model;
import com.comsol.model.util.ModelUtil;
import org.json.JSONObject;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

/*
TODO: allow mesh match with self if mesh.mph does exist and bases/ is empty
 */

public class ModelSearcher {

    private Path root;

    public ModelSearcher(String root) {
        this.setRoot(root);
    }

    public boolean setRoot(String root) {

        this.root = Paths.get(root);

        if (! Files.exists(this.root)) {
            this.root = null;
            return false;
        }

        return true;
    }

    public String getRoot() {
        return root.toString();
    }

    /**
     *
     * @param query
     * @param reference
     * @return
     */
    public ModelSearcher.Match searchMeshMatch(JSONObject query, JSONObject reference, String queryPath) throws IOException {

//        System.out.println("queryPath = " + queryPath);

        for (Path file : Files.walk(this.root).toArray(Path[]::new)) {

//            System.out.println("file = " + file.toString())

            String[] fileParts = file.toString().split("/");

            if (fileParts[fileParts.length - 1].equals("model.json")) {
                JSONObject target = JSONio.read(file.toString());
                String directory = String.join("/", Arrays.copyOfRange(fileParts, 0, fileParts.length - 1));
                if (ModelSearcher.meshMatch(reference, query, target) && ModelSearcher.meshFilesExist(directory)) {
                    System.out.println("Skipping meshing because found mesh match: " + directory);
                    return Match.fromMeshPath(directory);
                }
            }
        }
        return null;
    }

    private static boolean meshFilesExist(String directory) {
        String[] filenames = {
                directory + "/model.json",
                directory + "/mesh/mesh.mph",
                directory + "/mesh/im.json"
        };
        for (String filename: filenames) {
//            System.out.println("Checking existence of: " + filename);
            if (! new File(filename).exists()) return false;
        }
//        System.out.println("MESH FILES EXIST");
        return true;
    }

    /**
     *
     * @param reference
     * @param query1
     * @param query2
     * @return
     */
    public static boolean meshMatch(JSONObject reference, JSONObject query1, JSONObject query2) {
        Map<String, Object> rMap = reference.toMap();
        Map<String, Object> q1Map = query1.toMap();
        Map<String, Object> q2Map = query2.toMap();

        for (String rKey : rMap.keySet()) {
            if (q1Map.containsKey(rKey) && q2Map.containsKey(rKey)) {
                // the current value from the reference
                Object rVal = rMap.get(rKey);

                // if that value is a Boolean and is TRUE, check corresponding values in query1 and query2
                if ((rVal instanceof Boolean) && ((Boolean) rVal)) {
                    // ^ is XOR operator
                    if ((q1Map.containsKey(rKey) ^ q2Map.containsKey(rKey)) || !q1Map.get(rKey).equals(q2Map.get(rKey))) {
//                        System.out.println("\t\tA value does not match here: " + q1Map.get(rKey).toString() + " and " + q2Map.get(rKey).toString());
                        return false; // a value DOES NOT MATCH
                    }
                }

                // rVal is NOT boolean
                else if (! (rVal instanceof Boolean)) {
                    // recurse!
                    boolean match = ModelSearcher.meshMatch(
                            new JSONObject((Map<String, Object>) rVal),
                            new JSONObject((Map<String, Object>) q1Map.get(rKey)),
                            new JSONObject((Map<String, Object>) q2Map.get(rKey))
                    );
                    if (! match) return false;
                }
                // in case that rVal is boolean: false, do nothing --> go to next key
            }
        }
        return true;
    }

    public static class Match {

        private JSONObject modelConfig;
        private Model mph;
        private IdentifierManager im;
        private String path;
        private HashMap<String, IdentifierManager> partPrimitiveIMs;

        public Match(JSONObject modelConfig, Model mph, IdentifierManager im, HashMap<String, IdentifierManager> partPrimitiveIMs, String path) {
            this.modelConfig = modelConfig;
            this.mph = mph;
            this.im = im;
            this.partPrimitiveIMs = partPrimitiveIMs;
            this.path = path;
        }

        /**
         *
         * @param path
         * @return
         */
        public static Match fromMeshPath(String path) {
            try {

                JSONObject modelConfig = JSONio.read(path + "/model.json");
                Model mph = ModelUtil.loadCopy(ModelUtil.uniquetag("Model"), path + "/mesh/mesh.mph");
                IdentifierManager im = IdentifierManager.fromJSONObject(JSONio.read(path + "/mesh/im.json"));

                HashMap<String, IdentifierManager> ppims = new HashMap<>();
                File ppimPath = new File(path + "/mesh/ppim/");
                for (String filename : Objects.requireNonNull(ppimPath.list())) {
                    String[] fileParts = filename.split("\\.");
//                    System.out.println("file path = " + ppimPath.toString() + "/" + filename);
                    ppims.put(
                            fileParts[0],
                            IdentifierManager.fromJSONObject(JSONio.read(ppimPath.toString() + "/" + filename))
                    );
                }

                return new Match(modelConfig, mph, im, ppims, path);

            } catch (IOException e) {
                e.printStackTrace();
                return null;
            }

        }

        public JSONObject getModelConfig() {
            return modelConfig;
        }

        public Model getMph() {
            return mph;
        }

        public IdentifierManager getIdm() {
            return im;
        }

        public String getPath() {
            return path;
        }

        public HashMap<String, IdentifierManager> getPartPrimitiveIMs() {
            return partPrimitiveIMs;
        }
    }
}

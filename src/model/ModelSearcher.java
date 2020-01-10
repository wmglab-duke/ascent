package model;

import com.comsol.model.Model;
import com.comsol.model.util.ModelUtil;
import org.json.JSONObject;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.Map;

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
    public ModelSearcher.Match searchMeshMatch(JSONObject query, JSONObject reference) throws IOException {

        for (Path file : Files.walk(this.root).toArray(Path[]::new)) {

            String[] fileParts = file.toString().split("/");

            if (fileParts[fileParts.length - 1].equals("model.json")) {

                JSONObject target = JSONio.read(file.toString());
                if (ModelSearcher.meshMatch(reference, query, target)) {
                    return Match.fromMeshPath(
                            String.join("/", Arrays.copyOfRange(fileParts, 0, fileParts.length - 1))
                    );
                }
            }
        }
        return null;
    }

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
                    if (!q1Map.get(rKey).equals(q2Map.get(rKey))) {
                        return false; // a value DOES NOT MATCH
                    }
                }

                // else, that value must be a JSONObject; therefore, recurse
                else {
                    assert rVal instanceof JSONObject;
                    ModelSearcher.meshMatch(
                            (JSONObject) rVal,
                            (JSONObject) q1Map.get(rKey),
                            (JSONObject) q2Map.get(rKey)

                    );
                }
            }
        }
        return true;
    }


    public static class Match {

        private JSONObject modelConfig;
        private Model mph;
        private IdentifierManager idm;

        public Match(JSONObject modelConfig, Model mph, IdentifierManager idm) {
            this.modelConfig = modelConfig;
            this.mph = mph;
            this.idm = idm;
        }

        /**
         *
         * @param path
         * @return
         */
        public static Match fromMeshPath(String path) {
            try {
                JSONObject modelConfig = JSONio.read(path + "/model.json");
                Model mph = ModelUtil.loadCopy("new_model", path + "/mesh/mesh.mph");
                IdentifierManager idm = IdentifierManager.fromJSONObject(JSONio.read(path + "/mesh/idm.json"));

                return new Match(modelConfig, mph,idm);

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
            return idm;
        }
    }
}

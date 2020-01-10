package model;

import com.comsol.model.Model;
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

                JSONObject target = new JSONReader(file.toString()).getData();
                if (ModelSearcher.meshMatch(query, reference, target)) {
                    return Match.fromPath(
                            String.join("/", Arrays.copyOfRange(fileParts, 0, fileParts.length - 1))
                    );
                }
            }
        }
        return null;
    }

    public static boolean meshMatch(JSONObject query, JSONObject reference, JSONObject target) {
        Map<String, Object> rMap = reference.toMap();
        Map<String, Object> qMap = query.toMap();
        Map<String, Object> tMap = target.toMap();

        for (String rKey : rMap.keySet()) {
            if (qMap.containsKey(rKey) && tMap.containsKey(rKey)) {
                // the current value from the reference
                Object rVal = rMap.get(rKey);

                // if that value is a Boolean and is TRUE, check corresponding values in query and target
                if ((rVal instanceof Boolean) && ((Boolean) rVal)) {
                    if (!qMap.get(rKey).equals(tMap.get(rKey))) {
                        return false; // a value DOES NOT MATCH
                    }
                }

                // else, that value must be a JSONObject; therefore, recurse
                else {
                    assert rVal instanceof JSONObject;
                    ModelSearcher.meshMatch(
                            (JSONObject) qMap.get(rKey),
                            (JSONObject) rVal,
                            (JSONObject) tMap.get(rKey)

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

        public static Match fromPath(String path) {
            // TODO;
            return null;
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

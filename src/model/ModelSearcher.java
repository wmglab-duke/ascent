/*
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
*/

package model;

import com.comsol.model.Model;
import com.comsol.model.util.ModelUtil;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import org.json.JSONObject;

@SuppressWarnings({ "FieldMayBeFinal", "unchecked", "path" })
public class ModelSearcher {

    private Path root;

    public ModelSearcher(String root) {
        this.setRoot(root);
    }

    public void setRoot(String root) {
        this.root = Paths.get(root);

        if (!Files.exists(this.root)) {
            this.root = null;
        }
    }

    /**
     *
     */
    public ModelSearcher.Match searchMeshMatch(JSONObject query, JSONObject reference)
        throws IOException {
        for (Path file : Files.walk(this.root).toArray(Path[]::new)) {
            String[] fileParts;
            String os = System.getProperty("os.name").toLowerCase();
            if (os.contains("win")) {
                // if windows
                fileParts = file.toString().split("\\\\");
            } else {
                // if unix-like
                fileParts = file.toString().split("/");
            }

            if (file.endsWith("model.json")) {
                JSONObject target = JSONio.read(file.toString());
                String directory = String.join(
                    "/",
                    Arrays.copyOfRange(fileParts, 0, fileParts.length - 1)
                );
                if (
                    ModelSearcher.meshMatch(reference, query, target) &&
                    ModelSearcher.meshFilesExist(directory)
                ) {
                    System.out.println("\tSkipping meshing because found mesh match: " + directory);
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
            directory + "/mesh/im.json",
        };
        for (String filename : filenames) {
            if (!new File(filename).exists()) return false;
        }
        return true;
    }

    /**
     *
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
                    if (
                        (q1Map.containsKey(rKey) ^ q2Map.containsKey(rKey)) ||
                        !q1Map.get(rKey).equals(q2Map.get(rKey))
                    ) {
                        return false; // a value DOES NOT MATCH
                    }
                }
                // rVal is NOT boolean
                else if (!(rVal instanceof Boolean)) {
                    boolean match;
                    if (rKey.equals("cuff")) {
                        match = q1Map.get(rKey).equals(q2Map.get(rKey));
                    } else {
                        // recurse!
                        match =
                            ModelSearcher.meshMatch(
                                new JSONObject((Map<String, Object>) rVal),
                                new JSONObject((Map<String, Object>) q1Map.get(rKey)),
                                new JSONObject((Map<String, Object>) q2Map.get(rKey))
                            );
                    }
                    if (!match) return false;
                }
                // in case that rVal is boolean: false, do nothing --> go to next key
            }
        }
        return true;
    }

    public static class Match {

        private Model mph;
        private IdentifierManager im;
        private String path;
        private HashMap<String, IdentifierManager> partPrimitiveIMs;

        public Match(
            Model mph,
            IdentifierManager im,
            HashMap<String, IdentifierManager> partPrimitiveIMs,
            String path
        ) {
            this.mph = mph;
            this.im = im;
            this.partPrimitiveIMs = partPrimitiveIMs;
            this.path = path;
        }

        /**
         *
         */
        public static Match fromMeshPath(String path) {
            try {
                Model mph = ModelUtil.loadCopy(
                    ModelUtil.uniquetag("Model"),
                    path + "/mesh/mesh.mph"
                );
                IdentifierManager im = IdentifierManager.fromJSONObject(
                    JSONio.read(path + "/mesh/im.json")
                );

                HashMap<String, IdentifierManager> ppims = new HashMap<>();
                File ppimPath = new File(path + "/mesh/ppim/");
                for (String filename : Objects.requireNonNull(ppimPath.list())) {
                    String[] fileParts = filename.split("\\.");
                    ppims.put(
                        fileParts[0],
                        IdentifierManager.fromJSONObject(JSONio.read(ppimPath + "/" + filename))
                    );
                }

                return new Match(mph, im, ppims, path);
            } catch (IOException e) {
                e.printStackTrace();
                return null;
            }
        }

        public Model getMph() {
            return mph;
        }

        public IdentifierManager getIdm() {
            return im;
        }

        public HashMap<String, IdentifierManager> getPartPrimitiveIMs() {
            return partPrimitiveIMs;
        }
    }
}

package model;

import com.comsol.model.Model;
import org.json.JSONObject;

public class ModelSearcher {

    private String root;

    public ModelSearcher(String root) {
        this.root = root;
    }

    public ModelSearcher.Match[] searchMeshMatch(JSONObject targetConfig) {

        return null;
    }

    public void setRoot(String root) {
        this.root = root;
    }

    public String getRoot() {
        return root;
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

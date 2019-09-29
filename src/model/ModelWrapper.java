package model;

import java.util.Set;

public class ModelWrapper {

    private Object model;
    private String projectPath;
    private Set<String> parts;
    private ComsolIdentifierManager cim;

    ModelWrapper(Object model, String projectPath, Set<String> parts, ComsolIdentifierManager cim) {
        this.model = model;
        this.projectPath = projectPath;
        this.parts = parts;
        this.cim = cim;
    }

    public Object getModel() {
        return model;
    }

    public String getProjectPath() {
        return projectPath;
    }

    public Set<String> getParts() {
        return parts;
    }

    ComsolIdentifierManager getCIM() {
        return cim;
    }
}

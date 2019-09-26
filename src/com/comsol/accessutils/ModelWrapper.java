package com.comsol.accessutils;

import java.util.Set;

public class ModelWrapper {

    private Object model;
    private String projectPath;
    private Set<String> parts;
    //CIM

    public ModelWrapper(Object model, String projectPath, Set parts) {
        this.model = model;
        this.projectPath = projectPath;
        this.parts = parts;
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
}

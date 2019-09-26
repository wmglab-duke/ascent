package com.comsol.accessutils;

import com.comsol.model.Model;
import java.util.Set;

public class ModelWrapper {

    private Model model;
    private String projectPath;
    public Set<String> parts;

    public ModelWrapper(Model model, String projectPath, Set parts) {
        this.model = model;
        this.projectPath = projectPath;
        this.parts = parts;
    }

    public Model getModel() {
        return model;
    }

    public String getProjectPath() {
        return projectPath;
    }

    public Set<String> getParts() {
        return parts;
    }
}

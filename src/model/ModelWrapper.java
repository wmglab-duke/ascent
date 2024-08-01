/*
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
*/

package model;

import com.comsol.model.*;
import com.comsol.model.physics.PhysicsFeature;
import com.comsol.model.util.ModelUtil;
import com.comsol.util.exceptions.FlException;
import java.io.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.regex.Pattern;
import org.json.JSONArray;
import org.json.JSONObject;

/**
 * model.ModelWrapper
 * Master high-level class for managing a model, its metadata, and various critical operations such as creating parts,
 * assigning physics, and extracting potentials. This class houses the "meaty" operations of actually interacting with
 * the model object when creating parts in the static class model. Parts.
 */

@SuppressWarnings({ "FieldMayBeFinal", "path" })
public class ModelWrapper {

    // UNION PSEUDONYM CONSTANTS
    public static final String ALL_NERVE_PARTS_UNION = "allNervePartsUnion";
    public static final String ENDO_UNION = "endoUnion";
    public static final String PERI_UNION = "periUnion";

    // if these change, also need to change in createEnvironmentPartInstance
    public static final String DISTAL_MEDIUM = "DistalMedium";
    public static final String PROXIMAL_MEDIUM = "ProximalMedium";

    public static final String[] ALL_UNIONS = new String[] {
        ModelWrapper.ENDO_UNION,
        ModelWrapper.ALL_NERVE_PARTS_UNION,
        ModelWrapper.PERI_UNION,
    };
    // associated union contributors for above constants
    private HashMap<String, ArrayList<String>> unionContributors = new HashMap<>();

    // INSTANCE VARIABLES
    private Model model; // model

    public IdentifierManager im = new IdentifierManager(); // top level identifier manager
    public static IdentifierManager ve_im = new IdentifierManager(); // top level identifier manager

    private HashMap<String, IdentifierManager> partPrimitiveIMs = new HashMap<>(); // for managing parts within COMSOL

    // directory structure
    private String root;

    // CONSTRUCTORS
    /**
     * Default constructor (minimum of 2 arguments)
     * @param model com.comsol.model.Model object is REQUIRED
     * @param projectRoot the root directory of the project (might remove if unnecessary)
     */
    ModelWrapper(Model model, String projectRoot) {
        this.model = model;
        this.root = projectRoot;
        this.initUnionContributors();
    }

    // ACCESSOR/MUTATOR METHODS
    /**
     * @return the model
     */
    public Model getModel() {
        return model;
    }

    /**
     * @return the root of the project (String path)
     */
    public String getRoot() {
        return root;
    }

    /**
     * @param root set the project root (String path)
     */
    public void setRoot(String root) {
        this.root = root;
    }

    // OTHER METHODS
    /**
     * Call method on im (IdentifierManager)... see class for details
     */
    public String next(String key) {
        return this.im.next(key);
    }

    /**
     * Call method on im (IdentifierManager)... see class for details
     */
    public String next(String key, String pseudonym) {
        return this.im.next(key, pseudonym);
    }

    /**
     * Call method on im (IdentifierManager)... see class for details
     */
    public String get(String psuedonym) {
        return this.im.get(psuedonym);
    }

    /**
     * @param partPrimitiveLabel the name of the part primitive (i.e. "TubeCuff_Primitive")
     * @return the associated IdentifierManager, for correct intra-part indexing
     */
    public IdentifierManager getPartPrimitiveIM(String partPrimitiveLabel) {
        return this.partPrimitiveIMs.get(partPrimitiveLabel);
    }

    /**
     * @param destination full path to save to
     * @return success indicator
     */
    public boolean save(String destination) {
        try {
            this.model.save(destination);
            return true;
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
    }

    /**
     * Create the required primitives for a given cuff json
     *
     * @param name json filename WITH extension (i.e. "LivaNova2000.json")
     */
    public void addCuffPartPrimitives(String name) {
        // extract data from json
        try {
            // Only add primitives if this is the first time for this cuff
            if (!this.im.hasPseudonym(name)) {
                JSONObject cuffData = JSONio.read(
                    String.join("/", new String[] { this.root, "config", "system", "cuffs", name })
                );

                // get the id for the next "par" (i.e., parameters section), and give it a name from the JSON file name. */
                String id = this.next("par", name);
                model.param().group().create(id);
                model.param(id).label(name.split("\\.")[0] + " Parameters");

                // loop through all parameters in file, and set in parameters
                for (Object item : (JSONArray) cuffData.get("params")) {
                    JSONObject itemObject = (JSONObject) item;
                    model
                        .param(id)
                        .set(
                            (String) itemObject.get("name"),
                            (String) itemObject.get("expression"),
                            (String) itemObject.get("description")
                        );
                }

                // for each required part primitive, create it (if not already existing)
                for (Object item : (JSONArray) cuffData.get("instances")) {
                    JSONObject itemObject = (JSONObject) item;
                    String partPrimitiveName = (String) itemObject.get("type"); // quick cast to String

                    // create the part primitive if it has not already been created
                    if (!this.im.hasPseudonym(partPrimitiveName)) {
                        // get next available (TOP LEVEL) "part" id
                        String partID = this.im.next("part", partPrimitiveName);
                        try {
                            // TRY to create the part primitive (catch error if no existing implementation)
                            IdentifierManager partPrimitiveIM = Part.createCuffPartPrimitive(
                                partID,
                                partPrimitiveName,
                                this
                            );

                            // add the returned id manager to the HashMap of IMs with the partName as its key
                            this.partPrimitiveIMs.put(partPrimitiveName, partPrimitiveIM);
                        } catch (IllegalArgumentException e) {
                            e.printStackTrace();
                        }
                    }
                }
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    }

    /**
     * Instantiate required primitives for given cuff
     * NOTE: addCuffPartPrimitives() MUST be called first or there will be no primitives to instantiate.
     *
     * @param name same formatting as in addCuffPartPrimitives()
     */
    public void addCuffPartInstances(String name, int cuffNum, int cuffIndex) {
        // extract data from json (name is something like Enteromedics.json)
        try {
            JSONObject cuffData = JSONio.read(
                String.join("/", new String[] { this.root, "config", "system", "cuffs", name })
            );

            // loop through all part instances
            for (Object item : (JSONArray) cuffData.get("instances")) {
                JSONObject itemObject = (JSONObject) item;

                // add cuff cuffNum to instance label
                String instanceLabel = "Cuff " + cuffNum + "_" + itemObject.get("label");
                String instanceID = this.im.next("pi", instanceLabel);
                String type = (String) itemObject.get("type");
                String cuffName = name.split("\\.")[0];
                Part.createCuffPartInstance(
                    instanceID,
                    instanceLabel,
                    type,
                    this,
                    itemObject,
                    cuffName,
                    cuffNum,
                    cuffIndex
                );
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    }

    /**
     * Assign previously defined materials to domains in part instances
     *
     * @param cuffData is loaded JSON data for a defined cuff
     */
    public void addCuffPartMaterialAssignments(JSONObject cuffData, int cuff_num) {
        // extract data from json, its name is something like Enteromedics.json
        // loop through all part instances
        for (Object item : (JSONArray) cuffData.get("instances")) {
            JSONObject itemObject = (JSONObject) item;

            //add cuff cuff_num to instance label
            String instanceLabel = "Cuff " + cuff_num + "_" + itemObject.get("label");
            String type = (String) itemObject.get("type");

            Part.addCuffPartMaterialAssignment(instanceLabel, type, this, itemObject);
        }
    }

    /**
     * Create materials necessary for fascicles, nerve, surrounding media, etc.
     */
    public void addMaterialDefinitions(
        ArrayList<String> materials,
        JSONObject modelData,
        ModelParamGroup materialParams
    ) {
        try {
            // load system defined materials JSON into memory
            JSONObject materialsData = JSONio.read(
                String.join("/", new String[] { this.root, "config", "system", "materials.json" })
            );

            // add material definition for those materials that are needed in the instantiated parts
            for (String function : materials) {
                if (!this.im.hasPseudonym(function)) {
                    String materialID = this.im.next("mat", function);
                    Part.defineMaterial(
                        materialID,
                        function,
                        modelData,
                        materialsData,
                        this,
                        materialParams
                    );
                }
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    }

    /**
     * @return success indicator
     */
    public static double[] extractPotentials(Model model, String coords_path) throws IOException {
        // Load coordinates (x,y,z) from file in form: top line is number of rows of coords (int)
        //                                             coordinates[0][i] = [x] in micron, (double)
        //                                             coordinates[1][i] = [y] in micron, (double)
        //                                             coordinates[2][i] = [z] in micron  (double)

        // read in coords for axon segments as defined and saved to file in Python.
        double[][] coordinatesLoaded;
        coordinatesLoaded = readCoords(coords_path);

        // transpose saved coordinates (we like to save (x,y,z) as column vectors, but COMSOL wants as rows)
        double[][] coordinates;
        assert coordinatesLoaded != null;
        coordinates = transposeMatrix(coordinatesLoaded);

        // get Ve from COMSOL

        String id = ve_im.next("interp");
        model.result().numerical().create(id, "Interp");
        model.result().numerical(id).set("expr", "V");
        model.result().numerical(id).set("recover", "pprint");
        model.result().numerical(id).set("matherr", "on");
        model.result().numerical(id).setInterpolationCoordinates(coordinates);
        double[][][] ve_pre = model.result().numerical(id).getData();
        int len = ve_pre[0][0].length; // number of coordinates

        double[] ve = new double[len];
        System.arraycopy(ve_pre[0][0], 0, ve, 0, len);
        return ve;
    }

    /**
     * For each fiber set created on the Python side of things, extract potentials and save to file
     * @param projectPath Path of ASCENT root
     * @param run_path Path of run config
     */
    public static void extractAllPotentials(String projectPath, String run_path, String modelStr)
        throws IOException {
        System.out.println("\tExtracting/writing all potentials - skips if file already exists");

        // READ IN RUN CONFIGURATION DATA
        JSONObject runData = JSONio.read(run_path);
        // get sample number
        int sample = runData.getInt("sample");
        // get sims list
        JSONArray sims_list = runData.getJSONArray("sims");

        // GET BASES FOR EACH MODEL (SET UP SO THAT LOADS EACH BASE MPH FILE ONLY ONCE → SPEED)
        // load model config data.
        String model_path = String.join(
            "/",
            new String[] { // build path to sim config file
                projectPath,
                "samples",
                Integer.toString(sample),
                "models",
                modelStr,
            }
        );

        // construct bases path (to MPH)
        String bases_directory = String.join("/", new String[] { model_path, "bases" });

        // get bases at the bases MPH path
        String[] bases_files = new File(bases_directory).list();
        assert bases_files != null;
        bases_files =
            Arrays
                .stream(bases_files)
                .filter(s -> Pattern.matches("[0-9]_Cuff\\s[0-9]+_[a-zA-Z0-9 ]+\\.mph", s))
                .toArray(String[]::new);
        Arrays.sort(bases_files); // Now that bases files contain descriptive cuff strings, sort the values to avoid errors with later cuff indexing.

        // LOOP OVER BASES
        for (int basis_ind = 0; basis_ind < bases_files.length; basis_ind++) {
            assert basis_ind == Integer.parseInt(bases_files[basis_ind].split("_")[0]): "Issues in bases indexing.";

            // LOAD BASIS MPH MODEL
            String basis_dir = String.join(
                "/",
                new String[] { bases_directory, bases_files[basis_ind] } // + ".mph" }
            );

            File basis_file = new File(basis_dir);
            while (!basis_file.canWrite() || !basis_file.canRead()) {
                System.out.println("\twaiting");
            }
            String model_tag = ModelUtil.uniquetag("Model");
            Model basis = ModelUtil.load(model_tag, basis_dir);

            // LOOP OVER SIMS
            for (int sim_ind = 0; sim_ind < sims_list.length(); sim_ind++) { // loop over sims
                // build path to directory of sim
                String sim_dir = String.join(
                    "/",
                    new String[] { model_path, "sims", sims_list.get(sim_ind).toString() }
                );

                // GET FIBERSETS
                // build path to directory of fibersets, make sure they have fibers
                String fibersets_dir = String.join("/", new String[] { sim_dir, "fibersets" });
                File fibersets_file = new File(fibersets_dir);
                File[] fibersets_file_list = fibersets_file.listFiles();
                assert fibersets_file_list != null;

                // build path to directory of ve for each fiberset (all bases)
                String fibersets_bases_dir = String.join(
                    "/",
                    new String[] { sim_dir, "fibersets_bases" }
                );
                // SUPER SAMPLING COORDS
                // build path to direction of ss_coords
                String ss_coords_dir = String.join("/", new String[] { sim_dir, "ss_coords" });
                File ss_coords_file = new File(ss_coords_dir);
                // are we super sampling in this Sim?
                Boolean do_ss = ss_coords_file.isDirectory();

                // directory for ss_basis
                String ss_basis_dir = String.join(
                    "/",
                    new String[] { sim_dir, "ss_bases", String.valueOf(basis_ind) }
                );

                // LOOP OVER FIBERSETS
                for (
                    int fiberset_ind = 0;
                    fiberset_ind < fibersets_file_list.length;
                    fiberset_ind++
                ) {
                    // build path to directory of fiberseT
                    String fiberset_dir = String.join(
                        "/",
                        new String[] { fibersets_dir, Integer.toString(fiberset_ind) }
                    );
                    File fiberset_file = new File(fiberset_dir);

                    String[] fiberset_file_list = fiberset_file.list();
                    assert fiberset_file_list != null;

                    // build path to directory of fiberset basis
                    String ve_fiberset_basis_dir = String.join(
                        "/",
                        new String[] {
                            fibersets_bases_dir,
                            Integer.toString(fiberset_ind),
                            Integer.toString(basis_ind),
                        }
                    );

                    // if fiberset_basis_potentials directory does not yet exist, make it
                    File ve_fiberset_basis_file = new File(ve_fiberset_basis_dir);
                    if (!ve_fiberset_basis_file.exists()) {
                        boolean success = ve_fiberset_basis_file.mkdirs();
                        assert success;
                    }

                    // LOOP OVER FIBERS IN FIBERSET
                    for (String fiber_file : fiberset_file_list) {
                        if (
                            !fiber_file.contains("diams.txt") && !fiber_file.contains("offsets.txt")
                        ) {
                            // build path to fibeR
                            String[] fiber_file_parts = fiber_file.split("\\.");
                            Integer fiber_file_ind = Integer.parseInt(fiber_file_parts[0]);

                            manageExtractPotentials(
                                basis,
                                fiber_file_ind,
                                fiberset_dir,
                                ve_fiberset_basis_dir,
                                do_ss,
                                ss_coords_dir,
                                ss_basis_dir
                            );
                        }
                    }
                }
            }
            // remove basis from memory
            ModelUtil.remove(basis.tag());
        }
    }

    private static void manageExtractPotentials(
        Model basis,
        Integer fiber_file_ind,
        String fiberset_dir,
        String ve_fiberset_basis_dir,
        Boolean do_ss,
        String ss_coords_dir,
        String ss_basis_dir
    ) throws IOException {
        String fiber_ve_path = String.join(
            "/",
            new String[] { ve_fiberset_basis_dir, fiber_file_ind + ".dat" }
        );
        // DEAL WITH EXTRACTING POTENTIALS (FOR BASIS) FOR SUPERSAMPLING COORDS
        // Skip if file already exists
        if (!new File(fiber_ve_path).exists()) {
            // EXTRACT POTENTIALS (FOR BASIS) FOR FIBER
            String coords_path = String.join(
                "/",
                new String[] { fiberset_dir, fiber_file_ind + ".dat" }
            ); // build path to coordinates

            // GET POTENTIALS COMSOL
            double[] ve = extractPotentials(basis, coords_path);

            // SAVE POTENTIALS FROM COMSOL
            writeVe(ve, fiber_ve_path);

            if (do_ss) {
                // if ss_basis_potentials directory does not yet exist, make it
                File ss_basis_file = new File(ss_basis_dir);
                if (!ss_basis_file.exists()) {
                    boolean success = ss_basis_file.mkdirs();
                    assert success;
                }

                // check if super sampled basis exists
                String ss_ve_path = String.join(
                    "/",
                    new String[] { ss_basis_dir, fiber_file_ind + ".dat" }
                );

                // If the potentials for this fiberset/basis/fiber have been created, move on
                if (!new File(ss_ve_path).exists()) {
                    // EXTRACT POTENTIALS FOR SUPERSAMPLED COORDS
                    String ss_coords_path = String.join(
                        "/",
                        new String[] { ss_coords_dir, fiber_file_ind + ".dat" }
                    ); // build path to ss coordinates

                    // GET POTENTIALS FROM COMSOL
                    double[] ss_ve = extractPotentials(basis, ss_coords_path);

                    // SAVE POTENTIALS FROM COMSOL
                    writeVe(ss_ve, ss_ve_path);
                }
            }
        }
    }

    public static double[][] transposeMatrix(double[][] m) {
        // pre-allocated array of doubles for transposed matrix
        double[][] temp = new double[m[0].length][m.length];

        for (int i = 0; i < m.length; i++) for (int j = 0; j < m[0].length; j++) temp[j][i] =
            m[i][j];
        return temp;
    }

    private static void writeVe(double[] ve, String ve_path) throws IOException {
        PrintWriter printWriter = new PrintWriter(ve_path);
        int len = ve.length; // number of coordinates

        // write to file: number of coordintates top line,
        // then one Ve value for each coordinate  (x,y,z) for subsequent lines
        printWriter.println(len);
        for (double v : ve) {
            printWriter.println(v);
        }
        printWriter.close(); // close printWriter
    }

    public static double[][] readCoords(String coords_path) throws FileNotFoundException {
        File f = new File(coords_path);
        Scanner scan = new Scanner(f);

        String thisLine;
        try {
            // save rows (number of coords) at top line... so number of lines in file is (number of coords +1)
            String rows = scan.nextLine();
            int n_rows = Integer.parseInt(rows.trim());

            // pre-allocated array of doubles for coords in file (3 columns by default for (x,y,z)
            double[][] coords = new double[n_rows][3];
            int row_ind = 0;

            // while there are more lines to scan
            while (scan.hasNextLine()) {
                thisLine = scan.nextLine();
                String[] parts = thisLine.split("\\s+");
                for (int i = 0; i < parts.length; i++) {
                    coords[row_ind][i] = Double.parseDouble(parts[i]);
                }
                row_ind++;
            }

            if (n_rows != row_ind) {
                throw new Exception(
                    "Number of coordinates (rows) in coords file " +
                    "does not match header in file: " +
                    coords_path
                );
            }

            scan.close();
            return coords;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    /**
     * Add all fascicles to model.
     */
    public void addNerve(String sample, ModelParamGroup nerveParams, JSONObject modelData) {
        // define global nerve part names (MUST BE IDENTICAL IN Part)
        String[] fascicleTypes = new String[] { "FascicleCI", "FascicleMesh" };

        // Load configuration file
        try {
            JSONObject sampleData = JSONio.read(
                String.join("/", new String[] { this.root, "samples", sample, "sample.json" })
            );

            // Build path to fascicles
            String fasciclesPath = String.join(
                "/",
                new String[] {
                    this.root,
                    "samples",
                    sample,
                    "slides",
                    "0",
                    "0",
                    "sectionwise2d",
                    "fascicles",
                }
            );
            // Build path to nerve trace
            String nervePath = String.join(
                "/",
                new String[] {
                    this.root,
                    "samples",
                    sample,
                    "slides",
                    "0",
                    "0",
                    "sectionwise2d",
                    "nerve",
                    "0",
                }
            );

            // nerve trace filename
            HashMap<String, String[]> ndata = new HashMap<>();
            ndata.put("nerve", new String[] { "0.txt" });

            // Add epineurium
            String nerveMode = (String) sampleData.getJSONObject("modes").get("nerve");
            String reshapenerveMode = (String) sampleData
                .getJSONObject("modes")
                .get("reshape_nerve");

            // backwards compatibility
            double deform_ratio = 0;
            if (sampleData.has("deform_ratio")) {
                deform_ratio = sampleData.getDouble("deform_ratio");
            } else {
                if (reshapenerveMode.equals("CIRCLE")) {
                    deform_ratio = 1;
                } else if (reshapenerveMode.equals("NONE")) {
                    deform_ratio = 0;
                }
            }

            if (
                nerveMode.equals("PRESENT") &&
                !(reshapenerveMode.equals("CIRCLE") || reshapenerveMode.equals("NONE"))
            ) {
                System.out.println(
                    "Modeling Sample with epineurium (i.e., Nerve Trace) that is not deformed toward a" +
                    "CIRCLE (or NONE) is not yet implemented"
                );
                System.exit(0);
            }

            if (nerveMode.equals("PRESENT")) {
                if (deform_ratio == 1 && reshapenerveMode.equals("CIRCLE")) { //Use a circle otherwise
                    Part.createNervePartInstance(
                        "Epi_circle",
                        0,
                        null,
                        this,
                        null,
                        sampleData,
                        nerveParams,
                        modelData
                    );
                } else { //Use trace
                    Part.createNervePartInstance(
                        "Epi_trace",
                        0,
                        nervePath,
                        this,
                        ndata,
                        sampleData,
                        nerveParams,
                        modelData
                    );
                }
            }

            // Loop over all fascicle dirs
            String[] dirs = new File(fasciclesPath).list();

            JSONObject modelModes = modelData.getJSONObject("modes"); //

            if (dirs != null) {
                for (String dir : dirs) {
                    if (!dir.contains(".")) {
                        int index = Integer.parseInt(dir);
                        // Initialize data to send to Part.createPartInstance
                        HashMap<String, String[]> data = new HashMap<>();
                        // Add inners and outer files to array
                        String path = String.join("/", new String[] { fasciclesPath, dir });
                        for (String type : new String[] { "inners", "outer" }) {
                            data.put(
                                type,
                                new File(String.join("/", new String[] { path, type })).list()
                            );
                        }

                        // Quick loop to make sure there are at least one of each inner and outer
                        for (String[] arr : data.values()) {
                            if (arr.length < 1) throw new IllegalStateException(
                                "There must be at least one of each inner and outer for fascicle " +
                                index
                            );
                        }

                        String fascicleType;
                        if (modelModes.has("use_ci") && !modelModes.getBoolean("use_ci")) {
                            fascicleType = fascicleTypes[1]; // "FascicleMesh"
                        } else {
                            // do "FascicleCI" if only one inner, "FascicleMesh" otherwise
                            fascicleType =
                                data.get("inners").length == 1
                                    ? fascicleTypes[0]
                                    : fascicleTypes[1];
                        }

                        // hand off to Part to build instance of fascicle
                        Part.createNervePartInstance(
                            fascicleType,
                            index,
                            path,
                            this,
                            data,
                            sampleData,
                            nerveParams,
                            modelData
                        );
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * Pre-built for-loop to iterate through all current sources in model (added in Part)
     * Can be super useful for quickly setting different currents and possibly sweeping currents
     */
    public void loopCurrents(
        JSONObject modelData,
        String projectPath,
        String sample,
        String modelStr,
        Boolean skipMesh,
        boolean pre_solve_break,
        boolean[] basesValid
    ) {
        long runSolStartTime = System.nanoTime();
        // int index = 0;

        Set<Integer> s;
        s = this.im.currentIDs.keySet();

        for (int key_on_int = 0; key_on_int < s.size(); key_on_int++) {
            String key_on;
            String src;

            if (skipMesh) {
                String key_on_int_str = Integer.toString(key_on_int + 1);
                Map key_on_obj = (Map) this.im.currentIDs.get(key_on_int_str);
                key_on = key_on_int + "_" + key_on_obj.get("name");
                src = (String) key_on_obj.get("pcs");
            } else {
                JSONObject key_on_obj = this.im.currentIDs.get(key_on_int + 1);
                key_on = key_on_int + "_" + key_on_obj.getString("name");
                src = (String) key_on_obj.get("pcs");
            }

            PhysicsFeature current_on = model.physics("ec").feature(src);
            current_on.set("Qjp", 0.001); // turn on current

            String bases_directory = String.join(
                "/",
                new String[] { projectPath, "samples", sample, "models", modelStr, "bases" }
            );

            // if bases directory does not yet exist, make it
            File basesPathFile = new File(bases_directory);
            if (!basesPathFile.exists()) {
                boolean success = basesPathFile.mkdirs();
                assert success;
            }

            String mphFile = String.join(
                "/",
                new String[] {
                    projectPath,
                    "samples",
                    sample,
                    "models",
                    modelStr,
                    "bases",
                    key_on + ".mph",
                }
            );

            //if no bases are valid, must resolve all, even if file exists
            boolean resolveAll = !anyTrue(basesValid);
            System.out.println("\tSolving electric currents for " + key_on + ".");

            boolean save = true;
            if (!new File(mphFile).exists() || resolveAll) {
                if (!pre_solve_break) {
                    model.sol("sol1").runAll();
                    model.component("comp1").mesh("mesh1").clearMesh();
                } else {
                    System.out.println(
                        "\tSkipped solving for basis " +
                        key_on +
                        " because encountered pre_solve breakpoint. Basis MPH will be saved with no solution."
                    );
                }
            } else {
                save = false;
                System.out.println(
                    "\tSkipping solving and saving for basis " +
                    key_on +
                    " because found existing file: " +
                    mphFile
                );
            }

            try {
                if (save) {
                    System.out.println("\tSaving MPH (mesh and solution) file to: " + mphFile);
                    model.save(mphFile);

                    File mphFileFile = new File(mphFile);

                    while (!mphFileFile.canWrite() || !mphFileFile.canRead()) {
                        System.out.println("\twaiting");
                        // wait!
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }

            current_on.set("Qjp", 0.000); // reset current
            // index += 1;
        }

        JSONObject solution = new JSONObject();
        long estimatedRunSolTime = System.nanoTime() - runSolStartTime;
        solution.put("sol_time", estimatedRunSolTime / Math.pow(10, 6)); // convert nanos to millis, this is for solving all contacts
        String version = ModelUtil.getComsolVersion(); //The getComsolVersion method returns the current COMSOL Multiphysics
        solution.put("name", version);
        modelData.put("solution", solution);
    }

    /**
     * Call only from initializer!
     * Initialize the ArrayLists in the unionContributors HashMap
     */
    public void initUnionContributors() {
        for (String unionLabel : ModelWrapper.ALL_UNIONS) {
            this.unionContributors.put(unionLabel, new ArrayList<>());
        }
    }

    /**
     * Add string id for COMSOL element to the listed unions (which have not been "created" in COMSOL yet)
     * @param contributor the string id to add (use actual id, not pseudonym)
     * @param unions which unions to add it to  (use static pseudonym constants at top of class)
     */
    public void contributeToUnions(String contributor, String[] unions) {
        for (String union : unions) {
            this.unionContributors.get(union).add(contributor);
        }
    }

    /**
     * @param union which union to from of which to get the contributors
     * @return String array of the COMSOL id's of contributors (likely ext# or csel#)
     */
    public String[] getUnionContributors(String union) {
        if (!this.unionContributors.containsKey(union)) throw new IllegalArgumentException(
            "No such union: " + union
        );
        return this.unionContributors.get(union).toArray(new String[0]);
    }

    /**
     * Actually create the unions by looping through all defined ArrayLists and adding contents to a new union.
     * Will not create a union of no elements in associated ArrayList (i.e. no Peri union if only contact impedance)
     */
    public void createUnions() {
        for (String union : ModelWrapper.ALL_UNIONS) {
            String[] contributors = this.getUnionContributors(union);

            if (contributors.length > 0) {
                GeomFeature uni = model
                    .component("comp1")
                    .geom("geom1")
                    .create(im.next("uni", union), "Union");
                uni.set("keep", true);
                uni.selection("input").set(contributors);
                uni.label(union);

                String unionCselLabel = union + "Csel";
                GeomObjectSelectionFeature csel = model
                    .component("comp1")
                    .geom("geom1")
                    .selection()
                    .create(im.next("csel", unionCselLabel), "CumulativeSelection");
                csel.label(unionCselLabel);

                uni.set("contributeto", im.get(unionCselLabel));
            }
        }
    }

    static boolean deleteDir(File file) {
        File[] contents = file.listFiles();
        if (contents != null) {
            for (File f : contents) {
                deleteDir(f);
            }
        }
        return file.delete();
    }

    /**
     * Master procedure to run!
     * @param args command line arguments
     */
    public static void main(String[] args) throws InterruptedException {
        JSONObject cli_args = getCLI(args);

        //connect to comsol server
        ModelWrapper.serverConnect();

        setShowProgress(cli_args);

        //checkout comsol license
        if (cli_args.has("wait_for_license") && !cli_args.isNull("wait_for_license")) {
            long waitHours = cli_args.getLong("wait_for_license");
            ModelWrapper.licenseCheckout(waitHours);
        }

        // Take projectPath input to ModelWrapper and assign to string.
        String projectPath = args[0];

        // Load RUN configuration data
        String runPath = args[1]; // Take runPath input to ModelWrapper and assign to string

        JSONObject run = null;
        try {
            run = JSONio.read(runPath);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

        assert run != null;
        JSONArray models_list = run.getJSONArray("models"); // get array of COMSOL models
        String break_point = null;
        if (!cli_args.isNull("break_point")) {
            break_point = cli_args.getString("break_point");
        }
        boolean endo_only_solution = false;
        if (cli_args.has("endo_only_solution") && cli_args.getBoolean("endo_only_solution")) {
            endo_only_solution = true;
        } else if (run.has("endo_only_solution") && run.getBoolean("endo_only_solution")) {
            endo_only_solution = true;
        }

        boolean nerve_only = false;
        boolean cuff_only = false;
        if (!cli_args.isNull("partial_fem")) {
            if (cli_args.getString("partial_fem").equals("cuff_only")) {
                cuff_only = true;
            } else if (cli_args.getString("partial_fem").equals("nerve_only")) {
                nerve_only = true;
            }
        }

        String sample;
        JSONObject sampleData = null;
        String sampleFile;
        // Load SAMPLE configuration data
        sample = String.valueOf(Objects.requireNonNull(run).getInt("sample"));
        sampleFile = String.join("/", new String[] { "samples", sample, "sample.json" });
        try {
            sampleData = JSONio.read(projectPath + "/" + sampleFile);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

        // Load mesh_dependence_model configuration data
        JSONObject meshReferenceData = null;
        try {
            meshReferenceData =
                JSONio.read(
                    String.join(
                        "/",
                        new String[] {
                            projectPath,
                            "config",
                            "system",
                            "mesh_dependent_model.json",
                        }
                    )
                );
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

        // variables for optimization looping
        boolean skipMesh;

        // loop MODELS
        boolean[] models_exit_status = new boolean[models_list.length()];
        for (int model_index = 0; model_index < models_list.length(); model_index++) {
            try {
                Model model = null;
                ModelWrapper mw = null;
                skipMesh = false;

                String modelStr = String.valueOf(models_list.get(model_index));
                String bases_directory = String.join(
                    "/",
                    new String[] { projectPath, "samples", sample, "models", modelStr, "bases" }
                );

                System.out.println("BEGIN RUN - Model " + modelStr);

                // if bases directory does not yet exist, make it. If it exists, check that the bases are valid
                File basesPathFile = new File(bases_directory);
                boolean[] basesValid = areBasesValid(
                    projectPath,
                    sample,
                    modelStr,
                    bases_directory,
                    basesPathFile
                );

                String modelFile;
                if ((!allTrue(basesValid)) || nerve_only || cuff_only) {
                    // Load MODEL configuration data
                    modelFile =
                        String.join(
                            "/",
                            new String[] { "samples", sample, "models", modelStr, "model.json" }
                        );
                    JSONObject modelData = null;
                    try {
                        modelData = JSONio.read(projectPath + "/" + modelFile);
                    } catch (FileNotFoundException e) {
                        System.out.println("\tFailed to read MODEL config data.");
                        e.printStackTrace();
                    }

                    assert modelData != null;
                    modelData.put("solution", JSONObject.NULL);

                    try (FileWriter file = new FileWriter(projectPath + "/" + modelFile)) {
                        String output = modelData.toString(2);
                        file.write(output);
                    } catch (IOException e) {
                        e.printStackTrace();
                    }

                    // if optimizing
                    boolean recycle_meshes = false;
                    if (run.has("recycle_meshes") && !nerve_only && !cuff_only) {
                        recycle_meshes = run.getBoolean("recycle_meshes");
                    }

                    if (recycle_meshes) {
                        System.out.println("\tEntering mesh recycling logic.");
                        try {
                            ModelSearcher modelSearcher = new ModelSearcher(
                                String.join(
                                    "/",
                                    new String[] { projectPath, "samples", sample, "models" }
                                )
                            );
                            ModelSearcher.Match meshMatch = modelSearcher.searchMeshMatch(
                                modelData,
                                meshReferenceData
                            );

                            // if there was a mesh match
                            if (meshMatch != null) {
                                model = meshMatch.getMph();
                                mw = new ModelWrapper(model, projectPath);
                                mw.im =
                                    IdentifierManager.fromJSONObject(
                                        new JSONObject(meshMatch.getIdm().toJSONObject().toString())
                                    );
                                mw.partPrimitiveIMs = meshMatch.getPartPrimitiveIMs();

                                skipMesh = true;
                            }
                        } catch (IOException e) {
                            System.out.println("\tIssue in mesh recycling logic. Rebuilding mesh.");
                            e.printStackTrace();
                        }
                        System.out.println("\tEnd mesh recycling logic.");
                    }

                    String mediumPrimitiveString = "Medium_Primitive";
                    String instanceLabelDistalMedium = DISTAL_MEDIUM;
                    String instanceLabelProximalMedium = PROXIMAL_MEDIUM;

                    String geomFile = String.join(
                        "/",
                        new String[] {
                            projectPath,
                            "samples",
                            sample,
                            "models",
                            modelStr,
                            "debug_geom.mph",
                        }
                    );
                    String meshPath = String.join(
                        "/",
                        new String[] { projectPath, "samples", sample, "models", modelStr, "mesh" }
                    );
                    String meshFile = String.join("/", new String[] { meshPath, "mesh.mph" });

                    // START PRE MESH
                    if (!skipMesh) {
                        System.out.println("\tRunning pre-mesh procedure.");

                        // Define model object
                        model = ModelUtil.createUnique("Model");
                        // Add component node 1
                        model.component().create("comp1", true);
                        // Add 3D geom to component node 1
                        model.component("comp1").geom().create("geom1", 3);
                        // Set default length units to micron
                        model.component("comp1").geom("geom1").lengthUnit("um");
                        // Add materials node to component node 1
                        model.component("comp1").physics().create("ec", "ConductiveMedia", "geom1");
                        // and mesh node to component node 1
                        model.component("comp1").mesh().create("mesh1");
                        //set geometry order
                        String geometry_order;
                        try {
                            geometry_order =
                                modelData.getJSONObject("mesh").getString("shape_order");
                        } catch (Exception e) {
                            System.out.println(
                                "\tWARNING: Invalid geometry shape order, or geometry shape order not specified. Proceeding with default order of quadratic"
                            );
                            geometry_order = "quadratic";
                        }
                        model.component("comp1").sorder(geometry_order);
                        //set solution order
                        int solution_order;
                        try {
                            solution_order = modelData.getJSONObject("solver").getInt("sorder");
                        } catch (Exception e) {
                            System.out.println(
                                "\tWARNING: Invalid solution shape order, or solution shape order not specified. Proceeding with default order of 2 (quadratic)"
                            );
                            solution_order = 2;
                        }
                        model
                            .component("comp1")
                            .physics("ec")
                            .prop("ShapeProperty")
                            .set("order_electricpotential", solution_order);

                        // Define ModelWrapper class instance for model and projectPath
                        mw = new ModelWrapper(model, projectPath);

                        //Clear mesh stats
                        modelData.getJSONObject("mesh").put("stats", JSONObject.NULL);

                        try (FileWriter file = new FileWriter(projectPath + "/" + modelFile)) {
                            String output = modelData.toString(2);
                            file.write(output);
                        } catch (IOException e) {
                            e.printStackTrace();
                        }

                        // FEM MODEL GEOMETRY
                        // Set MEDIUM parameters
                        JSONObject distalMedium = modelData
                            .getJSONObject("medium")
                            .getJSONObject("distal");
                        JSONObject proximalMedium = modelData
                            .getJSONObject("medium")
                            .getJSONObject("proximal");
                        JSONObject meshTimes = new JSONObject();

                        setMediumParams(model, distalMedium, proximalMedium);

                        // Create PART PRIMITIVE for MEDIUM
                        String partID = mw.im.next("part", mediumPrimitiveString);
                        IdentifierManager partPrimitiveIM = null;
                        try {
                            partPrimitiveIM =
                                Part.createEnvironmentPartPrimitive(
                                    partID,
                                    mediumPrimitiveString,
                                    mw
                                );
                            mw.partPrimitiveIMs.put(mediumPrimitiveString, partPrimitiveIM);
                        } catch (IllegalArgumentException e) {
                            e.printStackTrace();
                        }

                        // Create PART INSTANCES for MEDIUM (Distal and Proximal)
                        String mediumProximal_instanceID = mw.im.next(
                            "pi",
                            instanceLabelProximalMedium
                        );
                        mw.addMediumInstances(
                            mediumPrimitiveString,
                            instanceLabelDistalMedium,
                            instanceLabelProximalMedium,
                            distalMedium,
                            proximalMedium,
                            mediumProximal_instanceID
                        );

                        ModelParamGroup nerveParams;
                        // Set NERVE MORPHOLOGY parameters
                        assert sampleData != null;
                        JSONObject morphology = (JSONObject) sampleData.get("Morphology");
                        String morphology_unit = "um";
                        String nerveParamsLabal = "Nerve Parameters";
                        nerveParams = model.param().group().create(nerveParamsLabal);
                        nerveParams.label(nerveParamsLabal);

                        if (!cuff_only) {
                            addNerveParams(
                                projectPath,
                                sampleData,
                                modelData,
                                nerveParams,
                                morphology,
                                morphology_unit
                            );
                            model
                                .nodeGroup()
                                .create(mw.im.next("grp", "Contact Impedances"), "Physics", "ec");
                            model
                                .nodeGroup(mw.im.get("Contact Impedances"))
                                .label("Contact Impedances");
                            // there are no primitives/instances for nerve parts, just build them
                            mw.addNerve(sample, nerveParams, modelData);
                        } else {
                            nerveParams.set("a_nerve", "NaN");
                            nerveParams.set(
                                "r_nerve",
                                modelData.getDouble("min_radius_enclosing_circle") +
                                " [" +
                                morphology_unit +
                                "]"
                            );
                        }

                        if (!nerve_only) {
                            // Set CUFF POSITIONING parameters
                            String cuffConformationParamsLabel = "Cuff Conformation Parameters";
                            ModelParamGroup cuffConformationParams = model
                                .param()
                                .group()
                                .create(cuffConformationParamsLabel);
                            cuffConformationParams.label(cuffConformationParamsLabel);

                            //Check if there are multiple cuffs (array) or only a single cuff (json object)
                            Object cuffObject = modelData.get("cuff");
                            JSONArray allCuffSpec = null;
                            if (cuffObject instanceof JSONArray) {
                                // It's an array --> single cuff
                                allCuffSpec = (JSONArray) cuffObject;
                            } else if (cuffObject instanceof JSONObject) {
                                // It's an object --> multiple cuffs in an array
                                allCuffSpec = new JSONArray();
                                allCuffSpec.put(cuffObject);
                            }

                            for (int i = 0; i < allCuffSpec.length(); i++) {
                                // Read cuff to build from model.json (cuff.preset) which links to JSON containing instantiations of parts
                                JSONObject cuffSpec = allCuffSpec.getJSONObject(i);
                                int cuffIndex;
                                try {
                                    cuffIndex = cuffSpec.getInt("index");
                                } catch (Exception e) {
                                    System.out.println("WARNING: No cuff index provided in model.json. Setting cuff index to 0.");
                                    cuffIndex = 0;
                                }
                                addCuffParams(mw, cuffConformationParams, cuffSpec, cuffIndex);
                            }
                        }

                        // create UNIONS
                        mw.createUnions();

                        // Saved model pre-run geometry for debugging
                        try {
                            System.out.println("\tSaving MPH (pre-geom_run) file to: " + geomFile);
                            model.save(geomFile);
                        } catch (IOException e) {
                            e.printStackTrace();
                        }

                        // break point "pre_geom_run"
                        if ("pre_geom_run".equals(break_point)) {
                            models_exit_status[model_index] = false;
                            System.out.println(
                                "\tpre_geom_run is the first break point encountered, moving on with next model index"
                            );
                            continue;
                        }

                        // BUILD GEOMETRY
                        System.out.println("\tBuilding the FEM geometry.");

                        try {
                            model.component("comp1").geom("geom1").run("fin");
                        } catch (Exception e) {
                            System.out.println(
                                "\tFailed to run geometry for Model Index " +
                                modelStr +
                                ", continuing " +
                                "to any remaining Models"
                            );
                            e.printStackTrace();
                            continue;
                        }

                        // Saved model post-run geometry for debugging
                        try {
                            System.out.println("\tSaving MPH (post-geom_run) file to: " + geomFile);
                            model.save(geomFile);
                        } catch (IOException e) {
                            e.printStackTrace();
                        }

                        // break point "post_geom_run"
                        if ("post_geom_run".equals(break_point) || nerve_only || cuff_only) {
                            models_exit_status[model_index] = false;
                            System.out.println(
                                "\tpost_geom_run is the first break point encountered, moving on with next model index"
                            );
                            continue;
                        }

                        // MESH
                        // ensure that the path for mesh files can be created
                        File meshPathFile = new File(meshPath);
                        if (!meshPathFile.exists()) {
                            boolean success = meshPathFile.mkdirs();
                            assert success;
                        }

                        // ditto for ppims
                        System.out.println("\tCreating PPIM dirs");
                        String ppimPath = meshPath + "/ppim";
                        File ppimPathFile = new File(ppimPath);
                        if (!ppimPathFile.exists()) {
                            boolean success = ppimPathFile.mkdirs();
                            assert success;
                        }

                        // define MESH for PROXIMAL
                        // swept: name (Sweep) and im (swe), facemethod (tri)
                        // free triangular: name (FreeTet) and im (ftet)
                        JSONObject proximalMeshParams = modelData
                            .getJSONObject("mesh")
                            .getJSONObject("proximal");
                        String meshProximalLabel = "Mesh Proximal";
                        String meshProximalKey = proximalMeshParams
                            .getJSONObject("type")
                            .getString("im");
                        String meshProximalName = proximalMeshParams
                            .getJSONObject("type")
                            .getString("name");
                        MeshFeature meshProximal = model
                            .component("comp1")
                            .mesh("mesh1")
                            .create(
                                mw.im.next(meshProximalKey, meshProximalLabel),
                                meshProximalName
                            );
                        meshProximal.selection().geom("geom1", 3);
                        assert partPrimitiveIM != null;
                        meshProximal
                            .selection()
                            .named(
                                "geom1" +
                                "_" +
                                mediumProximal_instanceID +
                                "_" +
                                partPrimitiveIM.get("MEDIUM") +
                                "_dom"
                            );

                        // if using a swept mesh, you need to define the face method
                        if (meshProximalKey.equals("swe")) {
                            String meshProximalFace = proximalMeshParams
                                .getJSONObject("type")
                                .getString("facemethod"); // (tri)
                            meshProximal.set("facemethod", meshProximalFace);
                        }
                        meshProximal.label(meshProximalLabel);

                        String meshProximalSizeInfoLabel = "Mesh Proximal Size Info";
                        MeshFeature meshProximalSizeInfo = meshProximal.create(
                            mw.im.next("size", meshProximalSizeInfoLabel),
                            "Size"
                        );
                        meshProximalSizeInfo.label(meshProximalSizeInfoLabel);
                        meshProximalSizeInfo.set("custom", true);
                        meshProximalSizeInfo.set("hmaxactive", true);
                        meshProximalSizeInfo.set("hmax", proximalMeshParams.getDouble("hmax"));
                        meshProximalSizeInfo.set("hminactive", true);
                        meshProximalSizeInfo.set("hmin", proximalMeshParams.getDouble("hmin"));
                        meshProximalSizeInfo.set("hgradactive", true);
                        meshProximalSizeInfo.set("hgrad", proximalMeshParams.getDouble("hgrad"));
                        meshProximalSizeInfo.set("hcurveactive", true);
                        meshProximalSizeInfo.set("hcurve", proximalMeshParams.getDouble("hcurve"));
                        meshProximalSizeInfo.set("hnarrowactive", true);
                        meshProximalSizeInfo.set(
                            "hnarrow",
                            proximalMeshParams.getDouble("hnarrow")
                        );

                        // Saved model pre-mesh for debugging
                        try {
                            System.out.println(
                                "\tSaving MPH (pre-proximal mesh) file to: " + meshFile
                            );
                            model.save(meshFile);
                        } catch (IOException e) {
                            System.out.println(
                                "\tFailed to save geometry for Model Index " +
                                modelStr +
                                ", continuing " +
                                "to any remaining Models"
                            );
                            e.printStackTrace();
                            continue;
                        }

                        // break point "pre_mesh_proximal"
                        if ("pre_mesh_proximal".equals(break_point)) {
                            models_exit_status[model_index] = false;
                            System.out.println(
                                "\tpre_mesh_proximal is the first break point encountered, moving on with next model index"
                            );
                            continue;
                        }

                        System.out.println("\tMeshing proximal parts... will take a while");

                        long proximalMeshStartTime = System.nanoTime();
                        try {
                            model
                                .component("comp1")
                                .mesh("mesh1")
                                .run(mw.im.get(meshProximalLabel));
                        } catch (Exception e) {
                            System.out.println(
                                "\tFailed to mesh proximal geometry for Model Index " +
                                modelStr +
                                ", continuing to any remaining Models"
                            );
                            e.printStackTrace();
                            continue;
                        }

                        long estimatedProximalMeshTime = System.nanoTime() - proximalMeshStartTime;
                        meshTimes.put("proximal", estimatedProximalMeshTime / Math.pow(10, 6)); // convert nanos to millis

                        // put nerve to mesh, rest to mesh, mesh to modelData
                        JSONObject mesh = modelData.getJSONObject("mesh");

                        TimeUnit.SECONDS.sleep(1);

                        // Saved model pre-mesh for debugging
                        model.save(meshFile);
                        TimeUnit.SECONDS.sleep(5);

                        // break point "post_mesh_proximal"
                        if ("post_mesh_proximal".equals(break_point)) {
                            models_exit_status[model_index] = false;
                            System.out.println(
                                "\tpost_mesh_proximal is the first break point encountered, moving on with next model index"
                            );
                            continue;
                        }

                        // define MESH for DISTAL
                        // swept: name (Sweep) and im (swe), facemethod (tri)
                        // free triangular: name (FreeTet) and im (ftet)
                        if (distalMedium.getBoolean("exist")) {
                            String meshDistalLabel = "Mesh Distal";
                            JSONObject distalMeshParams = modelData
                                .getJSONObject("mesh")
                                .getJSONObject("distal");
                            String meshDistalKey = distalMeshParams
                                .getJSONObject("type")
                                .getString("im");
                            String meshDistalName = distalMeshParams
                                .getJSONObject("type")
                                .getString("name");
                            MeshFeature meshDistal = model
                                .component("comp1")
                                .mesh("mesh1")
                                .create(mw.im.next(meshDistalKey, meshDistalLabel), meshDistalName);
                            meshDistal.selection().geom("geom1", 3);
                            meshDistal.selection().remaining();
                            meshDistal.label(meshDistalLabel);

                            String meshDistalSizeInfoLabel = "Mesh Distal Size Info";
                            MeshFeature meshDistalSizeInfo = meshDistal.create(
                                mw.im.next("size", meshDistalSizeInfoLabel),
                                "Size"
                            );
                            meshDistalSizeInfo.label(meshDistalSizeInfoLabel);

                            meshDistalSizeInfo.set("custom", true);
                            meshDistalSizeInfo.set("hmaxactive", true);
                            meshDistalSizeInfo.set("hmax", distalMeshParams.getDouble("hmax"));
                            meshDistalSizeInfo.set("hminactive", true);
                            meshDistalSizeInfo.set("hmin", distalMeshParams.getDouble("hmin"));
                            meshDistalSizeInfo.set("hgradactive", true);
                            meshDistalSizeInfo.set("hgrad", distalMeshParams.getDouble("hgrad"));
                            meshDistalSizeInfo.set("hcurveactive", true);
                            meshDistalSizeInfo.set("hcurve", distalMeshParams.getDouble("hcurve"));
                            meshDistalSizeInfo.set("hnarrowactive", true);
                            meshDistalSizeInfo.set(
                                "hnarrow",
                                distalMeshParams.getDouble("hnarrow")
                            );

                            // Saved model pre-mesh for debugging
                            try {
                                System.out.println(
                                    "\tSaving MPH (pre-distal mesh) file to: " + meshFile
                                );
                                model.save(meshFile);
                            } catch (IOException e) {
                                System.out.println(
                                    "\tFailed to save geometry for Model Index " +
                                    modelStr +
                                    ", continuing " +
                                    "to any remaining Models"
                                );
                                e.printStackTrace();
                                continue;
                            }

                            // break point "pre_mesh_distal"
                            if ("pre_mesh_distal".equals(break_point)) {
                                models_exit_status[model_index] = false;
                                System.out.println(
                                    "\tpre_mesh_distal is the first break point encountered, moving on with next model index"
                                );
                                continue;
                            }

                            System.out.println("\tMeshing the distal parts... will take a while");
                            long distalMeshStartTime = System.nanoTime();
                            try {
                                model
                                    .component("comp1")
                                    .mesh("mesh1")
                                    .run(mw.im.get(meshDistalLabel));
                            } catch (Exception e) {
                                System.out.println(
                                    "\tFailed to mesh distal geometry for Model Index " +
                                    modelStr +
                                    ", continuing to any remaining Models"
                                );
                                e.printStackTrace();
                                continue;
                            }
                            long estimatedRestMeshTime = System.nanoTime() - distalMeshStartTime;
                            meshTimes.put("distal", estimatedRestMeshTime / Math.pow(10, 6)); // convert nanos to millis

                            // Saved model post-mesh distal for debugging
                            try {
                                System.out.println(
                                    "\tSaving MPH (post-distal mesh) file to: " + meshFile
                                );
                                model.save(meshFile);
                            } catch (IOException e) {
                                System.out.println(
                                    "\tFailed to save geometry for Model Index " +
                                    modelStr +
                                    ", continuing " +
                                    "to any remaining Models"
                                );
                                e.printStackTrace();
                                continue;
                            }

                            // break point "post_mesh_distal"
                            if ("post_mesh_distal".equals(break_point)) {
                                models_exit_status[model_index] = false;
                                System.out.println(
                                    "\tpost_mesh_distal is the first break point encountered, moving on with next model index"
                                );
                                continue;
                            }
                        }

                        System.out.println("\tSaving mesh statistics.");

                        saveMeshStats(model, modelFile, modelData, meshTimes, mesh);

                        System.out.println("\tDONE MESHING");

                        try {
                            // save mesh.mph
                            System.out.println("\tSaving MPH (post-mesh) file to: " + meshFile);
                            model.save(meshFile);
                        } catch (IOException e) {
                            System.out.println(
                                "\tFailed to save mesh.mph file for Model Index " +
                                modelStr +
                                ", continuing to any remaining Models"
                            );
                            e.printStackTrace();
                        }

                        String imFile = String.join(
                            "/",
                            new String[] {
                                projectPath,
                                "samples",
                                sample,
                                "models",
                                modelStr,
                                "mesh",
                                "im.json",
                            }
                        );

                        // save IM !!!!
                        JSONio.write(imFile, mw.im.toJSONObject()); // write to file

                        // save ppIMs !!!!
                        for (String name : mw.partPrimitiveIMs.keySet()) {
                            JSONio.write(
                                ppimPath + "/" + name + ".json",
                                mw.partPrimitiveIMs.get(name).toJSONObject()
                            );
                        }

                        boolean keep_debug_geom;
                        if (run.has("keep") && run.getJSONObject("keep").has("debug_geom")) {
                            keep_debug_geom = run.getJSONObject("keep").getBoolean("debug_geom");
                        } else {
                            keep_debug_geom = true;
                        }

                        if (!keep_debug_geom) {
                            File debug_geom_file = new File(geomFile);
                            boolean delSuccess = debug_geom_file.delete();
                            if (delSuccess) {
                                System.out.println(
                                    "\tSuccessfully saved mesh.mph and ppim's, therefore deleted debug_geom.mph file."
                                );
                            } else {
                                System.out.println(
                                    "\tSuccessfully saved mesh.mph and ppim's; could not delete debug_geom.mph file."
                                );
                            }
                        }
                    }

                    //////////////// START POST MESH
                    // IMPORTANT THAT MODEL IS NOT NULL HERE!!
                    assert model != null;
                    assert sampleData != null;

                    // add MATERIAL DEFINITIONS
                    String materialParamsLabel = "Material Parameters";
                    ModelParamGroup materialParams = model
                        .param()
                        .group()
                        .create(materialParamsLabel);
                    materialParams.label(materialParamsLabel);

                    String nerveMode = (String) sampleData.getJSONObject("modes").get("nerve");
                    ArrayList<String> bio_materials = new ArrayList<>(
                        Arrays.asList("medium", "perineurium", "endoneurium")
                    );
                    if (nerveMode.equals("PRESENT")) {
                        bio_materials.add("epineurium");
                    }
                    mw.addMaterialDefinitions(bio_materials, modelData, materialParams);

                    // Add material assignments (links)
                    // DOMAIN
                    // Note: Domain assignment must come before cuffs to accurately override materials in COMSOL.
                    mw.addDomainMaterialAssignments(
                        model,
                        modelData,
                        mediumPrimitiveString,
                        instanceLabelDistalMedium,
                        instanceLabelProximalMedium
                    );

                    // CUFFS
                    // Add material definitions and assignments for CUFFs
                    // Check if multiple cuffs (array) or single cuff (json object)
                    Object cuffObject = modelData.get("cuff");
                    JSONArray allCuffSpec = null;
                    if (cuffObject instanceof JSONArray) { // Only one stim or recording cuff - single cuff configuration defined in model.json
                        allCuffSpec = (JSONArray) cuffObject;
                    } else if (cuffObject instanceof JSONObject) { // Stim and Rec cuffs - multiple cuff configurations defined in model.json
                        cuffObject = (JSONObject) cuffObject;
                        allCuffSpec = new JSONArray();
                        allCuffSpec.put(cuffObject);
                    }

                    //Loop through all cuffs
                    for (int i = 0; i < allCuffSpec.length(); i++) {
                        // Read cuff to build from model.json (cuff.preset) which links to JSON containing instantiations of parts
                        JSONObject cuffSpec = allCuffSpec.getJSONObject(i);

                        String cuff = cuffSpec.getString("preset");
                        int index;
                        try {
                            index = cuffSpec.getInt("index");
                        } catch (Exception e) {
                            System.out.println("WARNING: No cuff index provided in model.json. Setting cuff index to 0.");
                            index = 0; // If no cuff index provided: this is an old
                        }

                        JSONObject cuffData = JSONio.read(
                            String.join(
                                "/",
                                new String[] { mw.root, "config", "system", "cuffs", cuff }
                            )
                        );

                        ArrayList<String> cuff_materials = new ArrayList<>();
                        // loop through all part instances
                        for (Object item : (JSONArray) cuffData.get("instances")) {
                            JSONObject itemObject = (JSONObject) item;
                            for (Object function : itemObject.getJSONArray("materials")) {
                                JSONObject functionObject = (JSONObject) function;
                                cuff_materials.add(functionObject.getString("info"));
                            }
                        }
                        mw.addMaterialDefinitions(cuff_materials, modelData, materialParams);
                        mw.addCuffPartMaterialAssignments(cuffData, index);
                    }

                    // NERVE
                    mw.addNerveMaterialAssignments(model, nerveMode);

                    // break point "post_mesh_distal"
                    if ("post_material_assign".equals(break_point)) {
                        models_exit_status[model_index] = false;
                        System.out.println(
                            "\tpost_material_assign is the first break point encountered, moving on with next model index"
                        );
                        continue;
                    }

                    mw.solutionSetup(model, modelData, endo_only_solution);

                    // break point "post_mesh_distal"
                    if ("pre_loop_currents".equals(break_point)) {
                        models_exit_status[model_index] = false;
                        System.out.println(
                            "\tpre_loop_currents is the first break point encountered, moving on with next model index"
                        );
                        continue;
                    }
                    // break point "post_mesh_distal"
                    boolean pre_solve_break;
                    pre_solve_break = "pre_solve".equals(break_point);

                    mw.loopCurrents(
                        modelData,
                        projectPath,
                        sample,
                        modelStr,
                        skipMesh,
                        pre_solve_break,
                        basesValid
                    );

                    if (pre_solve_break) {
                        models_exit_status[model_index] = false;
                        System.out.println(
                            "\tpre_solve is the first break point encountered, moving on with next model index\n"
                        );
                        continue;
                    }

                    ModelUtil.remove(model.tag());

                    boolean keep_mesh;
                    if (run.has("keep") && run.getJSONObject("keep").has("mesh")) {
                        keep_mesh = run.getJSONObject("keep").getBoolean("mesh");
                    } else {
                        keep_mesh = true;
                    }

                    if (!keep_mesh) {
                        File mesh_path = new File(meshPath);
                        boolean delSuccess = deleteDir(mesh_path);
                        if (delSuccess) {
                            System.out.println(
                                "\tSuccessfully solved for /bases, therefore deleted /mesh directory."
                            );
                        } else {
                            System.out.println(
                                "\tSuccessfully solved for /bases; an issue occurred during deletion of mesh directory."
                            );
                        }
                    }

                    try (FileWriter file = new FileWriter(projectPath + "/" + modelFile)) {
                        String output = modelData.toString(2);
                        file.write(output);
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }

                // If no Sim configs, SKIP
                JSONArray sims_list = run.getJSONArray("sims");
                if (!sims_list.isEmpty()) {
                    try {
                        extractAllPotentials(projectPath, runPath, modelStr);
                    } catch (Exception e) {
                        System.out.println(
                            "\tFailed to extract potentials for Model Index " +
                            modelStr +
                            ", continuing to any remaining Models"
                        );
                        e.printStackTrace();
                        continue;
                    }
                }

                String model_path = String.join(
                    "/",
                    new String[] { // build path to sim config file
                        projectPath,
                        "samples",
                        sample,
                        "models",
                        modelStr,
                    }
                );

                // construct bases path (to MPH)
                String basesPath = String.join("/", new String[] { model_path, "bases" });

                boolean keep_bases;
                if (run.has("keep") && run.getJSONObject("keep").has("bases")) {
                    keep_bases = run.getJSONObject("keep").getBoolean("bases");
                } else {
                    keep_bases = true;
                }

                if (!keep_bases) {
                    File bases_path = new File(basesPath);
                    boolean delSuccess = deleteDir(bases_path);
                    if (delSuccess) {
                        System.out.println(
                            "\tSuccessfully extracted potentials, therefore deleted /bases directory."
                        );
                    } else {
                        System.out.println(
                            "\tSuccessfully extracted potentials; an issue occurred during deletion of bases directory."
                        );
                    }
                }

                models_exit_status[model_index] = true;
            } catch (Exception e) {
                models_exit_status[model_index] = false;
                System.out.println(
                    "\tFailed to mesh/solve/extract potentials for model " +
                    models_list.get(model_index)
                );
                e.printStackTrace();
            }
        }
        // keep track of successful and failed model indices, continue in Python for successes only

        ModelUtil.disconnect();
        System.out.println("Disconnected from COMSOL Server");
        run.put("models_exit_status", models_exit_status);

        try (FileWriter file = new FileWriter(runPath)) {
            String output = run.toString(2);
            file.write(output);
        } catch (IOException e) {
            e.printStackTrace();
        }

        System.exit(0);
    }

    private static void setShowProgress(JSONObject cli_args) {
        if (cli_args.has("comsol_progress") && cli_args.getBoolean("comsol_progress")) {
            ModelUtil.showProgress(null); // if you want to see COMSOL progress (as it makes all geometry, runs, etc.)
        }

        if (cli_args.has("comsol_progress_popup") && cli_args.getBoolean("comsol_progress_popup")) {
            ModelUtil.showProgress(true); // if you want to see COMSOL progress (as it makes all geometry, runs, etc.)
        }
    }

    private static JSONObject getCLI(String[] args) {
        //Load CLI args
        byte[] decodedBytes = Base64.getDecoder().decode(args[2]);
        String decodedString = new String(decodedBytes);
        return new JSONObject(decodedString);
    }

    private static void saveMeshStats(
        Model model,
        String modelFile,
        JSONObject modelData,
        JSONObject meshTimes,
        JSONObject mesh
    ) {
        // MESH STATISTICS
        String quality_measure;
        if (modelData.getJSONObject("mesh").has("quality_measure")) {
            quality_measure = modelData.getJSONObject("mesh").getString("quality_measure");
        } else {
            quality_measure = "vollength";
            System.out.println("\tNo quality measure for mesh, using default (vollength)");
        }

        model.component("comp1").mesh("mesh1").stat().setQualityMeasure(quality_measure);
        // could use: skewness, maxangle, volcircum, vollength, condition, growth...

        Integer number_elements = model.component("comp1").mesh("mesh1").getNumElem("all");
        Double min_quality = model.component("comp1").mesh("mesh1").getMinQuality("all");
        Double mean_quality = model.component("comp1").mesh("mesh1").getMeanQuality("all");
        Double min_volume = model.component("comp1").mesh("mesh1").getMinVolume("all");
        Double volume = model.component("comp1").mesh("mesh1").getVolume("all");

        JSONObject meshStats = new JSONObject();
        meshStats.put("mesh_times", meshTimes);
        meshStats.put("number_elements", number_elements);
        meshStats.put("min_quality", min_quality);
        meshStats.put("mean_quality", mean_quality);
        meshStats.put("mean_quality", mean_quality);
        meshStats.put("min_volume", min_volume);
        meshStats.put("volume", volume);
        meshStats.put("quality_measure_used", quality_measure);
        meshStats.put("name", ModelUtil.getComsolVersion());
        mesh.put("stats", meshStats);
        modelData.put("mesh", mesh);

        try (FileWriter file = new FileWriter("../" + modelFile)) {
            String output = modelData.toString(2);
            file.write(output);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void addCuffParams(
        ModelWrapper mw,
        ModelParamGroup cuffConformationParams,
        JSONObject cuffSpec,
        Integer cuff_num
    ) {
        // add PART PRIMITIVES for CUFF
        String cuff = cuffSpec.getString("preset");
        mw.addCuffPartPrimitives(cuff);

        // add PART INSTANCES for cuff
        // Note: If no index was given, we assume the single cuff is used for stimulation and cuffIndex is 0.
        Integer cuffIndex;
        try {
            cuffIndex = cuffSpec.getInt("index");
        } catch (Exception e) {
            System.out.println("WARNING: No cuff index provided in model.json. Setting cuff index to 0.");
            cuffIndex = 0;
        }
        mw.addCuffPartInstances(cuff, cuff_num, cuffIndex);

        //Set cuff conformation parameters
        String cuff_shift_unit = "[micrometer]";
        String cuff_rot_unit = "[degree]";
        Double cuff_shift_x = cuffSpec.getJSONObject("shift").getDouble("x");
        Double cuff_shift_y = cuffSpec.getJSONObject("shift").getDouble("y");
        Double cuff_shift_z = cuffSpec.getJSONObject("shift").getDouble("z");
        Double cuff_rot_pos = cuffSpec.getJSONObject("rotate").getDouble("pos_ang");
        Double cuff_rot_add = cuffSpec.getJSONObject("rotate").getDouble("add_ang");

        String cuffname = cuff.split("\\.")[0] + "_" + cuff_num;

        cuffConformationParams.set(
            cuffname + "_cuff_shift_x",
            cuff_shift_x + " " + cuff_shift_unit
        );
        cuffConformationParams.set(
            cuffname + "_cuff_shift_y",
            cuff_shift_y + " " + cuff_shift_unit
        );
        cuffConformationParams.set(
            cuffname + "_cuff_shift_z",
            cuff_shift_z + " " + cuff_shift_unit
        );
        cuffConformationParams.set(
            cuffname + "_cuff_rot",
            cuff_rot_pos + cuff_rot_add + " " + cuff_rot_unit
        );
    }

    private static void addNerveParams(
        String projectPath,
        JSONObject sampleData,
        JSONObject modelData,
        ModelParamGroup nerveParams,
        JSONObject morphology,
        String morphology_unit
    ) {
        // add NERVE (Fascicles CI/MESH and EPINEURIUM)
        if (morphology.isNull("Nerve")) { //Monofascicle, no-epineurium case
            nerveParams.set("a_nerve", "NaN");
            nerveParams.set(
                "r_nerve",
                modelData.getDouble("min_radius_enclosing_circle") + " [" + morphology_unit + "]"
            );
        } else {
            JSONObject nerve = (JSONObject) morphology.get("Nerve");
            nerveParams.set("a_nerve", nerve.get("area") + " [" + morphology_unit + "^2]");

            // backwards compatibility
            String reshapenerveMode = (String) sampleData
                .getJSONObject("modes")
                .get("reshape_nerve");
            double deform_ratio = 0;
            if (sampleData.has("deform_ratio")) {
                deform_ratio = sampleData.getDouble("deform_ratio");
            } else {
                if (reshapenerveMode.equals("CIRCLE")) {
                    deform_ratio = 1;
                } else if (reshapenerveMode.equals("NONE")) {
                    deform_ratio = 0;
                }
            }
            //

            if (deform_ratio < 1) { //Use trace
                nerveParams.set(
                    "r_nerve",
                    modelData.getDouble("min_radius_enclosing_circle") +
                    " [" +
                    morphology_unit +
                    "]"
                );
            } else { //Use area of nerve
                nerveParams.set("r_nerve", "sqrt(a_nerve/pi)");
            }
        }

        String ciCoeffsFile = String.join(
            "/",
            new String[] { "config", "system", "ci_peri_thickness.json" }
        );

        JSONObject ciCoeffsData = null;
        try {
            ciCoeffsData = JSONio.read(projectPath + "/" + ciCoeffsFile);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

        String ci_mode = sampleData.getJSONObject("modes").getString("ci_perineurium_thickness");
        if (ci_mode.compareTo("MEASURED") != 0) {
            assert ciCoeffsData != null;
            JSONObject myCICoeffs = ciCoeffsData
                .getJSONObject("ci_perineurium_thickness_parameters")
                .getJSONObject(ci_mode);
            nerveParams.set("ci_a", myCICoeffs.getDouble("a") + " [micrometer/micrometer]");
            nerveParams.set("ci_b", myCICoeffs.getDouble("b") + " [micrometer]");
        }
    }

    private void addMediumInstances(
        String mediumPrimitiveString,
        String instanceLabelDistalMedium,
        String instanceLabelProximalMedium,
        JSONObject distalMedium,
        JSONObject proximalMedium,
        String mediumProximal_instanceID
    ) {
        if (distalMedium.getBoolean("exist")) {
            String mediumDistal_instanceID = this.im.next("pi", instanceLabelDistalMedium);

            if (proximalMedium.getBoolean("distant_ground")) {
                System.out.println(
                    "\tWARNING: you have a distal domain, as well as a proximal domain " +
                    "that is grounded... make sure this is something you actually want to do..."
                );
            }

            try {
                Part.createEnvironmentPartInstance(
                    mediumDistal_instanceID,
                    instanceLabelDistalMedium,
                    mediumPrimitiveString,
                    this,
                    distalMedium
                );
            } catch (IllegalArgumentException e) {
                e.printStackTrace();
            }
        }

        try {
            Part.createEnvironmentPartInstance(
                mediumProximal_instanceID,
                instanceLabelProximalMedium,
                mediumPrimitiveString,
                this,
                proximalMedium
            );
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        }
    }

    private static void setMediumParams(
        Model model,
        JSONObject distalMedium,
        JSONObject proximalMedium
    ) {
        String mediumParamsLabel = "Medium Parameters";
        ModelParamGroup mediumParams = model.param().group().create(mediumParamsLabel);
        mediumParams.label(mediumParamsLabel);

        double proximal_length = proximalMedium.getDouble("length");
        double proximal_radius = proximalMedium.getDouble("radius");

        String bounds_unit = "[um]";
        mediumParams.set("z_nerve", proximal_length + " " + bounds_unit);
        mediumParams.set("r_proximal", proximal_radius + " " + bounds_unit);

        if (distalMedium.getBoolean("exist")) {
            double distal_length = distalMedium.getDouble("length");
            double distal_radius = distalMedium.getDouble("radius");
            double distal_x = distalMedium.getJSONObject("shift").getDouble("x");
            double distal_y = distalMedium.getJSONObject("shift").getDouble("y");
            double distal_z = distalMedium.getJSONObject("shift").getDouble("z");

            mediumParams.set("z_distal", distal_length + " " + bounds_unit);
            mediumParams.set("r_distal", distal_radius + " " + bounds_unit);
            mediumParams.set("distal_shift_x", distal_x + " " + bounds_unit);
            mediumParams.set("distal_shift_y", distal_y + " " + bounds_unit);
            mediumParams.set("distal_shift_z", distal_z + " " + bounds_unit);
        }
    }

    //Check if bases are valid and return a boolean array specifying the bases which need to be resolved
    private static boolean[] areBasesValid(
        String projectPath,
        String sample,
        String modelStr,
        String bases_directory,
        File basesPathFile
    ) {
        boolean[] basesValid;
        if (basesPathFile.exists()) {
            String imFile = String.join(
                "/",
                new String[] {
                    projectPath,
                    "samples",
                    sample,
                    "models",
                    modelStr,
                    "mesh",
                    "im.json",
                }
            );
            try {
                JSONObject imdata = JSONio.read(imFile);
                JSONObject currentIDs = imdata.getJSONObject("currentIDs");
                basesValid = new boolean[currentIDs.length()];
                for (int cu = 0; cu < currentIDs.length(); cu++) {
                    if ((currentIDs.getJSONObject(Integer.toString(cu + 1))).length()== 1) {
                        // If currentID has one element, means that im.json was generated with old version of ascent before multi-cuffs.
                        // Update to current structure (containing pcs, name, and cuff_index) if the bases do exist.
                        File basisFile = new File(bases_directory + "/" + cu + ".mph");
                        if (basisFile.exists()) {
                            // Update im.json
                            JSONObject current_object = currentIDs.getJSONObject(Integer.toString(cu + 1));
                            String key = current_object.keys().next();
                            current_object.put("pcs", current_object.get(key));
                            current_object.put("name", cu + "_Cuff 0_" + key);
                            current_object.put("cuff_index", "0");
                            current_object.remove(key);
                            String cuffNameIdPseudonym = imdata.getJSONObject("identifierPseudonyms").getString(key);
                            imdata.getJSONObject("identifierPseudonyms").put(cu+"_Cuff 0_"+key, cuffNameIdPseudonym);
                            imdata.getJSONObject("identifierPseudonyms").remove(key);
                            currentIDs.put(Integer.toString(cu + 1), current_object);
                            imdata.put("currentIDs", currentIDs);
                            JSONio.write(imFile, imdata); // write to file

                            // Rename bases files.
                            File newBasisFile = new File(bases_directory + "/" + current_object.get("name") + ".mph");
                            basisFile.renameTo(newBasisFile);
                            basesValid[cu] = newBasisFile.exists();
                        }
                        else{
                            basesValid = new boolean[] { false };
                        }
                    }
                    else {
                        // Check bases as you would for multi-cuffs.
                        String bases_name = currentIDs
                            .getJSONObject(Integer.toString(cu + 1))
                            .getString("name");
                        File basisFile = new File(bases_directory + "/" + cu + "_" + bases_name + ".mph");
                        basesValid[cu] = basisFile.exists();
                    }
                }
            }
            catch (FileNotFoundException e) {
                System.out.println(
                    "\tCould not validate bases because no identifier manager record exists (mesh/im.json). Resolving all bases."
                );
                basesValid = new boolean[] { false };
            }
        }
        else {
            basesValid = new boolean[] { false };
        }
        return basesValid;
    }

    private void addDomainMaterialAssignments(
        Model model,
        JSONObject modelData,
        String mediumPrimitiveString,
        String instanceLabelDistalMedium,
        String instanceLabelProximalMedium
    ) {
        JSONObject distalMedium = modelData.getJSONObject("medium").getJSONObject("distal");
        String mediumMaterial = this.im.get("medium");
        IdentifierManager myIM = this.getPartPrimitiveIM(mediumPrimitiveString);
        if (myIM == null) throw new IllegalArgumentException(
            "IdentifierManager not created for name: " + mediumPrimitiveString
        );
        String[] myLabels = myIM.labels; // may be null, but that is ok if not used
        String selection = myLabels[0];

        if (distalMedium.getBoolean("exist")) {
            String linkLabel = String.join(
                "/",
                new String[] { instanceLabelDistalMedium, selection, "medium" }
            );
            Material mat = model
                .component("comp1")
                .material()
                .create(this.im.next("matlnk", linkLabel), "Link");
            mat.label(linkLabel);
            mat.set("link", mediumMaterial);
            mat
                .selection()
                .named(
                    "geom1_" +
                    this.im.get(instanceLabelDistalMedium) +
                    "_" +
                    myIM.get(selection) +
                    "_dom"
                );
        } else {
            String linkLabel = String.join(
                "/",
                new String[] { instanceLabelProximalMedium, selection, "medium" }
            );
            Material mat = model
                .component("comp1")
                .material()
                .create(this.im.next("matlnk", linkLabel), "Link");
            mat.label(linkLabel);
            mat.set("link", mediumMaterial);
            mat
                .selection()
                .named(
                    "geom1_" +
                    this.im.get(instanceLabelProximalMedium) +
                    "_" +
                    myIM.get(selection) +
                    "_dom"
                );
        }
    }

    private void addNerveMaterialAssignments(Model model, String nerveMode) {
        // Add epineurium only if NerveMode == PRESENT
        if (nerveMode.equals("PRESENT")) {
            String epineuriumMatLinkLabel = "epineurium material";
            PropFeature epineuriumMatLink = model
                .component("comp1")
                .material()
                .create(this.im.next("matlnk", epineuriumMatLinkLabel), "Link");
            epineuriumMatLink.selection().named("geom1" + "_" + this.im.get("EPINEURIUM") + "_dom");
            epineuriumMatLink.label(epineuriumMatLinkLabel);
            epineuriumMatLink.set("link", this.im.get("epineurium"));
        }

        // Add perineurium material only if there are any fascicles being meshed
        if (this.im.get("periUnionCsel") != null) {
            String perineuriumMatLinkLabel = "perineurium material";
            PropFeature perineuriumMatLink = model
                .component("comp1")
                .material()
                .create(this.im.next("matlnk", perineuriumMatLinkLabel), "Link");
            perineuriumMatLink
                .selection()
                .named("geom1" + "_" + this.im.get("periUnionCsel") + "_dom");
            perineuriumMatLink.label(perineuriumMatLinkLabel);
            perineuriumMatLink.set("link", this.im.get("perineurium"));
        }

        // Will always need to add endoneurium material
        String fascicleMatLinkLabel = "endoneurium material";
        PropFeature fascicleMatLink = model
            .component("comp1")
            .material()
            .create(this.im.next("matlnk", fascicleMatLinkLabel), "Link");
        fascicleMatLink.selection().named("geom1" + "_" + this.im.get("endoUnionCsel") + "_dom");
        fascicleMatLink.label(fascicleMatLinkLabel);
        fascicleMatLink.set("link", this.im.get("endoneurium"));
    }

    private void solutionSetup(Model model, JSONObject modelData, boolean endo_only_solution) {
        // Solve
        model.study().create("std1");
        model.study("std1").setGenConv(true);
        model.study("std1").create("stat", "Stationary");
        model.study("std1").feature("stat").activate("ec", true);

        model.sol().create("sol1");
        model.sol("sol1").study("std1");

        model.study("std1").feature("stat").set("notlistsolnum", 1);
        model.study("std1").feature("stat").set("notsolnum", "1");
        model.study("std1").feature("stat").set("listsolnum", 1);
        model.study("std1").feature("stat").set("solnum", "1");
        if (endo_only_solution) {
            model.study("std1").feature("stat").set("usestoresel", "selection");
            model
                .study("std1")
                .feature("stat")
                .set("storesel", new String[] { "geom1_" + this.im.get("endoUnionCsel") + "_dom" });
        }

        model.sol("sol1").create("st1", "StudyStep");
        model.sol("sol1").feature("st1").set("study", "std1");
        model.sol("sol1").feature("st1").set("studystep", "stat");
        model.sol("sol1").create("v1", "Variables");
        model.sol("sol1").feature("v1").set("control", "stat");

        model.sol("sol1").create("s1", "Stationary");
        model.sol("sol1").feature("s1").create("fc1", "FullyCoupled");
        model.sol("sol1").feature("s1").create("i1", "Iterative");
        model.sol("sol1").feature("s1").feature("i1").set("linsolver", "cg");
        model.sol("sol1").feature("s1").feature("i1").create("mg1", "Multigrid");
        model.sol("sol1").feature("s1").feature("i1").feature("mg1").set("prefun", "amg");
        model.sol("sol1").feature("s1").feature("fc1").set("linsolver", "i1");
        model.sol("sol1").feature("s1").feature().remove("fcDef");

        // check for solver type and select appropriate option
        if (modelData.getJSONObject("solver").has("type")) {
            String solverType = modelData.getJSONObject("solver").getString("type");
            if (solverType.equals("direct")) {
                model.sol("sol1").feature("s1").feature("dDef").active(true);
            } else if (!solverType.equals("iterative")) System.out.println(
                "Invalid solver type, proceeding with default (iterative)."
            );
        } else {
            System.out.println("\tSolver type not specified, proceeding with default (iterative).");
        }

        model.sol("sol1").attach("std1");
    }

    private static void licenseCheckout(long waitHours) throws InterruptedException {
        System.out.println(
            "Attempting to check out COMSOL license. System will wait up to " +
            waitHours +
            " hours for an available license seat."
        );
        boolean lic = false;
        long start = System.currentTimeMillis();
        long stop = waitHours * 60 * 60 * 1000 + start;
        while (System.currentTimeMillis() < stop) {
            lic = ModelUtil.checkoutLicense("COMSOL");
            if (lic) {
                long now = System.currentTimeMillis();
                double elapsed =
                    (Long.valueOf(now).doubleValue() - Long.valueOf(start).doubleValue()) /
                    (60 * 60 * 1000);
                System.out.printf("COMSOL license seat obtained (took %.3f hours).%n", elapsed);
                break;
            } else {
                TimeUnit.SECONDS.sleep(600);
            }
        }
        if (!lic) {
            System.out.println(
                "A COMSOL license did not become available within the specified time window. Exiting..."
            );
            System.exit(0);
        }
    }

    private static void serverConnect() throws InterruptedException {
        // Try to connect to comsol server (5 minutes)
        long connectTime = (long) 5 * 60 * 1000 + System.currentTimeMillis();
        while (true) {
            try {
                ModelUtil.connect("localhost", 2036);
                break;
            } catch (FlException e) {
                System.out.println(
                    "Could not connect to COMSOL server on port 2036, trying on port 2037..."
                );
                try {
                    ModelUtil.connect("localhost", 2037);
                    break;
                } catch (FlException exc) {
                    System.out.println(
                        "Could not connect to COMSOL server on port 2037, trying without specifying a port..."
                    );
                    try {
                        ModelUtil.connect();
                        break;
                    } catch (Exception except) {
                        if (System.currentTimeMillis() > connectTime) {
                            except.printStackTrace();
                            System.out.println("Could not connect to COMSOL server, exiting...");
                            System.exit(1);
                        }
                        System.out.println(
                            "Could not connect to COMSOL server, trying again in 60 seconds..."
                        );
                        TimeUnit.SECONDS.sleep(60);
                    }
                }
            }
        }
    }

    public static boolean allTrue(boolean[] array) {
        for (boolean b : array) if (!b) return false;
        return true;
    }

    public static boolean anyTrue(boolean[] array) {
        for (boolean b : array) if (b) return true;
        return false;
    }
}

package model;

import com.comsol.model.Model;
import com.comsol.model.util.ModelUtil;
import com.comsol.util.exceptions.FlException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.json.JSONObject;

public class ModelClearer {

    public static void main(String[] args) throws InterruptedException, IOException {
        String[] comsol_files = args[0].split(",", -1);
        String export_directory = args[1].replace("[", "").replace("]", "").replace("'", "");
        String data_index = args[2];

        JSONObject preserve_data = JSONio.read(
            String.join(
                "/",
                new String[] {
                    export_directory,
                    "config",
                    "comsol_clearing_exceptions",
                    data_index + ".json",
                }
            )
        );

        //connect to comsol server
        int waitMinutes = 5;
        ModelClearer.serverConnect(waitMinutes);

        //checkout comsol license
        long waitHours = 1;
        ModelClearer.licenseCheckout(waitHours);

        // remove the list [] from Python
        // convert ' to " if necessary
        for (String python_comsol_file : comsol_files) {
            String pre_comsol_file = python_comsol_file
                .replace("[", "")
                .replace("]", "")
                .replace("'", "");

            // remove drive (C:, D:, E:, etc) as necessary
            String comsol_file;
            if (pre_comsol_file.contains(":")) {
                comsol_file = pre_comsol_file.substring(pre_comsol_file.lastIndexOf(":") + 1);
            } else {
                comsol_file = pre_comsol_file;
            }

            // https://devqa.io/extract-numbers-string-java-regular-expressions/
            Pattern p = Pattern.compile("\\d+");
            Matcher m = p.matcher(comsol_file);

            List<Integer> allMatches = new ArrayList<>();
            while (m.find()) {
                allMatches.add(Integer.valueOf(m.group()));
            }
            allMatches.toArray(new Integer[0]);

            boolean clear_mesh = true;
            boolean clear_sol = true;

            Integer sample_index;
            Integer model_index;
            Integer basis_index;

            if (comsol_file.contains("mesh")) { // file is mesh.mph
                sample_index = allMatches.get(allMatches.size() - 2); // 2nd from end
                model_index = allMatches.get(allMatches.size() - 1); // end

                ArrayList<Integer> inds = new ArrayList<>(2);
                inds.add(sample_index);
                inds.add(model_index);

                if (preserve_data.getJSONArray("mesh.mph").toList().contains(inds)) {
                    clear_mesh = false;
                }
            } else { // file is <basis_index>.mph
                sample_index = allMatches.get(allMatches.size() - 3); // 3rd from end
                model_index = allMatches.get(allMatches.size() - 2); // 2nd from end
                basis_index = allMatches.get(allMatches.size() - 1); // end

                ArrayList<Integer> inds = new ArrayList<>(2);
                inds.add(sample_index);
                inds.add(model_index);
                inds.add(basis_index);

                if (
                    preserve_data
                        .getJSONObject("<basis_index>.mph")
                        .getJSONArray("mesh")
                        .toList()
                        .contains(inds)
                ) {
                    clear_mesh = false;
                }

                if (
                    preserve_data
                        .getJSONObject("<basis_index>.mph")
                        .getJSONArray("solution")
                        .toList()
                        .contains(inds)
                ) {
                    clear_sol = false;
                }
            }

            Model model = ModelUtil.loadCopy(ModelUtil.uniquetag("Model"), comsol_file);
            assert model != null;

            System.out.println("COMSOL File: " + comsol_file);
            if (clear_mesh) {
                try {
                    model.component("comp1").mesh("mesh1").clearMesh();
                    System.out.println("\t->Cleared mesh");
                    if (clear_sol) {
                        try {
                            model.sol("sol1").clearSolutionData();
                            System.out.println("\t->Cleared solution");
                        } catch (Exception e) {
                            System.out.println("\t->No solution to clear");
                        }
                    }
                } catch (Exception e) {
                    System.out.println("\t->No mesh to clear");
                }
            }

            try {
                System.out.println("\t\tSaving COMSOL file to: " + comsol_file + "\n");
                model.save(comsol_file);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        ModelUtil.disconnect();
        System.out.println("Disconnected from COMSOL Server\n");
        System.exit(0);
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
                System.out.printf("COMSOL license seat obtained (took %.3f hours).%n\n", elapsed);
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

    private static void serverConnect(int waitMinutes) throws InterruptedException {
        // Try to connect to comsol server
        long connectTime = (long) waitMinutes * 60 * 1000 + System.currentTimeMillis();
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
}

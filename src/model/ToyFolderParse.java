package model;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Iterator;
import java.util.stream.Stream;

public class ToyFolderParse {
    public static void main(String[] args) {
        String path = "/Users/jakecariello/Box/Documents/Pipeline/access/data/samples/Pig13-1/0/0/sectionwise/fascicles";

        try(Stream<Path> result = Files.walk(Paths.get(path))) {

            for (Iterator<Path> it = result.iterator(); it.hasNext(); ) {
                Path p = it.next();
                if (p.toString().contains(".txt")) {
                    String[] pathParts = p.toString().split("/");
                    int length = pathParts.length;
                    String fascicleName = (pathParts[length - 2] + pathParts[length - 3] + "_" + pathParts[length - 1])
                            .replaceAll(".txt", "").replaceAll("s", "");
                    System.out.println("fascicleName = " + fascicleName);
                }
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

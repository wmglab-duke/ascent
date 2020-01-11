import com.comsol.model.*;
import com.comsol.model.util.*;

public class feeder_clamp {
    public static void main(String[] args) {
        run();
    }

    public static Model run() {
        Model model = ModelUtil.create("Model");
        ...
        return model;
        }
    }

#You can retrieve the current model using the steps:
import java.io.*;
tag = System.getProperty("cs.currentmodel");
model = ModelUtil.model(tag);

#To run the file, enter
<COMSOL Path>\bin\win32\comsolbatch -inputfile filename.class #windows
<COMSOL Path>/bin/comsol batch -inputfile filename.class # Linux or Mac

# If you want to have an application finding a COMSOL installation automatically tou can have your application examine the registry key
HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\COMSOL\COMSOL43 #64 bit computers
HKEY_LOCAL_MACHINE\SOFTWARE\COMSOL\COMSOL43\ #32 bit computers
# The value name COMSOLROOT contains the installation path


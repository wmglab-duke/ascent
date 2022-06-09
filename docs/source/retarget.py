from pathlib import Path
import os
jsonlist = ['[JSON Parameters](prepend/JSON/JSON_parameters/index)',
                                           '[Sample Parameters](prepend/JSON/JSON_parameters/sample)',
                                           '[Model Parameters](prepend/JSON/JSON_parameters/model)',
                                           '[Sim Parameters](prepend/JSON/JSON_parameters/sim)',
                                           '[Run Parameters](prepend/JSON/JSON_parameters/run)',
                                           '[Environment Parameters](prepend/JSON/JSON_parameters/env)',
                                           '[Mock Sample Parameters](prepend/JSON/JSON_parameters/mock_sample)',
                                           '[Mesh Dependent Model](prepend/JSON/JSON_parameters/mesh_dependent_model)',
                                           '[Query Parameters](prepend/JSON/JSON_parameters/query_criteria)',
                                           '[Material Parameters](prepend/JSON/JSON_parameters/materials)',
                                           '[Contact Impedance](prepend/JSON/JSON_parameters/ci_peri_thickness)']

redict = {
    '[S8 Text](S8-JSON-file-parameter-guide)':jsonlist,
#    '[S7](S7-JSON-configuration-files)':'[JSON Overview](prepend/JSON/JSON_overview)',
    '[S7 Text](S7-JSON-configuration-files)':'[JSON Overview](prepend/JSON/JSON_overview)',
    '[S12](S12-Python-MockSample-class-for-creating-binary-masks-of-nerve-morphology)':'[Mock Morphology](prepend/MockSample)',
    '[S11 Text](S11-Morphology-files)':'prepend/Running_ASCENT/Info#Morphology-Input-Files)',
    '[S26 Text](S26-Java-utility-classes)':'[Java Utility Classes](prepend/Code_Hierarchy/Java#Java-utility-classes)',
#    '[S31](S31-NEURON-launch.hoc)':'[Launch](prepend/Code_Hierarchy/NEURON#NEURON-Launch-hoc)',
#    '[S32](S32-NEURON-Wrapper.hoc)':'[Wrapper](prepend/Code_Hierarchy/NEURON#NEURON-Wrapper-hoc)',
#    '[S8](S8-JSON-file-parameter-guide)':jsonlist,
    '[S12 Text](S12-Python-MockSample-class-for-creating-binary-masks-of-nerve-morphology)':'[Mock Morphology](prepend/MockSample)',
    '[S3 Text](S3-ASCENT-data-hierarchy)':'[ASCENT Data Hierarchy](prepend/Data_Hierarchy)',
    '[S16 Text](S16-Library-of-part-primitives-for-electrode-contacts-and-cuffs)':'[ASCENT Part Primitives](prepend/Primitives_and_Cuffs/Cuff_Primitives)',
    '[S17 Text](S17-Creating-custom-preset-cuffs-from-instances-of-part-primitives)':'[Creating Custom Cuffs](prepend/Primitives_and_Cuffs/Custom_Cuffs)',
    '[S18 Text](S18-Creating-new-part-primitives)':'[Creating New Part Primitives](prepend/Primitives_and_Cuffs/Creating_Primitives)',
    '[S2 Text](S2-Installation)':'[Installation](prepend/Getting_Started#Installation)',
    }

for path in Path('').rglob('*.md'):
    # print(path)
    count = len(str(path).split('\\'))
    prepend = '../'*(count-1)
    with open(path,'r',encoding='utf8') as f:
        text=f.readlines()
    for i,line in enumerate(text):
        for key,value in redict.items():
            if key[1:] in line and key.startswith('.'):
                print(line)
            elif key in line:
                if type(value) is list:
                    print()
                    print(text[i-1:i+1])
                    # num = int(input(list(enumerate(value))))
                    num=0
                    if num<0: continue
                    choice = value[num]
                else:
                    choice= value
                newstr = choice.replace('prepend/',prepend)
                newline=line.replace(key,newstr)
                text[i]=newline
                print('replaced')
    with open(path,'w',encoding='utf8') as f:
        f.writelines(text)
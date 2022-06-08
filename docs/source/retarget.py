from pathlib import Path
import os
jsonlist = ['[JSON Parameters](prepend/JSON/JSON_parameters/index)',
                                           '[Sample Parameters](prepend/JSON/JSON_parameters/sample)'
                                           '[Model Parameters](prepend/JSON/JSON_parameters/model)',
                                           '[Sim Parameters](prepend/JSON/JSON_parameters/sim)',
                                           '[Environment Parameters](prepend/JSON/JSON_parameters/env)']

redict = {
    '[S8 Text](S8-JSON-file-parameter-guide)':jsonlist,
    '[S7](S7-JSON-configuration-files)':'[JSON Overview](prepend/JSON/JSON_overview)',
    '[S12](S12-Python-MockSample-class-for-creating-binary-masks-of-nerve-morphology)':'[Mock Morphology](prepend/MockSample)',
    '.[S11 Text](S11-Morphology-files)':'asd',
    '.[S26 Text](S26-Java-utility-classes)':'as',
    '.[S31](S31-NEURON-launch.hoc)':'[Launch](prepend/Code_Hierarchy/NEURON#NEURON-Launch-hoc)',
    '.[S32](S32-NEURON-Wrapper.hoc)':'[Wrapper](prepend/Code_Hierarchy/NEURON#NEURON-Wrapper-hoc)',
    '[S8](S8-JSON-file-parameter-guide)':jsonlist,
    '[S12 Text](S12-Python-MockSample-class-for-creating-binary-masks-of-nerve-morphology)':'[Mock Morphology](prepend/MockSample)',
    }

for path in Path('').rglob('*.md'):
    # print(path)
    count = len(str(path).split('\\'))
    prepend = '../'*(count-1)
    with open(path,'r',encoding='utf8') as f:
        text=f.readlines()
    for i,line in enumerate(text):
        for key,value in redict.items():
            if key in line and key.startswith('.'):
                print(line)
            elif key in line:
                if type(value) is list:
                    print(line)
                    num = int(input(list(enumerate(value))))
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
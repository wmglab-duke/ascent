import os
import json
import pandas as pd

def runs():
    run_path = os.path.join('config', 'user', 'runs')
    jsons = [file for file in os.listdir(run_path) if file.endswith('.json')]
    data = []
    for j in jsons:
        with open(run_path+'/'+j) as f:
            rundata = json.load(f)
            data.append({'RUN':os.path.splitext(j)[0],
                 'SAMPLE':rundata['sample'],
                 'MODELS':rundata['models'],
                 'SIMS':rundata['sims']})
    df = pd.DataFrame(data)
    print('Run indices available (defined by user .json files in {}):\n'.format(run_path))
    print(df.to_string(index = False))
            
import os
import json
import pandas as pd

def run(mode):
    if mode == 'runs':
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
        
    elif mode == 'samples':
        run_path = os.path.join('samples')
        samples = [file for file in os.listdir(run_path) if not file.startswith('.')]
        sample_jsons = [os.path.join(run_path,x,'sample.json') if os.path.isfile(os.path.join(run_path,x,'sample.json') ) else print('WARNING: sample {} has no json file'.format(x)) for x in samples]
        sample_jsons = [x for x in sample_jsons if x is not None]
        data = []
        for j in sample_jsons:
            with open(j) as f:
                sampledata = json.load(f)
                data.append({'SAMPLE':os.path.splitext(j)[0],
                     'INPUT':sampledata['sample'],
                     'NERVEMODE':sampledata['modes'].get('nerve'),
                     'MASKINPUTMODE':sampledata['modes'].get('mask_input')})
        df = pd.DataFrame(data)
        print('Run indices available (defined by user .json files in {}):\n'.format(run_path))
        print(df.to_string(index = False))
            
    elif mode == 'sims':
        run_path = os.path.join('config', 'user', 'sims')
        jsons = [file for file in os.listdir(run_path) if file.endswith('.json')]
        data = []
        for j in jsons:
            with open(run_path+'/'+j) as f:
                simdata = json.load(f)
                data.append({'SIM':os.path.splitext(j)[0],
                     'FIBERMODE':simdata['fibers'].get('mode'),
                     'PROTOCOL':simdata['protocol'].get('mode'),
                     'XYMODE':simdata['fibers']['xy_parameters'].get('mode')})
        df = pd.DataFrame(data)
        print('Run indices available (defined by user .json files in {}):\n'.format(run_path))
        print(df.to_string(index = False))

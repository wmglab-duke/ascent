import json
import os

import pandas as pd


def run(mode):
    if mode == 'runs':
        run_path = os.path.join('config', 'user', 'runs')
        jsons = [file for file in os.listdir(run_path) if file.endswith('.json')]
        data = []
        for j in jsons:
            with open(run_path + '/' + j) as f:
                try:
                    rundata = json.load(f)
                except Exception as e:
                    print('WARNING: Could not load {}'.format(j))
                    print(e)
                    continue
                data.append({'RUN': os.path.splitext(j)[0],
                             'PSEUDONYM': rundata.get('pseudonym'),
                             'SAMPLE': rundata['sample'],
                             'MODELS': rundata['models'],
                             'SIMS': rundata['sims']})
        df = pd.DataFrame(data)
        df.RUN = df.RUN.astype(int)
        df = df.sort_values('RUN')
        print('Run indices available (defined by user .json files in {}):\n'.format(run_path))
        print(df.to_string(index=False))

    elif mode == 'samples':
        run_path = os.path.join('samples')
        samples = [file for file in os.listdir(run_path) if not file.startswith('.')]
        sample_jsons = [os.path.join(run_path, x, 'sample.json') if os.path.isfile(os.path.join(run_path, x, 'sample.json')) else print('WARNING: sample {} has no json file'.format(x)) for x in samples]
        sample_jsons = [x for x in sample_jsons if x is not None]
        data = []
        for j in sample_jsons:
            with open(j) as f:
                try:
                    sampledata = json.load(f)
                except Exception as e:
                    print('WARNING: Could not load {}'.format(j))
                    print(e)
                    continue
                data.append({'SAMPLE': j.split(os.sep)[1],
                             'PSEUDONYM': sampledata.get('pseudonym'),
                             'INPUT': sampledata['sample'],
                             'NERVEMODE': sampledata['modes'].get('nerve'),
                             'MASKINPUTMODE': sampledata['modes'].get('mask_input')})
        df = pd.DataFrame(data)
        df.SAMPLE = df.SAMPLE.astype(int)
        df = df.sort_values('SAMPLE')
        print('Sample indices available (defined by user folders in {}):\n'.format(run_path))
        print(df.to_string(index=False))

    elif mode == 'sims':
        run_path = os.path.join('config', 'user', 'sims')
        jsons = [file for file in os.listdir(run_path) if file.endswith('.json')]
        data = []
        for j in jsons:
            with open(run_path + '/' + j) as f:
                try:
                    simdata = json.load(f)
                except Exception as e:
                    print('WARNING: Could not load {}'.format(j))
                    print(e)
                    continue
                data.append({'SIM': os.path.splitext(j)[0],
                             'PSEUDONYM': simdata.get('pseudonym'),
                             'FIBERMODE': simdata['fibers'].get('mode'),
                             'PROTOCOL': simdata['protocol'].get('mode'),
                             'XYMODE': simdata['fibers']['xy_parameters'].get('mode')})
        df = pd.DataFrame(data)
        df.SIM = df.SIM.astype(int)
        df = df.sort_values('SIM')
        print('Sim indices available (defined by user .json files in {}):\n'.format(run_path))
        print(df.to_string(index=False))

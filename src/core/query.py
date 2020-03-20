from typing import Union

from src.core import Sample, Simulation
from src.utils import *


class Query(Exceptionable, Configurable, Saveable):
    """
    IMPORTANT: MUST BE RUN FROM PROJECT LEVEL
    """

    def __init__(self, criteria_path: str):
        """
        :param exceptions_config:
        """

        # set up superclasses
        Configurable.__init__(self)
        Exceptionable.__init__(self, SetupMode.NEW)

        self._ran: bool = False  # marker will be set to True one self.run() is called (as is successful)
        self.add(SetupMode.NEW, Config.CRITERIA, criteria_path)  # initialize criteria
        self._result = None  # begin with empty result

    def run(self):
        """
        Build query result using criteria
        :return: result as a dict
        """

        # initialize empty result
        result = {}

        # preliminarily find sample, model, and sim filter indices if applicable (else None)
        sample_indices = self.search(Config.CRITERIA, 'indices', 'sample')
        model_indices = self.search(Config.CRITERIA, 'indices', 'model')
        sim_indices = self.search(Config.CRITERIA, 'indices', 'sim')

        # criteria for each layer
        sample_criteria = self.search(Config.CRITERIA, 'sample')
        model_criteria = self.search(Config.CRITERIA, 'model')
        sim_criteria = self.search(Config.CRITERIA, 'sim')

        # control if missing sim criteria or both sim and model criteria
        include_downstream = self.search(Config.CRITERIA, 'include_downstream')

        # labeling for samples level
        samples_key = 'samples'
        samples_dir = samples_key

        # init list of samples in result
        result[samples_key] = []

        # loop samples
        for sample in os.listdir(samples_dir):
            # skip this sample if applicable
            if sample_indices is not None and int(sample) not in sample_indices:
                continue

            # if applicable, check against sample criteria
            if sample_criteria is not None:
                if not self._match(
                        sample_criteria,
                        self.load(os.path.join(samples_dir, sample, 'sample.json'))
                ):
                    continue

            # labeling for models level
            models_key = 'models'
            models_dir = os.path.join(samples_dir, sample, models_key)

            # post-filtering, add empty SAMPLE to result
            # important to remember that this is at END of list
            result[samples_key].append({
                'index': int(sample),
                models_key: []
            })

            # if no downstream criteria and NOT including downstream, skip lower loops
            # note also that the post loop removal of samples will be skipped (as we desire in this case)
            if model_criteria is None and sim_criteria is None and not include_downstream:
                continue

            # loop models
            for model in os.listdir(models_dir):
                # if there are filter indices for models, use them
                if model_indices is not None and int(model) not in model_indices:
                    continue

                # if applicable, check against model criteria
                if model_criteria is not None:
                    if not self._match(
                            model_criteria,
                            self.load(os.path.join(models_dir, model, 'model.json'))
                    ):
                        continue

                # labeling for sims level
                sims_key = 'sims'
                sims_dir = os.path.join(models_dir, model, sims_key)

                # post-filtering, add empty MODEL to result
                # important to remember that this is at END of list
                result[samples_key][-1][models_key].append({
                    'index': int(model),
                    sims_key: []
                })

                # if no downstream criteria and NOT including downstream, skip lower loops
                # note also that the post loop removal of models will be skipped (as we desire in this case)
                if sim_criteria is None and not include_downstream:
                    continue

                # loop sims
                for sim in os.listdir(sims_dir):
                    if sim_indices is not None and int(sim) not in sim_indices:
                        continue

                    # if applicable, check against model criteria
                    if sim_criteria is not None:
                        if not self._match(
                                sim_criteria,
                                self.load(os.path.join('config', 'user', 'sims', sim + '.json'))
                        ):
                            continue

                    # post-filtering, add SIM to result
                    result[samples_key][-1][models_key][-1][sims_key].append(int(sim))

                # remove extraneous model if no sims were found
                # only reached if sim_criteria not None
                if len(result[samples_key][-1][models_key][-1][sims_key]) == 0:
                    result[samples_key][-1][models_key].pop(-1)

            # remove extraneous sample if no sims were found
            # only reached if model_criteria not None
            if len(result[samples_key][-1][models_key]) == 0:
                result[samples_key].pop(-1)

        self._result = result

    def summary(self) -> dict:
        """
        Return result of self.run()... maybe add result statistics? (e.g. counts of samples, models, sims, etc.)
        :return:
        """
        if self._result is None:
            self.throw(53)

        return self._result

    def fetch_config(self) -> dict:
        """

        :return:
        """

    def fetch_object(self) -> Union[Sample, Simulation]:
        """

        :return:
        """

    def _match(self, criteria: dict, data: dict) -> bool:
        """

        :param criteria:
        :param data:
        :return:
        """

        for key in criteria.keys():

            # ensure key is valid in data
            if key not in data:
                print('ERRONEOUS KEY: '.format(key))
                self.throw(54)

            # corresponding values
            c_val = criteria[key]
            d_val = data[key]

            # now lots of control flow - dependent on the types of the variables

            # if c_val is a dict, recurse
            if type(c_val) is dict:
                if not self._match(c_val, d_val):
                    print('fail 0')
                    return False

            # neither c_val nor d_val are list
            elif not any([type(v) is list for v in (c_val, d_val)]):
                if not c_val == d_val:
                    print('fail 1')
                    return False

            # c_val IS list, d_val IS NOT list
            elif type(c_val) is list and type(d_val) is not list:
                if d_val not in c_val:
                    print('fail 2')
                    return False

            # c_val IS NOT list, d_val IS list
            elif type(c_val) is not list and type(d_val) is list:
                # "partial matches" indicates that other values may be present in d_val
                if not self.search(Config.CRITERIA, 'partial_matches') or c_val not in d_val:
                    print('fail 3')
                    return False

            # both c_val and d_val are list
            else:  # all([type(v) is list for v in (c_val, d_val)]):
                # "partial matches" indicates that other values may be present in d_val
                if not self.search(Config.CRITERIA, 'partial_matches') or not all([c_i in d_val for c_i in c_val]):
                    print('fail 4')
                    return False

        return True

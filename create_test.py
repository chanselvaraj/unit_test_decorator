import functools
import inspect
import os
import pickle
import traceback
from pathlib import Path
from dotenv import load_dotenv
import json

class parameterise_test:
    @staticmethod
    def _get_pickle_variable(path):
        """parse the pickel file in the path to an object variable"""
        with open(path, "rb") as pklfile:
            res = pickle.load(pklfile)
        return res

    @staticmethod
    def _get_json_variable(path):
        """parse the json file in the path to a json variable"""
        with open(path, "rb") as jsonfile:
            res = json.load(jsonfile)
        return res

    @staticmethod
    def _get_fn_dataset(fun_name, test_variable_path):
        """input : testing function name
        functionality : locate the folder with the fun_name under "test_variable_path" and load the test
                        datas (arguments and result) to a list of tuples"""
        try:
            directory = Path(os.path.abspath(os.path.dirname(__file__)) + test_variable_path + "/" + fun_name)
            directories = [
                os.path.join(directory, name)
                for name in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, name))
            ]
            data_set = []
            for dir in directories:
                try:
                    file = "/input.pkl"
                    attributes = (
                        parameterise_test._get_pickle_variable(dir + file)
                        if os.path.exists(dir + file)
                        else parameterise_test._get_json_variable(dir + "/input.json")
                    )
                    file = "/result.pkl"
                    result = (
                        parameterise_test._get_pickle_variable(dir + file)
                        if os.path.exists(dir + file)
                        else parameterise_test._get_json_variable(dir + "/result.json")
                    )
                    if attributes is not None and result is not None:
                        data_set.append({"att": attributes, "result": result["result"]})
                except Exception:
                    print(traceback.format_exc())
            return data_set
        except Exception:
            return []

class create_test_data:
    """This decorator can wrap any function that has valid non-null arguments and a valid non-null return type.
    It will serialise the data as pickle files and can be used for convenient test data generation for unit tests
    Ensure that ENABLE_TEST_DATA_CREATION is set to True for this to take effect. Test data is saved to bh_bond_scraper/tests/test_data
    """

    def __init__(self):
        self.call_count = 0
        self.data = []
        self.flag = True
        load_dotenv()

    def find_directories_with_name(self, target_name, class_name):
        matching_dirs = []
        for dirpath, dirnames, filenames in os.walk(os.path.dirname(__file__)):
            for dirname in dirnames:
                if dirname == target_name:
                    if class_name is None or class_name == dirpath.split("/").pop():
                        matching_dirs.append(os.path.join(dirpath, dirname))
        if len(matching_dirs) == 0:
            os.makedirs(
                Path(
                    os.path.dirname(__file__)
                    + "//test_data//"
                    + (class_name if class_name else "common")
                    + "//"
                    + target_name
                )
            )
            return [
                os.path.dirname(__file__)
                + "//test_data//"
                + (class_name if class_name else "common")
                + "//"
                + target_name
            ]
        return matching_dirs

    def populate_test_data(self, func, input_data, output, class_name):
        try:
            dirs = self.find_directories_with_name(func.__name__, class_name)
            for dir in dirs:
                os.makedirs(f"{dir}/test_dataset{self.call_count}",exist_ok=True)
                with open(f"{dir}/test_dataset{self.call_count}/input.pkl", "wb") as f:
                    inputs = dict(
                        zip(
                            inspect.getfullargspec(func).args, input_data["args"] + tuple(input_data["kwargs"].values())
                        )
                    )  #
                    inputs.pop("self", None)
                    pickle.dump(inputs, f)
                with open(f"{dir}/test_dataset{self.call_count}/result.pkl", "wb") as f:
                    pickle.dump(output, f)
        except Exception:
            print(traceback.format_exc())

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.flag:
                self.call_count += 1
                self.flag = False
            input_data = {"args": args, "kwargs": kwargs}
            output = {"result": func(*args, **kwargs)}
            class_name = None
            if "self" in inspect.signature(func).parameters:
                class_name = args[0].__class__.__name__
            if (
                self.call_count <= 2 # the number of test datasets needed can be altered by changing this variable
                and {"false": False, "true": True}.get(os.getenv("ENABLE_TEST_DATA_CREATION").lower())
                if isinstance(os.getenv("ENABLE_TEST_DATA_CREATION"), str)
                else False  # parse env var string as bool if str input, by default, assume False
            ):
                self.populate_test_data(
                    func, input_data, output, class_name.lower().replace("scraper", "") if class_name else None
                )
            self.flag = True

            return output["result"]

        return wrapper

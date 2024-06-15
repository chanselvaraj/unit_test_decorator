from mathematics import calculation
from create_test import parameterise_test

test_variable_path = r"/test_data/calculation"

def pytest_generate_tests(metafunc):
    for fixture in metafunc.fixturenames:
        data_set = parameterise_test._get_fn_dataset(fixture, test_variable_path)
        metafunc.parametrize(fixture, data_set)



def test_sum_of_even(sum_of_even):
    result = (
        calculation().sum_of_even(**sum_of_even["att"])
    )  # unpack saved argument state
    expectation = sum_of_even["result"]  # unpack saved expectation state
    assert result == expectation

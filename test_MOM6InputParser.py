import pytest
from MOM6InputParser import MOM6InputParser
from unittest.mock import mock_open, call


@pytest.fixture
def simple_input():
    return [
        "! === HEADER1 ===\n",
        "PARAM1 = 1.0                    ! first comment\n",
        "                                ! second comment\n",
        "PARAM2 = True\n",
        "! === HEADER2 ===\n",
        "KPP%\n",
        "PARAM3 = False                  ! first comment\n",
        "                                ! second comment\n",
        "PARAM4 = 100.0                  ! first comment\n",
        "%KPP",
    ]


@pytest.fixture
def param_output():
    return {
        "HEADER1": {"PARAM1": "1.0", "PARAM2": "True"},
        "HEADER2": {
            "KPP%": "",
            "PARAM3": "False",
            "PARAM4": "100.0",
            "%KPP": "",
        },
    }


@pytest.fixture
def comment_output():
    return {
        "HEADER1": {"PARAM1": "first comment\n! second comment", "PARAM2": ""},
        "HEADER2": {
            "KPP%": "",
            "PARAM3": "first comment\n! second comment",
            "PARAM4": "first comment",
            "%KPP": "",
        },
    }


def test_read_input(mocker, simple_input):
    mocker.patch(
        "builtins.open", mocker.mock_open(read_data="".join(simple_input))
    )
    parser = MOM6InputParser()
    parser.read_input("dummy_path")
    print(parser.lines)
    assert parser.lines == simple_input


def test_param_output(simple_input, param_output, comment_output):
    parser = MOM6InputParser()
    parser.lines = simple_input
    parser.parse_lines()
    assert parser.param_dict == param_output
    assert parser.commt_dict == comment_output


def test_write_output(mocker, simple_input):
    # Create the mock_open object
    mock_file = mock_open()

    # Patch the built-in open function to use the mock object
    mocker.patch("builtins.open", mock_file)

    # Create an instance of MOM6InputParser and process the input
    parser = MOM6InputParser()
    parser.lines = simple_input
    parser.parse_lines()

    # Write the output to the mock file
    parser.writefile_MOM_input("dummy_path")

    # Access the file handle from the mock
    handle = mock_file()

    # Print actual calls for debugging
    # print("Actual calls:")
    # for call in handle.write.call_args_list:
    #     print(call)

    # Define the expected write calls, including the hardcoded lines
    expected_calls = [
        call("! This file was written by the script xxx \n"),
        call("! and records the non-default parameters used at run-time.\n"),
        call("\n"),
        call("! === HEADER1 ===\n"),
        call("PARAM1 = 1.0                     ! first comment\n"),
        call("                                 ! second comment\n"),
        call("PARAM2 = True\n"),
        call("\n"),
        call("! === HEADER2 ===\n"),
        call("KPP%\n"),
        call("PARAM3 = False                   ! first comment\n"),
        call("                                 ! second comment\n"),
        call("PARAM4 = 100.0                   ! first comment\n"),
        call("%KPP\n"),
        call("\n"),
    ]
    # Assert that the write method was called with the expected arguments
    handle.write.assert_has_calls(expected_calls, any_order=False)


if __name__ == "__main__":
    pytest.main()

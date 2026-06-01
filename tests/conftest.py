import subprocess
from pathlib import Path

import pytest
from helper import MockExpandMethod, TestMethod

from workflowpy import Workflow
from workflowpy.rule import Rule


# Some basic information
@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Return the path to the testdata directory."""
    return Path(__file__).parent / "_data"


@pytest.fixture
def has_snakemake() -> bool:
    """Return True if snakemake is installed."""
    try:
        subprocess.run(["snakemake", "--version"], check=True)
        return True
    except Exception:
        return False


# Functions and classes used in testing
@pytest.fixture
def test_method():
    return TestMethod(input_file1="test_file1", input_file2="test_file2", param="param")


@pytest.fixture
def workflow() -> Workflow:
    config = {"rps": [2, 50, 100]}
    wildcards = {"region": ["region1", "region2"]}
    return Workflow(name="wf_instance", config=config, wildcards=wildcards)


@pytest.fixture
def mock_expand_method():
    return MockExpandMethod(input_file="test.yml", root="", events=["1", "2"])


@pytest.fixture
def rule(test_method, workflow):
    return Rule(method=test_method, workflow=workflow, rule_id="test_rule")


@pytest.fixture
def w() -> Workflow:
    config = {"rps": [2, 50, 100]}
    wildcards = {"region": ["region1", "region2"]}
    return Workflow(name="wf_instance", config=config, wildcards=wildcards)


@pytest.fixture
def workflow_yaml_dict():
    return {
        "config": {
            "input_file": "tests/_data/region.geojson",
            "events": ["1", "2", "3"],
            "root": "root",
        },
        "rules": [
            {
                "method": "mock_expand_method",
                "kwargs": {
                    "input_file": "$config.input_file",
                    "events": "$config.events",
                    "root": "$config.root",
                },
            },
            {
                "method": "mock_reduce_method",
                "kwargs": {
                    "files": "$rules.mock_expand_method.output.output_file",
                    "root": "$config.root",
                },
            },
        ],
    }

#!/usr/bin/python3
"""Test fixtures."""
import mock
import pytest
from charms import layer


@pytest.fixture
def mock_options(monkeypatch):
    """Mock charm layer options."""
    def options(name):
        return {
            "owner": "mockuser",
            "group": "mockgroup",
            "repo": "mocked-repo",
            "target": "/mock",
        }

    mocked_options = mock.Mock()
    mocked_options.side_effect = options
    monkeypatch.setattr(layer, "options", mocked_options, raising=False)


@pytest.fixture
def mock_hookenv_config(monkeypatch):
    """Mock the hookenv config helper."""
    import yaml

    def mock_config():
        cfg = {}
        yml = yaml.safe_load(open("./config.yaml"))

        # Load all defaults
        for key, value in yml["options"].items():
            cfg[key] = value["default"]

        # Manually add cfg from other layers
        # cfg['my-other-layer'] = 'mock'
        return cfg

    monkeypatch.setattr("charms.layer.git_deploy.config", mock_config)


@pytest.fixture
def mock_chownr(monkeypatch):
    """Mock the charmhelpers chownr call."""
    def chownr_mocked_call(path, owner, group, follow_links=True, chowntopdir=False):
        if owner == "fail-owner" or group == "fail-group" or path == "fail-path":
            return False
        return True

    mocked_chownr = mock.Mock()
    mocked_chownr.side_effect = chownr_mocked_call
    monkeypatch.setattr("charms.layer.git_deploy.chownr", mocked_chownr)
    return mocked_chownr


@pytest.fixture
def mock_check_call(monkeypatch):
    """Mock subprocess check_call on helper."""
    def mocked_check_call(args, *, stdin=None, stdout=None, stderr=None, shell=False):
        print(args)
        if type(args) is list:
            return 0
        return 1

    mock_call = mock.Mock()
    mock_call.side_effect = mocked_check_call
    monkeypatch.setattr("charms.layer.git_deploy.check_call", mock_call)
    return mock_call


@pytest.fixture
def mock_mkdir(monkeypatch):
    """Mock the mkdir function."""
    def mocked_mkdir(path, mode=0o755):
        return True

    monkeypatch.setattr("charms.layer.git_deploy.os.mkdir", mocked_mkdir)


@pytest.fixture
def mock_symlink(monkeypatch):
    """Mock the symlink function."""
    def mocked_symlink(source, dest):
        return True

    monkeypatch.setattr("charms.layer.git_deploy.os.symlink", mocked_symlink)


@pytest.fixture
def git_deploy(
    tmpdir,
    mock_options,
    mock_hookenv_config,
    mock_chownr,
    mock_check_call,
    mock_mkdir,
    mock_symlink,
    monkeypatch,
):
    """Mock the helper library."""
    from charms.layer.git_deploy import GitDeployHelper

    helper = GitDeployHelper()
    helper.target_dir = tmpdir
    helper.timestamp = "2019120100010220"
    helper.deploy_dir = "{}/{}".format(helper.target_dir, helper.timestamp)
    helper.current_deploy = "{}/{}".format(helper.target_dir, "current")

    # Any other functions that load helper will get this version
    monkeypatch.setattr("charms.layer.git_deploy.GitDeployHelper", lambda: helper)

    return helper

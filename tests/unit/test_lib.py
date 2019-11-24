#!/usr/bin/python3
"""Units tests."""
from mock import call


def test_pytest():
    """Test pytest."""
    assert True


def test_git_deploy_helper(git_deploy):
    """See if the helper fixture works to load charm configs."""
    assert isinstance(git_deploy.charm_config, dict)


def test_git_deploy_clone(git_deploy, mock_check_call, mock_chownr, tmpdir):
    """See if the helper fixture works to load charm configs."""
    mock_check_call.reset_mock()
    mock_chownr.reset_mock()
    git_deploy.charm_config["repo"] = "test-repo"
    result = git_deploy.clone()
    mock_check_call.assert_has_calls(
        [
            call(
                [
                    "/usr/bin/git",
                    "clone",
                    "test-repo",
                    "{}/{}".format(tmpdir, git_deploy.timestamp),
                ]
            )
        ]
    )
    assert mock_check_call.call_count == 1
    mock_chownr.assert_has_calls(
        [
            call(group="mockgroup", owner="mockuser", path="{}/{}".format(tmpdir, git_deploy.timestamp)),
            call(group="mockgroup", owner="mockuser", path="{}/{}".format(tmpdir, git_deploy.timestamp)),
        ]
    )
    assert mock_chownr.call_count == 2
    assert result


def test_git_deploy_update(git_deploy, mock_check_call, mock_chownr, tmpdir):
    """See if the helper fixture works to load charm configs."""
    mock_check_call.reset_mock()
    mock_chownr.reset_mock()
    git_deploy.charm_config["repo"] = "test-repo"
    result = git_deploy.update_to_commit("test-commit")
    assert mock_check_call.call_count == 2
    mock_check_call.assert_has_calls(
        [
            call(
                [
                    "/usr/bin/git",
                    "checkout",
                    "test-commit",
                ]
            ),
            call(["/usr/bin/git", "pull"]),
        ]
    )
    assert mock_chownr.call_count == 4
    assert result


def test_git_deploy(git_deploy, mock_check_call, mock_chownr, tmpdir):
    """See if the helper fixture works to load charm configs."""
    mock_check_call.reset_mock()
    mock_chownr.reset_mock()
    git_deploy.charm_config["repo"] = "test-repo"
    git_deploy.charm_config["commit-or-branch"] = "test-branch"
    result = git_deploy.deploy()
    assert mock_check_call.call_count == 3
    mock_check_call.assert_has_calls(
        [
            call(
                [
                    "/usr/bin/git",
                    "clone",
                    "test-repo",
                    "{}/{}".format(tmpdir, git_deploy.timestamp),
                ]
            ),
            call(
                [
                    "/usr/bin/git",
                    "checkout",
                    "test-branch",
                ]
            ),
            call(["/usr/bin/git", "pull"]),
        ]
    )
    assert mock_chownr.call_count == 6
    assert result

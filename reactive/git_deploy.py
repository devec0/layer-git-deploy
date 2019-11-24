"""Reactive layer for deploying application code via Git."""

from charms.layer.git_deploy import GitDeployHelper
from charms.reactive import when_not


@when_not("codebase.available")
def git_deploy_avail():
    """Clone down codebase and set codebase.available state."""
    helper = GitDeployHelper()
    helper.deploy()

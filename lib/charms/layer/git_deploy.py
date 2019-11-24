"""Helper library for the git-deploy reactive charm layer."""
from subprocess import check_call
from charms.reactive import set_state
from charmhelpers.core.host import chownr
from charmhelpers.core.hookenv import config, status_set, log, INFO
from charmhelpers.core.templating import render

import os
import sys
import charms

from shutil import rmtree
from datetime import datetime


class GitDeployHelper:
    """Helper class for the git-deploy layer."""

    def __init__(self):
        """Instantiate variables."""
        self.opts = charms.layer.options("git-deploy")
        self.charm_config = config()
        self.target_dir = self.opts.get("target")
        self.timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%d")
        self.deploy_dir = os.path.join(self.target_dir, self.timestamp)
        self.current_deploy = os.path.join(self.target_dir, "current")

    def check_dir(self, path):
        """Check if dir has been provided and is configured correctly for usage."""
        if path:
            if not os.path.isdir(path):
                os.mkdir(path)
            chownr(
                path=path, owner=self.opts.get("owner"), group=self.opts.get("group")
            )
        return False

    def git(self, args, setenv=False):
        """Format the git command including wrapper."""
        log("Running git operation: {}, setenv={}".format(" ".join(args), setenv), INFO)
        # TODO: Actually manage host keys
        os.environ["GIT_SSH_COMMAND"] = "ssh -o StrictHostKeyChecking=no"
        if setenv:
            os.environ["GIT_DIR"] = "{}/.git".format(self.deploy_dir)
            os.environ["GIT_WORK_TREE"] = self.deploy_dir
        else:
            os.unsetenv("GIT_DIR")
            os.unsetenv("GIT_WORK_TREE")
        self.check_dir(self.deploy_dir)
        cmd = ["/usr/bin/git"]
        cmd.extend(args)
        ret = check_call(cmd)
        self.check_dir(self.deploy_dir)
        return ret

    def clone(self):
        """Perform the git clone operation."""
        log(
            "Cloning {} to {}".format(self.charm_config.get("repo"), self.deploy_dir),
            INFO,
        )
        res = self.git(
            [
                "clone",
                self.charm_config.get("repo"),
                self.deploy_dir,
            ]
        )
        if res != 0:
            if self.charm_config.get("key-required"):
                if self.charm_config.get("deploy-key") is None:
                    status_set("blocked", "Set a deploy_key to continue installation")
                else:
                    status_set("blocked", "Your deploy_key may have been rejected")
            return False
        return True

    def update_to_commit(self, commit):
        """Update prm codebase to a commit sha."""
        self.opts = charms.layer.options("git-deploy")

        if commit:
            res = self.git(["checkout", commit], setenv=True)
        if res != 0:
            status_set(
                "blocked", "git checkout failed, check and correct configuration."
            )
        else:
            res = self.git(["pull"], setenv=True)
            if res != 0:
                status_set(
                    "blocked", "git pull failed, check and correct configuration."
                )
            return True
        return False

    def deploy(self):
        """Perform a deploy from the configured repo."""
        if self.charm_config.get("key-required"):
            if self.charm_config.get("deploy-key") is None:
                status_set("blocked", "Set a deploy_key to continue installation")
                sys.exit(0)

            # Render deploy key
            render(
                source="key",
                target="/root/.ssh/id_rsa",
                perms=0o600,
                context={"key": self.charm_config.get("deploy-key")},
            )

        # Has a repo actually been set?
        if self.charm_config.get("repo"):
            # Check if path exists, remove if it does,
            # then recreate it for idempotency
            if os.path.exists(self.target_dir):
                rmtree(self.target_dir, ignore_errors=True)
            os.makedirs(self.target_dir, mode=0o755, exist_ok=True)
            self.clone()

            # Update to commit if config('commit')
            if self.charm_config.get("commit-or-branch") is not None:
                self.update_to_commit(self.charm_config.get("commit-or-branch"))

            if os.path.exists(self.current_deploy):
                os.remove(self.current_deploy)
            os.symlink(self.deploy_dir, self.current_deploy)

            # Set codebase.available state
            set_state("codebase.available")
            return True
        else:
            status_set("blocked", "The repo config needs to be set before deploy.")
        return False

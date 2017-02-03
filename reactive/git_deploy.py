import os
import sys
from datetime import datetime

from charms.reactive import when_not, set_state

from charmhelpers.core.hookenv import config, status_set
from charmhelpers.core.templating import render

from charms.layer.git_deploy import clone, update_to_commit
from charms.layer import options


@when_not('codebase.available')
def git_deploy_avail():
    """Clone down codebase and set codebase.available state
    """

    opts = options('git-deploy')
    target_dir = opts.get('target')
    parent_dir = os.path.dirname(os.path.normpath(target_dir))
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%d')
    new_deploy_dir = os.path.join(target_dir, timestamp)
    current_deploy = os.path.join(target_dir, 'current')

    if config('key-required'):
        if config('deploy-key') is None:
            status_set('blocked',
                       'Set a deploy_key to continue installation')
            sys.exit(0)

        # Render deploy key
        render(
            source='key',
            target='/root/.ssh/id_rsa',
            perms=0o600,
            context={
              'key': config('deploy-key')
            }
        )

    # Check if path exists, remove if it does,
    # then recreate it for idempotency
    if os.path.exists(target_dir):
        rmtree(target_dir, ignore_errors=True)
    os.makedirs(target_dir, mode=0o755, exist_ok=True)
    clone(deploy_dir=new_deploy_dir)

    # Update to commit if config('commit')
    if config('commit-or-branch') is not None:
        update_to_commit(config('commit-or-branch'), deploy_dir=new_deploy_dir)

    if os.path.exists(current_deploy):
        os.remove(current_deploy)
    os.symlink(new_deploy_dir, current_deploy)

    # Set codebase.available state
    set_state('codebase.available')

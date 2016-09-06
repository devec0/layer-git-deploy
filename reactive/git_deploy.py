from charms.reactive import when_not, set_state
from charmhelpers.core.hookenv import config

from charms.layer.git_deploy import clone, update_to_commit

from charms.layer import options


@when_not('codebase.available')
def git_deploy_avail():
    """Clone down codebase and set codebase.available state
    """

    opts = options('git-deploy')
    # Check if path exists, clone down repo
    if os.path.exists(opts('target')):
        shutil.rmtree(opts('target'), ignore_errors=True)
    clone()

    # Update to commit if config('commit')
    if config('commit') is not None:
        update_to_commit()

    # Chownr app-dir
    chownr(path=opts('target'), owner=opts('owner'), group=opts('group'))

    # Set codebase.available state
    set_state('codebase.available')


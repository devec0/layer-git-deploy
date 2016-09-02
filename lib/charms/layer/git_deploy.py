from subprocess import check_call

from charmhelpers.core.hookenv import (
    charm_dir,
    config,
    status_set,
)

from charms.layer import options


def _git():
    return 'GIT_SSH={} git'.format('{}/files/wrap_ssh.sh'.format(charm_dir()))


def clone():
    cmd =  "{} clone {} {}".format(_git(), config('repo'), options('target'))
    res = check_call(cmd, shell=True)
    if res != 0:
        if config('key-required'):
            if config('deploy-key') is None:
                status_set('blocked',
                           'Set a deploy_key to continue installation')
                sys.exit(0)
            status_set('blocked', 'Your deploy_key may have been rejected')
            sys.exit(0)
        status_set('error', 'has a problem with git, try `resolved --retry')
        sys.exit(1)
    chownr(path=options('target'),
           owner=options('owner'), group=options('group'))


def update_to_commit():
    """Update prm codebase to a commit sha
    """
    cmd = "cd {} && {} checkout {}".format(options('target'), 
                                           _git(), config('commit'))
    res = check_call(cmd, shell=True)
    if res != 0:
        status_set('error', 'has a problem with git, try `resolved --retry')
        sys.exit(1)
    chownr(path=options('target'),
           owner=options('owner'), group=options('group'))

from subprocess import check_call

from charmhelpers.core.hookenv import (
    charm_dir,
    config,
    status_set,
)

from charms.layer import options




def git():
    return 'GIT_SSH={} git'.format('{}/files/wrap_ssh.sh'.format(charm_dir()))


def clone():
    opts = options('git-deploy')
    cmd =  "{} clone {} {}".format(git(), config('repo'), 
                                   opts.get('target'))
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
    chownr(path=opts.get('target'), owner=opts.get('owner'),
           group=opts.get('group'))


def update_to_commit():
    """Update prm codebase to a commit sha
    """
    opts = options('git-deploy')
    cmd = "cd {} && {} checkout {}".format(opts.get('target'),
                                           git(), config('commit'))
    res = check_call(cmd, shell=True)
    if res != 0:
        status_set('error', 'has a problem with git, try `resolved --retry')
        sys.exit(1)
    chownr(path=opts.get('target'), owner=opts.get('owner'),
           group=opts.get('group'))

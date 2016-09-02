from charms.reactive import when, set_state

@when_not('git.deploy.available')
def git_deploy_avail:
    """Set git.deploy.available state so
    other layers know when they can use the
    git, clone, and update_to_commit utility 
    functions.
    """
    set_state('git.deploy.available')


# layer-git-deploy

This layer provides 2 utility functions and 1 actions
that make getting your project code from your git repo 
to your machine a breeze!


### Utils
Once the 'git.deploy.available' state is set, you can access the utility functions
by importing `charms.layer.git_deploy`.


* clone - appropriately titled, preforms 'git clone' of the repo specified in config.yaml
* update_to_commit - also appropriately titled, updates the  codebase to a commit.

##### Example Usage
```python
from charmhelpers.core.hookenv import config, status_set
from charms.reactive import when, when_not, set_state

from charms.layer import git_deploy

@when('git.deploy.available')
@when_not('codebase.deployed')
def clone_repo():
    git_deploy.clone()
    if config('commit'):
        git_deploy.update_to_commit()
    set_state('codebase.deployed')
```

### Actions
This layer defines the following action:
* update-app <commit-sha> - update application to commit sha, takes commit sha as arg

To use this action, once your charm that has been built with this layer is deployed,
you can use Juju to run the action from the Juju cli. E.g `juju run-action <mycharm>/0 update-app <commit-sha>`.

### States
* `'git.deploy.available'` - set once layer-git-deploy is available


#### Contributors
* Chris MacNaughton <chris.macnaughton@canonical.com> - Actions and utils
* James Beedy <jamesbeedy@gmail.com> - Reactive layer

# layer-git-deploy

This layer provides a git abstraction for github/gitlab code deploys that
makes getting your project code from your git repo to your machine a breeze!

Once the 'codebase.available' state is set, you can be assured your project code has been
cloned down to the 'target' directory.

##### Example Usage
```python
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.hookenv import service_restart
from charms.reactive import when, when_not, set_state

from charms.layer import git_deploy

@when('codebase.available')
@when_not('app.initialized')
def init_app():
    service_restart('nginx')
    set_state('app.initialized')
```

### Actions
This layer defines the following action:
* update-app <commit-sha> - update application to commit sha, takes commit sha as arg

To use this action, once your charm that has been built with this layer is deployed,
you can use Juju to run the action from the Juju cli. E.g `juju run-action <mycharm>/0 update-app <commit-sha>`.

### States
* `'codebase.available'` - set once the codebase has been successfully cloned from the remote repository.


#### Contributors
* Chris MacNaughton <chris.macnaughton@canonical.com> - Actions and utils
* James Beedy <jamesbeedy@gmail.com> - Reactive layer

import os
import pytest
import subprocess
import stat

# Treat all tests as coroutines
pytestmark = pytest.mark.asyncio

juju_repository = os.getenv("JUJU_REPOSITORY", ".").rstrip("/")
series = [
    "xenial",
    "bionic",
    pytest.param('eoan', marks=pytest.mark.xfail(reason='canary')),
]

# Uncomment for re-using the current model, useful for debugging functional tests
# @pytest.fixture(scope='module')
# async def model():
#     from juju.model import Model
#     model = Model()
#     await model.connect_current()
#     yield model
#     await model.disconnect()


# Custom fixtures
@pytest.fixture(params=series)
def series(request):
    return request.param


@pytest.fixture
async def app(model, series):
    app_name = "git-deploy-{}".format(series)
    return await model._wait_for_new("application", app_name)


async def test_static_site_deploy(model, series, request):
    # Starts a deploy for each series
    # Using subprocess b/c libjuju fails with JAAS
    # https://github.com/juju/python-libjuju/issues/221
    application_name = "git-deploy-{}".format(series)
    cmd = [
        "juju",
        "deploy",
        "{}/builds/git-deploy".format(
            juju_repository
        ),
        "-m",
        model.info.name,
        "--series",
        series,
        application_name,
    ]
    if request.node.get_closest_marker("xfail"):
        cmd.append("--force")
    subprocess.check_call(cmd)


# Tests
async def test_static_site_status(model, app):
    # Verifies status for all deployed series of the charm
    await model.block_until(lambda: app.status == "active")
    unit = app.units[0]
    await model.block_until(lambda: unit.agent_status == "idle")


async def test_update_action(app):
    unit = app.units[0]
    action = await unit.run_action("update")
    action = await action.wait()
    assert action.status == "completed"


async def test_run_command(app, jujutools):
    unit = app.units[0]
    cmd = "hostname -i"
    results = await jujutools.run_command(cmd, unit)
    assert results["Code"] == "0"
    assert unit.public_address in results["Stdout"]


async def test_file_stat(app, jujutools):
    unit = app.units[0]
    path = "/var/lib/juju/agents/unit-{}/charm/metadata.yaml".format(
        unit.entity_id.replace("/", "-")
    )
    fstat = await jujutools.file_stat(path, unit)
    assert stat.filemode(fstat.st_mode) == "-rw-r--r--"
    assert fstat.st_uid == 0
    assert fstat.st_gid == 0

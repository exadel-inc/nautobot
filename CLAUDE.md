# CLAUDE.md

Guidance for coding agents working in this repository.

## Testing in the agent container

The Colleague agent image runs Nautobot's tests without Docker. Postgres 16, Redis and a WebDriver
endpoint run on 127.0.0.1, and `INVOKE_NAUTOBOT_LOCAL=True` is already set. Check the services with
`cat /tmp/eae-test-env.status`, and run every command from the repository root.

### Unit tests

Run the tests for the code you changed:

    invoke tests --keepdb --no-input --skip-docs-build --no-parallel --label nautobot.dcim.tests.test_views

or call the Django test runner directly:

    nautobot-server --config=nautobot/core/tests/nautobot_config.py test --keepdb --no-input nautobot.dcim.tests.test_forms

### Integration (Selenium) tests

These are the UI end-to-end tests under `nautobot/*/tests/integration/`. CI runs them in the
`integration-test` job.

- **Where they run:** headless Firefox through geckodriver on `127.0.0.1:4444`. The image sets
  `NAUTOBOT_SELENIUM_URL` and `NAUTOBOT_SELENIUM_HOST`.
- **When to run them:** for any change to templates, views, forms, tables, JavaScript or CSS, or
  anything else a user sees in the web UI. Run the integration module for the area you changed:

      nautobot-server --config=nautobot/core/tests/nautobot_config.py test --keepdb --no-input --tag integration nautobot.dcim.tests.integration.test_create_device

- **If geckodriver isn't running:** start it first:

      curl -fsS http://127.0.0.1:4444/status >/dev/null || (setsid nohup geckodriver --host 127.0.0.1 --port 4444 >/tmp/geckodriver.log 2>&1 &)

- **For a UI bug fix:** add or extend an integration test that reproduces the bug when one is
  feasible, and run it before and after the fix.
- **Enforced by a hook:** in the agent container, the Stop hook in `.claude/settings.json`
  (`.claude/hooks/require_integration_tests.py`) blocks finishing once when the branch changes
  web-UI code and no `--tag integration` run happened in the session. Outside that container
  it does nothing.
- **Avoid the full suite:** `--tag integration` with no label runs all of it, which takes a long
  time. Use labels.

### Lint and format

Run these on the files you changed:

    ruff check --fix <files>
    ruff format <files>
    invoke pylint

Note that `invoke pylint` is slow, and CI runs it as a separate check.

### Reporting

In the PR description, list each test command you ran with its result line (for example
`Ran 5 tests ... OK`). If you did not run integration tests, say so explicitly and give the
reason.

## Pull requests

PR descriptions follow `.github/PULL_REQUEST_TEMPLATE.md`. Add a change fragment as
`changes/<issue>.<type>.md`; see the "Creating changelog fragments" section of the contributing
documentation.

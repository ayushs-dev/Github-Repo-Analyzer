# conftest.py is loaded by pytest before any test file.
#
# Our Settings class (app/services/config.py) REQUIRES a GITHUB_TOKEN and crashes
# on import without one. Tests must never use a real token, so we set a fake one
# here, before the app gets imported. setdefault keeps any value already provided
# (for example by CI).
import os

os.environ.setdefault("GITHUB_TOKEN", "test-token-not-real")

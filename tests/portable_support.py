"""Fixture-only vault injection; production has no env or config bypass for this."""
import os
import secrets
from unittest.mock import patch


def isolate_vault(testcase, hub):
    if os.name == "nt":
        return  # Windows regressions continue using actual DPAPI.
    keys = {}
    def key(root, create=False):
        identity = hub._adapters.platform_io.account(root)
        if create:
            keys.setdefault(identity, secrets.token_bytes(32))
        if identity not in keys:
            raise hub._adapters.platform_io.PlatformError("Fixture key unavailable")
        return keys[identity]
    for target, name, value in ((hub._adapters.platform_io, "state_key", key),
                                (hub, "native_continuation_verified", lambda: True)):
        mocked = patch.object(target, name, value)
        mocked.start()
        testcase.addCleanup(mocked.stop)

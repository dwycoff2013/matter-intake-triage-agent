import importlib
import sys


def test_app_agent_import_does_not_import_google_adk_when_absent_from_cache():
    for module_name in list(sys.modules):
        if module_name == "app.agent" or module_name.startswith("google.adk"):
            sys.modules.pop(module_name, None)
    module = importlib.import_module("app.agent")
    assert hasattr(module, "main")
    assert "google.adk" not in sys.modules

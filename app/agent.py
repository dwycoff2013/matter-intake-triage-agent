"""Application entrypoint and lightweight CLI demo."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _load_sample_intake() -> str:
    sample_path = Path(__file__).resolve().parent.parent / "demo" / "sample_intake_email_1.md"
    return sample_path.read_text(encoding="utf-8")


def get_root_agent() -> Any:
    """Load the ADK root agent lazily for ADK runners.

    The local CLI smoke demo intentionally does not call this helper, so it can
    run without google-adk, Google credentials, or live model access.
    """
    from app.coordinator import coordinator_agent

    return coordinator_agent


def __getattr__(name: str) -> Any:
    if name == "root_agent":
        return get_root_agent()
    raise AttributeError(name)


def main() -> None:
    """Run a no-credential smoke demo using the synthetic sample intake."""
    sample = _load_sample_intake()
    print("Matter Intake Triage Agent CLI smoke demo")
    print("=" * 43)
    print("Loaded synthetic sample from demo/sample_intake_email_1.md.")
    print("No real client data, API keys, ADK imports, or model calls are used in this demo.\n")

    preview = sample.strip().splitlines()[:12]
    print("Sample preview:")
    print("\n".join(preview))

    print("\nFull ADK web UI usage requires google-adk==2.3.* and configured credentials.")
    print("Run `adk web agents` or `adk run agents/lextriage` after setting GOOGLE_API_KEY in an uncommitted .env file.")


if __name__ == "__main__":
    main()

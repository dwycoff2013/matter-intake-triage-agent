"""Application entrypoint and lightweight CLI demo."""

from pathlib import Path

try:
    from app.coordinator import coordinator_agent
except ModuleNotFoundError as exc:
    if not (exc.name or "").startswith("google"):
        raise
    coordinator_agent = None

root_agent = coordinator_agent


def _load_sample_intake() -> str:
    sample_path = Path(__file__).resolve().parent.parent / "demo" / "sample_intake_email_1.md"
    return sample_path.read_text(encoding="utf-8")


def main() -> None:
    """Run a no-credential smoke demo using the synthetic sample intake."""
    sample = _load_sample_intake()
    print("Matter Intake Triage Agent CLI smoke demo")
    print("=" * 43)
    print("Loaded synthetic sample from demo/sample_intake_email_1.md.")
    print("No real client data, API keys, or model calls are used in this demo.\n")

    preview = sample.strip().splitlines()[:12]
    print("Sample preview:")
    print("\n".join(preview))

    print("\nFull ADK web UI usage still requires google-adk and configured credentials.")
    print("Run `adk web app` after setting GOOGLE_API_KEY in an uncommitted .env file.")


if __name__ == "__main__":
    main()

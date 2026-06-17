from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class DemoCheck:
    label: str
    path: Path
    required_text: tuple[str, ...] = ()


CHECKS = (
    DemoCheck(
        "main demo flow doc",
        REPO_ROOT / "docs/demo/main-flow.md",
        ("config", "queue", "raw evidence", "insights"),
    ),
    DemoCheck(
        "system architecture demo doc",
        REPO_ROOT / "docs/demo/system-architecture.md",
        ("Config service", "Visibility service", "Insights service"),
    ),
    DemoCheck(
        "technical implementation demo doc",
        REPO_ROOT / "docs/demo/technical-implementation.md",
        ("OpenSpec", "Cypress", "Poetry"),
    ),
    DemoCheck(
        "Cypress demo spec",
        REPO_ROOT / "apps/web/cypress/e2e/demo.cy.ts",
        ("Brandlight interview demo", "data-cy"),
    ),
    DemoCheck(
        "Cypress config",
        REPO_ROOT / "apps/web/cypress.config.ts",
        ("defineConfig", "specPattern"),
    ),
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check and print the Brandlight demo walkthrough.")
    parser.add_argument(
        "--commands-only",
        action="store_true",
        help="Print the demo command sequence without validating files.",
    )
    args = parser.parse_args(argv)

    if not args.commands_only:
        failures = _validate_files()
        if failures:
            for failure in failures:
                print(failure)
            return 1

    print("Brandlight demo walkthrough commands:")
    print("1. poetry run dev")
    print("2. poetry run demo-e2e --skip-migrations")
    print("3. poetry run web-check")
    print("4. poetry run web-e2e")
    print("5. Open http://127.0.0.1:5173 and follow docs/demo/main-flow.md")
    print("")
    print("Demo docs:")
    print("- docs/demo/system-architecture.md")
    print("- docs/demo/technical-implementation.md")
    print("- docs/demo/main-flow.md")
    return 0


def _validate_files() -> list[str]:
    failures: list[str] = []
    for check in CHECKS:
        if not check.path.is_file():
            failures.append(f"missing {check.label}: {check.path.relative_to(REPO_ROOT)}")
            continue
        text = check.path.read_text(encoding="utf-8")
        for marker in check.required_text:
            if marker not in text:
                failures.append(
                    f"{check.label} missing marker {marker!r}: {check.path.relative_to(REPO_ROOT)}"
                )
    return failures


if __name__ == "__main__":
    raise SystemExit(main())

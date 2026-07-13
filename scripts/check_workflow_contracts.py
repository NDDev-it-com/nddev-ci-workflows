#!/usr/bin/env python3
"""Reusable-workflow contract: every workflow except the self workflows
(`ci.yml`, `release.yml`) must be reusable (`on: workflow_call`). The self
workflows must NOT be reusable, and `ci.yml` must expose the `ci-gate` job that
branch protection requires as a status check. Caller-provided command runners
must also fail on the first failing command instead of returning the status of
only the final command. The Go pack's history-depth input remains a typed,
backward-compatible pass-through to checkout.
"""
from __future__ import annotations

import sys

from _workflow_yaml import SELF_WORKFLOWS, get_on, is_reusable, load_yaml, workflow_files


def check() -> list[str]:
    problems: list[str] = []
    for path in workflow_files():
        doc = load_yaml(path)
        reusable = is_reusable(doc)
        if path.name in SELF_WORKFLOWS:
            if reusable:
                problems.append(f"{path.name}: self workflow must not be `on: workflow_call`")
        elif not reusable:
            problems.append(f"{path.name}: reusable workflow missing `on: workflow_call`")

    ci = load_yaml((workflow_files()[0].parent / "ci.yml"))
    jobs = ci.get("jobs", {}) or {}
    if "ci-gate" not in jobs:
        problems.append("ci.yml: missing required `ci-gate` job (branch-protection status check)")

    go_ci = load_yaml((workflow_files()[0].parent / "go-ci.yml"))
    go_on = get_on(go_ci)
    go_call = go_on.get("workflow_call", {}) if isinstance(go_on, dict) else {}
    go_inputs = go_call.get("inputs", {}) if isinstance(go_call, dict) else {}
    fetch_depth = go_inputs.get("fetch_depth", {}) if isinstance(go_inputs, dict) else {}
    if not isinstance(fetch_depth, dict) or (
        fetch_depth.get("type") != "number" or fetch_depth.get("default") != 1
    ):
        problems.append(
            "go-ci.yml: fetch_depth must remain a number with the "
            "backward-compatible default 1"
        )
    go_steps = go_ci.get("jobs", {}).get("go", {}).get("steps", [])
    checkout = next(
        (
            step
            for step in go_steps
            if isinstance(step, dict) and step.get("name") == "Checkout"
        ),
        {},
    )
    checkout_with = checkout.get("with", {})
    actual_depth = (
        checkout_with.get("fetch-depth")
        if isinstance(checkout_with, dict)
        else None
    )
    if actual_depth != "${{ inputs.fetch_depth }}":
        problems.append(
            "go-ci.yml: Checkout must pass fetch_depth through to actions/checkout"
        )

    private_static = load_yaml((workflow_files()[0].parent / "private-static.yml"))
    static_steps = private_static.get("jobs", {}).get("static", {}).get("steps", [])
    steps_by_name = {step.get("name"): step for step in static_steps if isinstance(step, dict)}
    fail_fast_commands = {
        "Run install command": 'bash -euo pipefail -c "$INSTALL_COMMAND"',
        "Run validation": 'bash -euo pipefail -c "$VALIDATION_COMMAND"',
    }
    for name, expected in fail_fast_commands.items():
        actual = steps_by_name.get(name, {}).get("run")
        if actual != expected:
            problems.append(
                f"private-static.yml: {name!r} must use the fail-fast runner {expected!r}"
            )
    return problems


def main() -> int:
    problems = check()
    if problems:
        print("check_workflow_contracts: FAIL", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print("check_workflow_contracts: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

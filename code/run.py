"""Run the coastal-protection local/MSI workflow."""

from __future__ import annotations

import argparse
import sys

sys.dont_write_bytecode = True

import initialization


CONFIG = {
    "enabled_tasks": ["validate_project_layout"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--task",
        action="append",
        choices=sorted(initialization.TASK_REGISTRY),
        help="Task to run; repeat this option to select multiple tasks.",
    )
    parser.add_argument("--list-tasks", action="store_true", help="List registered tasks and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Show resolved paths and task order only.")
    parser.add_argument(
        "--project-root",
        default=None,
        help="Override the project root (or set COASTAL_PROTECTION_PROJECT_ROOT).",
    )
    parser.add_argument("--start-year", type=int, default=1996, help="First storm season to include.")
    parser.add_argument("--end-year", type=int, default=2026, help="Last storm season to include.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.list_tasks:
        for task_name in initialization.TASK_REGISTRY:
            print(task_name)
        return 0

    config = dict(CONFIG)
    config["enabled_tasks"] = args.task or list(CONFIG["enabled_tasks"])
    config["storm_start_year"] = args.start_year
    config["storm_end_year"] = args.end_year
    if args.project_root:
        config["project_root"] = args.project_root

    project = initialization.LocalProjectFlow()
    initialization.initialize_paths(project, config)

    if args.dry_run:
        print("Resolved paths:")
        for name, path in project.paths.items():
            print(f"  {name}: {path}")
        print("Task order:")
        for index, name in enumerate(config["enabled_tasks"], start=1):
            print(f"  {index}. {name}")
        return 0

    initialization.build_task_tree(project, config)
    project.execute()
    print("[complete] Workflow finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

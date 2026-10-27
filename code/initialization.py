"""Path registry and ordered task runner for coastal-protection work."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

import tasks


TASK_REGISTRY: dict[str, Callable] = {
    "validate_project_layout": tasks.validate_project_layout,
    "audit_stormarea_inputs": tasks.audit_stormarea_inputs,
    "prepare_msi_dem_download": tasks.prepare_msi_dem_download,
    "download_nhc_storm_tracks": tasks.download_nhc_storm_tracks,
}


class LocalProjectFlow:
    """Small task runner with explicit order and shared project paths."""

    def __init__(self) -> None:
        self.tasks: list[tuple[str, Callable]] = []
        self.paths: dict[str, Path | tuple[Path, ...]] = {}
        self.config: dict[str, object] = {}
        self.results: dict[str, object] = {}

    def add_task(self, name: str, task_function: Callable) -> None:
        self.tasks.append((name, task_function))

    def execute(self) -> dict[str, object]:
        total = len(self.tasks)
        for index, (name, task_function) in enumerate(self.tasks, start=1):
            print(f"[task {index}/{total}] START {name}")
            try:
                result = task_function(self)
            except Exception as exc:
                print(f"[task {index}/{total}] FAILED {name}: {exc}")
                raise
            self.results[name] = result
            print(f"[task {index}/{total}] DONE {name}")
        return self.results


def _unique_paths(paths: list[Path]) -> tuple[Path, ...]:
    unique: list[Path] = []
    for path in paths:
        resolved = path.expanduser().resolve()
        if resolved not in unique:
            unique.append(resolved)
    return tuple(unique)


def initialize_paths(
    project: LocalProjectFlow,
    config: dict[str, object] | None = None,
) -> LocalProjectFlow:
    """Resolve local/MSI paths once; input data may live outside the code checkout."""
    config = dict(config or {})
    code_root = Path(__file__).resolve().parent
    checkout_root = code_root.parent
    configured_root = os.environ.get("COASTAL_PROTECTION_PROJECT_ROOT") or config.get("project_root")
    project_root = Path(configured_root).expanduser().resolve() if configured_root else checkout_root.resolve()

    scratch_root = Path("/scratch.global/yxlong/projects/coastal_protection")
    home_root = Path.home() / "projects" / "coastal_protection"
    extra_roots = [
        Path(value).expanduser()
        for value in os.environ.get("COASTAL_PROTECTION_DATA_ROOTS", "").split(os.pathsep)
        if value.strip()
    ]
    data_roots = _unique_paths([scratch_root, home_root, *extra_roots, project_root])

    def existing_or_default(relative: str, *, directory: bool = False) -> Path:
        for root in data_roots:
            candidate = root / relative
            if candidate.is_dir() if directory else candidate.is_file():
                return candidate.resolve()
        return (project_root / relative).resolve()

    output = project_root / "outputs"
    dem_relative = Path("data/raw/usgs_3dep_13arcsec_dem")
    project.paths = {
        "code": code_root,
        "project_root": project_root,
        "data_roots": data_roots,
        "data": project_root / "data",
        "raw": project_root / "data" / "raw",
        "processed": project_root / "data" / "processed",
        "study_area_boundary": existing_or_default(
            "data/processed/final_study_area_noaa_shoreline_conus_except_great_lakes_boundary.gpkg"
        ),
        "county_boundaries": existing_or_default("data/raw/counties/tl_2023_us_county.shp"),
        "hurdat2_tracks": existing_or_default("data/processed/hurdat2_tracks_1996_2025.csv"),
        "nhc_storm_track_root": project_root / "data" / "raw" / "nhc_storm_tracks",
        "slosh_root": existing_or_default("data/raw/noaa_storm_surge/extracted", directory=True),
        "dem_root": existing_or_default(str(dem_relative), directory=True),
        "dem_tile_manifest": existing_or_default(
            str(dem_relative / "dem_tile_manifest_final_shoreline_counties_except_great_lakes.csv")
        ),
        "dem_tiles": existing_or_default(str(dem_relative / "tiles"), directory=True),
        "stormarea_output": project_root / "data" / "processed" / "stormarea_2017_2025",
        "output": output,
        "figures": output / "figures",
        "tables": output / "tables",
        "logs": output / "logs",
        "msi": output / "msi",
        "msi_dem_download_script": output / "msi" / "download_usgs_3dep_dem.sh",
    }
    project.config = config
    project.results = {}
    print(f"[paths] project root: {project_root}")
    print("[paths] data roots: " + " -> ".join(map(str, data_roots)))
    return project


def build_task_tree(project: LocalProjectFlow, config: dict[str, object]) -> LocalProjectFlow:
    """Validate configured task names and register them in requested order."""
    enabled_tasks = list(config.get("enabled_tasks", []))
    unknown_tasks = [name for name in enabled_tasks if name not in TASK_REGISTRY]
    if unknown_tasks:
        raise ValueError(f"Unknown enabled tasks: {unknown_tasks}")
    if not enabled_tasks:
        raise ValueError("Select at least one task.")
    project.tasks.clear()
    for task_name in enabled_tasks:
        project.add_task(task_name, TASK_REGISTRY[task_name])
    return project


# Register coastal land-mask and NAVD88 3DEP download task.
import tasks as _pipeline_tasks
TASK_REGISTRY.setdefault("download_coastal_dem_inputs", _pipeline_tasks.download_coastal_dem_inputs)

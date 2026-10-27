"""Thin ProjectFlow task wrappers for coastal-protection data preparation."""

from __future__ import annotations

import functions


def validate_project_layout(project):
    """Create ignored working directories and report expected input availability."""
    return functions.validate_project_layout(project)


def audit_stormarea_inputs(project):
    """Report inputs needed for the Sun-Carson-style storm-area construction."""
    return functions.audit_stormarea_inputs(project)


def prepare_msi_dem_download(project):
    """Write, but do not submit, a resumable DEM downloader for MSI."""
    return functions.prepare_msi_dem_download(project)


def download_nhc_storm_tracks(project):
    """Download NHC storm tracks and wind-radius source files for the requested years."""
    return functions.download_nhc_storm_tracks(project)

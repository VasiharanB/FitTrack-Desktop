"""UI package for FitTrack Enterprise."""
from ui.styles import configure_styles
from ui.dashboard import FitTrackDashboard
from ui.table import HealthRecordTable
from ui.dialogs import AlertDialog, ConfirmDialog, SettingsDialog

__all__ = [
    "configure_styles",
    "FitTrackDashboard",
    "HealthRecordTable",
    "AlertDialog",
    "ConfirmDialog",
    "SettingsDialog",
]

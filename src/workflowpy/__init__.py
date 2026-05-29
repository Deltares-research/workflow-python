"""Library template."""

from .version import __version__
from .workflow import Wildcards, Workflow, WorkflowConfig

__all__ = [
    "Wildcards",
    "Workflow",
    "WorkflowConfig",
]

"""Chain-of-Thought code review pipeline.

Public API:
    CoTPipeline    - the orchestrator
    ReviewResult   - aggregated step outputs
    ReviewContext  - per-run context passed to each step
    register_step  - decorator to add a custom review step
    create_backend - factory to build a backend from config
"""

from prthinker.config import BackendKind, Config
from prthinker.pipeline import CoTPipeline, ReviewContext, ReviewResult
from prthinker.steps import ReviewStep, register_step
from prthinker.backends import create_backend

__all__ = [
    "BackendKind",
    "Config",
    "CoTPipeline",
    "ReviewContext",
    "ReviewResult",
    "ReviewStep",
    "register_step",
    "create_backend",
]

__version__ = "0.1.0"

"""Chain-of-Thought code review pipeline.

Public API:
    CoTPipeline    - the orchestrator
    ReviewResult   - aggregated step outputs
    ReviewContext  - per-run context passed to each step
    register_step  - decorator to add a custom review step
    create_backend - factory to build a backend from config
"""

from reviewmind.config import BackendKind, Config
from reviewmind.pipeline import CoTPipeline, ReviewContext, ReviewResult
from reviewmind.steps import ReviewStep, register_step
from reviewmind.backends import create_backend

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

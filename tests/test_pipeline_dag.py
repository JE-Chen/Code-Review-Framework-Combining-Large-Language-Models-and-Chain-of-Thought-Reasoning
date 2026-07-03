from prthinker.backends.base import InferenceBackend
from prthinker.pipeline import CoTPipeline
from prthinker.rag import NoOpRetriever


class Backend(InferenceBackend):
    concurrency_limit = 2

    def generate(self, prompt, max_new_tokens, *, cancel_event=None):
        return "ok"


def test_pipeline_uses_typed_dag_config():
    pipeline = CoTPipeline(
        Backend(),
        NoOpRetriever(),
        steps=("first_summary", "linter"),
        step_dependencies={
            "first_summary": {"depends_on": [], "cache": True},
            "linter": {
                "depends_on": ["first_summary"],
                "when_result": "first_summary",
                "timeout_seconds": 2,
            },
        },
    )
    result = pipeline.run("diff --git a/a.py b/a.py\n+x=1")
    assert result.step_outputs == {"first_summary": "ok", "linter": "ok"}

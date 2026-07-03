"""Optional OpenTelemetry spans using GenAI semantic attribute names."""

from __future__ import annotations
from contextlib import contextmanager
from typing import Mapping, Any


def configure(endpoint: str = "", service_name: str = "prthinker") -> bool:
    """Configure OTLP tracing when the observability extra is installed."""
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        return False
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint or None))
    )
    trace.set_tracer_provider(provider)
    return True


@contextmanager
def inference_span(backend: str, model: str, max_tokens: int):
    try:
        from opentelemetry import trace
    except ImportError:
        yield None
        return
    with trace.get_tracer("prthinker").start_as_current_span(
        "gen_ai.generate_content"
    ) as span:
        span.set_attribute("gen_ai.operation.name", "generate_content")
        span.set_attribute("gen_ai.provider.name", backend)
        span.set_attribute("gen_ai.request.model", model)
        span.set_attribute("gen_ai.request.max_tokens", max_tokens)
        try:
            yield span
        except Exception as exc:
            span.record_exception(exc)
            span.set_attribute("error.type", type(exc).__name__)
            raise


@contextmanager
def operation_span(name: str, attributes: Mapping[str, Any] | None = None):
    """Create an optional agent/retrieval/tool span without recording content."""
    try:
        from opentelemetry import trace
    except ImportError:
        yield None
        return
    with trace.get_tracer("prthinker").start_as_current_span(name) as span:
        for key, value in (attributes or {}).items():
            if value is not None:
                span.set_attribute(key, value)
        try:
            yield span
        except Exception as exc:
            span.record_exception(exc)
            span.set_attribute("error.type", type(exc).__name__)
            raise

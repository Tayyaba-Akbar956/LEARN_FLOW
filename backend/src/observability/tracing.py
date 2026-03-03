"""OpenTelemetry tracing configuration for code execution flow."""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import os

# Initialize tracer provider
resource = Resource.create({"service.name": "learnflow-code-execution"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer_provider = trace.get_tracer_provider()

# Configure exporters
if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
    # Production: export to OTLP collector
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
        insecure=True
    )
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
else:
    # Development: export to console
    console_exporter = ConsoleSpanExporter()
    tracer_provider.add_span_processor(BatchSpanProcessor(console_exporter))

# Get tracer instance
tracer = trace.get_tracer(__name__)


def trace_code_execution(func):
    """Decorator to trace code execution functions."""
    def wrapper(*args, **kwargs):
        with tracer.start_as_current_span(
            f"code_execution.{func.__name__}",
            attributes={
                "function": func.__name__,
                "module": func.__module__
            }
        ) as span:
            try:
                result = func(*args, **kwargs)
                span.set_attribute("execution.success", True)
                return result
            except Exception as e:
                span.set_attribute("execution.success", False)
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
                span.record_exception(e)
                raise
    return wrapper

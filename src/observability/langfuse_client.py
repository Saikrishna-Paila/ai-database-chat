"""
Langfuse Client for LLM Observability
Updated for Langfuse v3 API
"""

from typing import Optional, Any
from contextlib import contextmanager

from src.config import settings

# Conditional import for Langfuse
try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    Langfuse = None


class LangfuseClient:
    """Wrapper for Langfuse observability client (v3 API)"""

    def __init__(self):
        self._client: Optional[Any] = None
        self._enabled = settings.langfuse_enabled and LANGFUSE_AVAILABLE
        self._init_failed = False

    @property
    def client(self) -> Optional[Any]:
        """Lazy load Langfuse client"""
        if not self._enabled or self._init_failed:
            return None

        if self._client is None and LANGFUSE_AVAILABLE:
            try:
                self._client = Langfuse(
                    public_key=settings.langfuse_public_key,
                    secret_key=settings.langfuse_secret_key,
                    host=settings.langfuse_host
                )
            except Exception as e:
                print(f"Langfuse initialization failed: {e}")
                self._init_failed = True
                return None
        return self._client

    @property
    def is_enabled(self) -> bool:
        """Check if Langfuse is enabled and available"""
        return self._enabled and not self._init_failed and self.client is not None

    def start_span(self, name: str, input_data: Any = None, metadata: dict = None):
        """Start a new span (auto-creates trace)"""
        if not self.is_enabled:
            return None

        try:
            span = self.client.start_span(
                name=name,
                input=input_data,
                metadata=metadata or {}
            )
            return span
        except Exception as e:
            print(f"Langfuse span creation failed: {e}")
            return None

    def end_span(self, span, output: Any = None):
        """End a span"""
        if span is not None:
            try:
                if output is not None:
                    span.update(output=output)
                span.end()
            except Exception as e:
                print(f"Langfuse span end failed: {e}")

    def start_generation(self, parent_span, name: str, model: str, input_data: Any = None):
        """Start a generation nested under a span"""
        if parent_span is None:
            return None

        try:
            gen = parent_span.start_observation(
                name=name,
                as_type="generation"
            )
            gen.update(model=model, input=input_data)
            return gen
        except Exception as e:
            print(f"Langfuse generation creation failed: {e}")
            return None

    def end_generation(self, generation, output: str = None, usage: dict = None):
        """End a generation"""
        if generation is not None:
            try:
                update_data = {}
                if output is not None:
                    update_data["output"] = output
                if usage is not None:
                    update_data["usage"] = usage
                if update_data:
                    generation.update(**update_data)
                generation.end()
            except Exception as e:
                print(f"Langfuse generation end failed: {e}")

    def flush(self):
        """Flush any pending events"""
        if self.is_enabled:
            try:
                self.client.flush()
            except Exception as e:
                print(f"Langfuse flush failed: {e}")

    def shutdown(self):
        """Shutdown the client"""
        if self.is_enabled:
            try:
                self.client.shutdown()
            except Exception as e:
                print(f"Langfuse shutdown failed: {e}")


# Singleton instance
_langfuse_client: Optional[LangfuseClient] = None


def get_langfuse() -> LangfuseClient:
    """Get the singleton Langfuse client instance"""
    global _langfuse_client
    if _langfuse_client is None:
        _langfuse_client = LangfuseClient()
    return _langfuse_client


@contextmanager
def trace_context(name: str, input_data: Any = None, metadata: dict = None):
    """Context manager for tracing"""
    langfuse = get_langfuse()
    span = langfuse.start_span(name=name, input_data=input_data, metadata=metadata)
    try:
        yield span
    finally:
        if span:
            langfuse.end_span(span)
        langfuse.flush()

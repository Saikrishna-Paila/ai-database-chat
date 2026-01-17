"""
Tracing Decorators and Utilities for Langfuse v3
"""

from functools import wraps
from typing import Callable, Any, Optional
import time

from .langfuse_client import get_langfuse


def trace_query(name: str = "database_query"):
    """Decorator to trace database queries"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            langfuse = get_langfuse()

            if not langfuse.is_enabled:
                return func(*args, **kwargs)

            span = langfuse.start_span(
                name=name,
                metadata={
                    "function": func.__name__,
                    "args_count": len(args)
                }
            )

            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                langfuse.end_span(span, output={
                    "success": True,
                    "duration_ms": duration * 1000
                })

                return result

            except Exception as e:
                duration = time.time() - start_time

                langfuse.end_span(span, output={
                    "success": False,
                    "error": str(e),
                    "duration_ms": duration * 1000
                })

                raise

            finally:
                langfuse.flush()

        return wrapper
    return decorator


def trace_generation(name: str = "llm_generation", model: str = None):
    """Decorator to trace LLM generations"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            langfuse = get_langfuse()

            if not langfuse.is_enabled:
                return func(*args, **kwargs)

            span = langfuse.start_span(name=name)
            used_model = kwargs.get('model', model) or "unknown"

            generation = langfuse.start_generation(
                parent_span=span,
                name="generation",
                model=used_model,
                input_data=kwargs.get('messages', [])
            )

            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                langfuse.end_generation(
                    generation,
                    output=str(result)[:1000] if result else None,
                    usage={"duration_ms": duration * 1000}
                )
                langfuse.end_span(span, output={"success": True})

                return result

            except Exception as e:
                langfuse.end_generation(generation, output=f"Error: {str(e)}")
                langfuse.end_span(span, output={"success": False, "error": str(e)})
                raise

            finally:
                langfuse.flush()

        return wrapper
    return decorator


class QueryTracer:
    """Class-based tracer for more complex tracing scenarios"""

    def __init__(self, user_id: Optional[str] = None):
        self.langfuse = get_langfuse()
        self.user_id = user_id
        self.root_span = None
        self.current_span = None

    def start_trace(self, name: str, metadata: dict = None):
        """Start a new trace (creates root span)"""
        if self.langfuse.is_enabled:
            self.root_span = self.langfuse.start_span(
                name=name,
                metadata=metadata
            )
        return self

    def start_span(self, name: str, input_data: Any = None):
        """Start a nested span"""
        if self.langfuse.is_enabled and self.root_span:
            try:
                self.current_span = self.root_span.start_span(
                    name=name,
                    input=input_data
                )
            except Exception as e:
                print(f"Nested span failed: {e}")
        return self

    def end_span(self, output: Any = None):
        """End the current span"""
        if self.current_span:
            try:
                if output:
                    self.current_span.update(output=output)
                self.current_span.end()
            except Exception as e:
                print(f"End span failed: {e}")
            self.current_span = None
        return self

    def log_generation(
        self,
        name: str,
        model: str,
        input_messages: list,
        output: str,
        usage: dict = None
    ):
        """Log an LLM generation"""
        if self.langfuse.is_enabled and self.root_span:
            gen = self.langfuse.start_generation(
                parent_span=self.root_span,
                name=name,
                model=model,
                input_data=input_messages
            )
            self.langfuse.end_generation(gen, output=output, usage=usage)
        return self

    def log_score(self, name: str, value: float, comment: str = None):
        """Log a score"""
        if self.root_span:
            try:
                self.root_span.score(name=name, value=value, comment=comment)
            except Exception as e:
                print(f"Score failed: {e}")
        return self

    def end(self):
        """End the trace and flush"""
        if self.root_span:
            self.langfuse.end_span(self.root_span)
        self.langfuse.flush()

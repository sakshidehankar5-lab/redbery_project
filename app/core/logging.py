"""
Aspect-Based Logging
--------------------
Provides:
  - Structured JSON logging via loguru
  - @log_execution  decorator  – logs entry/exit + duration
  - @log_exceptions decorator  – logs & re-raises exceptions
  - request_id context var     – injected per HTTP request
"""
import functools
import sys
import time
import traceback
import uuid
from contextvars import ContextVar
from typing import Any, Callable, TypeVar

from loguru import logger

from app.core.config import get_settings

settings = get_settings()

# ── Context variable (set per request in middleware) ──────────────────────────
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


# ── Logger configuration ──────────────────────────────────────────────────────

def configure_logging() -> None:
    """Configure loguru sinks once at startup."""
    logger.remove()  # remove default sink

    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
        "<yellow>req_id={extra[request_id]}</yellow> | "
        "{message}"
    )

    # Console sink
    logger.add(
        sys.stdout,
        format=fmt,
        level=settings.log_level,
        colorize=True,
        diagnose=settings.debug,
    )

    # File sink (structured JSON for production)
    logger.add(
        settings.log_file,
        format="{time} | {level} | {name}:{line} | req_id={extra[request_id]} | {message}",
        level=settings.log_level,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        serialize=True,          # JSON lines
        enqueue=True,            # thread-safe async write
        backtrace=True,
        diagnose=settings.debug,
    )


def get_logger(name: str):
    """Return a contextualised logger bound to the current request_id."""
    return logger.bind(request_id=request_id_ctx.get() or "-", logger_name=name)


# ── Decorator helpers ─────────────────────────────────────────────────────────

F = TypeVar("F", bound=Callable[..., Any])


def log_execution(func: F) -> F:
    """
    Decorator — logs method/function entry, exit, and wall-clock duration.
    Works on both sync and async callables.
    """
    _log = get_logger(func.__module__)

    if _is_async(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            _log.info(f"▶ ENTER {func.__qualname__} | args_count={len(args)} kwargs={list(kwargs.keys())}")
            t0 = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed = (time.perf_counter() - t0) * 1000
                _log.info(f"◀ EXIT  {func.__qualname__} | duration={elapsed:.2f}ms")
                return result
            except Exception:
                elapsed = (time.perf_counter() - t0) * 1000
                _log.error(f"✖ ERROR {func.__qualname__} | duration={elapsed:.2f}ms")
                raise
        return async_wrapper  # type: ignore
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            _log.info(f"▶ ENTER {func.__qualname__} | args_count={len(args)} kwargs={list(kwargs.keys())}")
            t0 = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.perf_counter() - t0) * 1000
                _log.info(f"◀ EXIT  {func.__qualname__} | duration={elapsed:.2f}ms")
                return result
            except Exception:
                elapsed = (time.perf_counter() - t0) * 1000
                _log.error(f"✖ ERROR {func.__qualname__} | duration={elapsed:.2f}ms")
                raise
        return sync_wrapper  # type: ignore


def log_exceptions(func: F) -> F:
    """
    Decorator — logs full traceback on exception, then re-raises.
    """
    _log = get_logger(func.__module__)

    if _is_async(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                _log.error(
                    f"Unhandled exception in {func.__qualname__}: {exc}\n"
                    + traceback.format_exc()
                )
                raise
        return async_wrapper  # type: ignore
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                _log.error(
                    f"Unhandled exception in {func.__qualname__}: {exc}\n"
                    + traceback.format_exc()
                )
                raise
        return sync_wrapper  # type: ignore


def _is_async(func: Callable) -> bool:
    import asyncio
    return asyncio.iscoroutinefunction(func)

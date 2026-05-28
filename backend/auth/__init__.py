"""Auth package."""

__all__ = ["router"]

# Lazy import to avoid relative-import errors when pytest imports submodules directly.
def __getattr__(name: str):
    if name == "router":
        from .router import router
        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

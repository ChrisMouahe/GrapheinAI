"""LazyModelLoader for on-demand initialization of heavy ML models and vector stores."""

import logging
from typing import Any, Callable

logger = logging.getLogger("LazyModelLoader")


class LazyModelLoader:
    """Utility enabling deferred, on-demand instantiation of heavy resources."""

    def __init__(self) -> None:
        self._instances: dict[str, Any] = {}
        self._factories: dict[str, Callable[[], Any]] = {}

    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """Registers a model instantiation factory callable."""
        self._factories[name] = factory

    def get_instance(self, name: str) -> Any:
        """Retrieves or lazily instantiates a named model instance."""
        if name in self._instances:
            return self._instances[name]

        if name not in self._factories:
            raise KeyError(f"No lazy factory registered for model '{name}'.")

        logger.info(f"LazyModelLoader: Lazily instantiating model '{name}' on demand...")
        instance = self._factories[name]()
        self._instances[name] = instance
        return instance

    def is_loaded(self, name: str) -> bool:
        """Returns True if the specified model is already instantiated in memory."""
        return name in self._instances

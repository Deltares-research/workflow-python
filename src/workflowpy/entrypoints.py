"""workflowpy Method entry points."""

from typing import TYPE_CHECKING, ClassVar, Dict, Optional, Union

from importlib_metadata import EntryPoint, entry_points

if TYPE_CHECKING:
    from workflowpy import Method

__all__ = ["METHODS"]

__eps__ = {
    "script_method": "workflowpy.methods.script:ScriptMethod",
}  # Register our single built-in method


class MethodEPS:
    """Method entry points.

    The class is used to allow users to contribute methods and
    load local methods lazily. Methods are loaded by name or class name.
    """

    group: ClassVar[str] = "workflowpy"

    def __init__(self, eps: Optional[Dict[str, Union[str, EntryPoint]]] = None) -> None:
        """Initialize."""
        # cache entry points by name property and class.__name__
        self._entry_points: Dict[str, EntryPoint] = {}
        # local eps
        eps = eps or {}
        # load other eps
        for ep in entry_points(group=self.group):
            ep_dict = ep.load()
            if isinstance(ep_dict, dict):
                eps.update(ep_dict)
            else:
                raise ValueError(f"Invalid entry point {ep} in group {self.group}")
        # add eps
        for name, ep in eps.items():
            self.set_ep(name, ep)

    @property
    def entry_points(self) -> Dict[str, EntryPoint]:
        """List of method entry points."""
        return self._entry_points

    def set_ep(self, name: str, ep: Union[str, EntryPoint]) -> None:
        name = name.lower()
        if name in self._entry_points:
            raise ValueError(f"Duplicate entry point {name}")
        if isinstance(ep, str):
            ep = EntryPoint(name, ep, self.group)
        elif not isinstance(ep, EntryPoint):
            raise ValueError(f"Invalid entry point {ep}")
        self._entry_points[name] = ep

    def get_ep(self, name: str) -> EntryPoint:
        """Get entry point by name."""
        name = name.lower()
        ep = self.entry_points.get(name)
        if ep is None:  # try by class name
            for ep0 in self.entry_points.values():
                if ep0.value.split(":")[-1].split(".")[-1].lower() == name:
                    ep = ep0
                    break
        if ep is None:
            raise ValueError(f"Method {name} not found")
        return ep

    def load(self, name: str) -> "Method":
        """Load method by name."""
        from workflowpy import Method

        obj = self.get_ep(name).load()
        if not issubclass(obj, Method):
            raise ValueError(f"Method {name} is not a valid Method")

        return obj


METHODS = MethodEPS(__eps__)

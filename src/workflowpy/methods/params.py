"""Some enhanced parameters."""

import json
from pathlib import Path
from typing import Any, ClassVar

from pydantic import ConfigDict, model_validator

from workflowpy.parameters import Parameters

__all__ = [
    "ExtraFileParameters",
    "ParamsFromDict",
]


class ExtraFileParameters(Parameters):
    """Extra file parameters.

    For input and output.
    """

    # Allow extra fields in the model
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def check_extra_fields_are_paths(self):
        """Check that all extra fields are Path types."""
        for key, value in self:
            if value is None:
                continue  # skip None values such as initial script
            try:
                setattr(self, key, Path(value))
            except Exception:
                raise ValueError(f"{key} not a Path type ({type(value)})")
        return self


class ParamsFromDict(Parameters):
    """Parse parameters form a dictionary."""

    _type: ClassVar[str]

    # Allow extra fields in the model
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def _input_to_dict(cls, data: Any) -> Any:
        """Convert the input field to a dictionary."""
        # check if json and convert to dict
        if isinstance(data, str) and data.startswith("{") and data.endswith("}"):
            # replace single quotes with double quotes
            data = json.loads(data.replace("'", '"'))
        # check if single path and convert to dict
        elif isinstance(data, (Path, str)):
            data = {f"{cls._type}1": data}
        # check if list and convert to dict
        elif isinstance(data, list):
            data = {f"{cls._type}{i + 1}": item for i, item in enumerate(data)}
        return data

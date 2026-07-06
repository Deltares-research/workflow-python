"""Dummy methods for testing and user documentation."""

from pathlib import Path

from workflowpy import Parameters, ReduceMethod
from workflowpy._typing import ListOfPath, WildcardPath


class Input(Parameters):
    """Input files for the DummyCombine method."""

    model_out_ncs: ListOfPath | WildcardPath
    """Model output netcdf files to be combined.
    This argument expects either a path with a wildcard or a list of paths."""


class Params(Parameters):
    """Parameters for the DummyCombine method."""

    output_dir: Path | None = None
    """Output directory"""


class Output(Parameters):
    """Output files for the DummyCombine method."""

    combined_out_nc: Path
    """Combined model output netcdf file"""


class DummyCombine(ReduceMethod):
    """Combine multiple dummy events.

    Parameters
    ----------
    model_out_ncs : List[Path] | WildcardPath
        Model output netcdf files to be combined.
        This argument expects either a path with a wildcard or a list of paths.
    output_dir : Path, optional
        The output directory, by default None
    **params
        Additional parameters to pass to the DummyCombine Params instance.
        See :py:class:`~workflowpy.methods._dummy.combine.Params`
    """

    name = "_dummy_combine"

    _test_kwargs = {
        "model_out_ncs": ["out1.nc", "out2.nc"],
        "output_dir": "output",
    }

    def __init__(
        self,
        model_out_ncs: ListOfPath | WildcardPath,
        output_dir: Path | None = None,
        **params,
    ):
        self.input: Input = Input(model_out_ncs=model_out_ncs)
        self.params: Params = Params(output_dir=output_dir, **params)
        self.output: Output = Output(
            combined_out_nc=self.params.output_dir / "events_combined.nc"
        )

    def _run(self):
        # Combine the model outputs
        self.output.combined_out_nc.touch()

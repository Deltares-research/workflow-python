"""Dummy methods for testing and user documentation."""

from pathlib import Path

from workflowpy import Method, Parameters


class Input(Parameters):
    """Input files for the DummyPostprocess method."""

    model_nc: Path
    """Model output netcdf file"""


class Output(Parameters):
    """Output files for the DummyPostprocess method."""

    postprocessed_nc: Path
    """Postprocessed netcdf file"""


class Params(Parameters):
    """Parameters for the DummyPostprocess method."""

    output_dir: Path
    """The output directory"""

    event_name: str
    """The event name"""


class DummyPostprocess(Method):
    """Postprocess a dummy event.

    Parameters
    ----------
    model_nc : Path
        Model output netcdf file
    output_dir : Path
        The output directory
    event_name : str, optional
        The event name, by default None
    """

    name = "_dummy_postprocess"

    _test_kwargs = {
        "model_nc": "model.nc",
        "output_dir": "output",
    }

    def __init__(
        self,
        model_nc: Path,
        output_dir: Path,
        event_name: str | None = None,
    ):
        self.input: Input = Input(model_nc=model_nc)
        event_name = event_name or self.input.model_nc.stem
        self.params: Params = Params(output_dir=output_dir, event_name=event_name)
        self.output: Output = Output(
            postprocessed_nc=self.params.output_dir
            / f"event_{event_name}_postprocessed.nc"
        )

    def _run(self):
        # Run model and save output
        self.output.postprocessed_nc.touch()

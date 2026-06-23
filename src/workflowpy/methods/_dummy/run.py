"""Dummy methods for testing and user documentation."""

from pathlib import Path
from typing import Literal

from workflowpy import Method, Parameters


class Input(Parameters):
    """Input files for the DummyRun method."""

    event_csv: Path
    """Event csv file"""

    settings_toml: Path
    """Model sttings file"""

    model_exe: Path | None = None
    """Model executable, required if run_method is 'exe'"""


class Output(Parameters):
    """Output files for the DummyRun method."""

    model_out_nc: Path
    """Model output netcdf file"""


class Params(Parameters):
    """Parameters for the DummyRun method."""

    run_method: Literal["exe", "docker"] = "exe"
    """How to run the model"""

    output_dir: Path
    """The output directory"""

    event_name: str
    """The event name"""


class DummyRun(Method):
    """Run a dummy event.

    Parameters
    ----------
    event_csv : Path
        Event csv file
    settings_toml : Path
        Model settings file
    output_dir : Path
        Output directory
    event_name : str, optional
        The event name, by default None
    model_exe : Path, optional
        Model executable, required if run_method is 'exe', by default None
    **params
        Additional parameters to pass to the DummyRun Params instance.
        See :py:class:`~workflowpy.methods._dummy.run.Params`.
    """

    name = "_dummy_run"

    _test_kwargs = {
        "event_csv": "event.csv",
        "settings_toml": "settings.toml",
        "output_dir": "output",
        "run_method": "docker",
    }

    def __init__(
        self,
        event_csv: Path,
        settings_toml: Path,
        output_dir: Path,
        event_name: str | None = None,
        model_exe: Path | None = None,
        **params,
    ):
        self.input: Input = Input(
            event_csv=event_csv, settings_toml=settings_toml, model_exe=model_exe
        )
        event_name = event_name or self.input.event_csv.stem
        self.params: Params = Params(
            output_dir=output_dir, event_name=event_name, **params
        )
        if self.params.run_method == "exe" and model_exe is None:
            raise ValueError("Model executable is required for run_method 'exe'")
        self.output: Output = Output(
            model_out_nc=self.params.output_dir / f"event_{event_name}_result.nc"
        )

    def _run(self):
        # Dummy run model and save output
        self.output.model_out_nc.touch()

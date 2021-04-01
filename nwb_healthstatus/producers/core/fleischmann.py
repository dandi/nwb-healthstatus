import datetime
from pathlib import Path

import hdmf
import numpy as np
import pandas as pd
import pynwb

np.random.seed(42)
metadata = dict(
    session_description="my first synthetic recording",
    identifier="EXAMPLE_ID",
    session_start_time=datetime.datetime(
        year=2021, month=3, day=3, tzinfo=datetime.timezone.utc
    ),
    experimenter=("Dr. Bilbo Baggins",),
    lab="Bag End Laboratory",
    institution="University of Middle Earth at the Shire",
    experiment_description="I went on an adventure with thirteen dwarves to reclaim vast treasures.",
    session_id="LONELYMTN",
)
serie_length = 10
acquisition = {
    "name1": "my_awesome_timeserie",
    "name2": "my_awesome_timeserie",
    "data": np.random.random(serie_length),
    "timestamps": np.linspace(0, 0.1, serie_length),
    "unit": "squirrel squared",
    "trials": np.arange(0, 0.1, 0.02),
}


def create():
    nwbfile = pynwb.NWBFile(**metadata)
    timeserie1 = pynwb.TimeSeries(
        name=acquisition["name1"],
        data=acquisition["data"],
        timestamps=acquisition["timestamps"],
        unit=acquisition["unit"],
    )
    timeserie2 = pynwb.TimeSeries(
        name=acquisition["name2"],
        data=acquisition["data"],
        timestamps=acquisition["timestamps"],
        unit=acquisition["unit"],
    )
    nwbfile.add_stimulus(timeserie1)
    nwbfile.add_acquisition(timeserie2)
    for trial in acquisition["trials"]:
        nwbfile.add_trial(
            start_time=trial,
            stop_time=trial + (acquisition["trials"][1] - acquisition["trials"][0]) / 2,
        )

    return nwbfile


def test_basic(nwbfile):
    # TODO: make it more specific to this example
    for f, v in metadata.items():
        assert getattr(nwbfile, f) == v, f"{f}: {getattr(nwbfile, f)!r} vs. {v!r}"


if __name__ == "__main__":
    base_filename = Path(__file__).name
    env_details = {
        "nwb": pynwb.__version__,
        "hdmf": hdmf.__version__,
    }
    suffix = "_".join("{}:{}".format(*i) for i in env_details.items())

    filename = f"/tmp/{base_filename}_{suffix}"

    ### this would be executed once for some combinations of hdmf/pynwb
    ### version and stored indefinetely somewhere
    nwbfile = create()
    with pynwb.NWBHDF5IO(filename + ".nwb", "w") as io:
        io.write(nwbfile)  # , cache_spec=cache_spec)
    # todo dump into '.yaml' the details of the spec

    ### CI run would load the file and give it away for testing
    with pynwb.NWBHDF5IO(filename + ".nwb", mode="r") as io:
        ## capture and display possible warnings
        obj = io.read()

        test_basic(obj)

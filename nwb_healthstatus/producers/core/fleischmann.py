import datetime
from pathlib import Path

import numpy as np
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
    "name1": "my_awesome_timeserie1",
    "name2": "my_awesome_timeserie2",
    "data": np.random.random(serie_length),
    "timestamps": np.linspace(0, 0.1, serie_length),
    "unit": "squirrel squared",
    "trials": np.arange(0, 0.1, 0.02),
}


class Fleischmann:
    EXTENSIONS = set()
    FILENAME = "fleischmann.nwb"

    def create(self):
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
        nwbfile.add_acquisition(timeserie1)
        nwbfile.add_stimulus(timeserie2)
        for trial in acquisition["trials"]:
            nwbfile.add_trial(
                start_time=trial,
                stop_time=trial
                + (acquisition["trials"][1] - acquisition["trials"][0]) / 2,
            )
        return nwbfile

    def test(self, nwbfile):
        for f, v in metadata.items():
            assert getattr(nwbfile, f) == v, f"{f}: {getattr(nwbfile, f)!r} vs. {v!r}"
        np.testing.assert_array_equal(
            nwbfile.acquisition[acquisition["name1"]].data[:], acquisition["data"]
        )
        np.testing.assert_array_equal(
            nwbfile.acquisition[acquisition["name1"]].timestamps[:],
            acquisition["timestamps"],
        )
        np.testing.assert_array_equal(
            nwbfile.stimulus[acquisition["name2"]].data[:], acquisition["data"]
        )
        np.testing.assert_array_equal(
            nwbfile.stimulus[acquisition["name2"]].timestamps[:],
            acquisition["timestamps"],
        )
        np.testing.assert_array_equal(
            nwbfile.trials.columns[0].data[:], acquisition["trials"]
        )

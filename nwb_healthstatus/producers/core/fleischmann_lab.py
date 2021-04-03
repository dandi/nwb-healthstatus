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
timeseries = {
    "name1": "my_awesome_timeserie1",
    "name2": "my_awesome_timeserie2",
    "data": np.random.random(serie_length),
    "timestamps": np.linspace(0, 0.1, serie_length),
    "unit": "squirrel squared",
    "trials": np.arange(0, 0.1, 0.02),
}
ops = {
    "Ly": 150,
    "Lx": 150,
    "filelist": ["/path/to/tiff/files"],
    "fs": 4.5,
    "nplanes": 3,
}


class Fleischmann:
    EXTENSIONS = set()
    FILENAME = "fleischmann.nwb"

    def create(self):
        nwbfile = pynwb.NWBFile(**metadata)

        # TimeSeries
        timeserie1 = pynwb.TimeSeries(
            name=timeseries["name1"],
            data=timeseries["data"],
            timestamps=timeseries["timestamps"],
            unit=timeseries["unit"],
        )
        timeserie2 = pynwb.TimeSeries(
            name=timeseries["name2"],
            data=timeseries["data"],
            timestamps=timeseries["timestamps"],
            unit=timeseries["unit"],
        )
        nwbfile.add_acquisition(timeserie1)
        nwbfile.add_stimulus(timeserie2)
        for trial in timeseries["trials"]:
            nwbfile.add_trial(
                start_time=trial,
                stop_time=trial
                + (timeseries["trials"][1] - timeseries["trials"][0]) / 2,
            )

        # Ophys
        device = nwbfile.create_device(
            name="Microscope",
            description="My two-photon microscope",
            manufacturer="The best microscope manufacturer",
        )
        optical_channel = pynwb.ophys.OpticalChannel(
            name="OpticalChannel",
            description="an optical channel",
            emission_lambda=500.0,
        )
        imaging_plane = nwbfile.create_imaging_plane(
            name="ImagingPlane",
            optical_channel=optical_channel,
            imaging_rate=ops["fs"],
            description="standard",
            device=device,
            excitation_lambda=600.0,
            indicator="GCaMP",
            location="V1",
            grid_spacing=([2.0, 2.0, 30.0]),
            grid_spacing_unit="microns",
        )
        image_series = pynwb.ophys.TwoPhotonSeries(
            name="TwoPhotonSeries",
            dimension=[ops["Ly"], ops["Lx"]],
            external_file=(ops["filelist"] if "filelist" in ops else [""]),
            imaging_plane=imaging_plane,
            starting_frame=[0],
            format="external",
            starting_time=0.0,
            rate=ops["fs"] * ops["nplanes"],
        )
        nwbfile.add_acquisition(image_series)
        img_seg = pynwb.ophys.ImageSegmentation()
        ps = img_seg.create_plane_segmentation(
            name="PlaneSegmentation",
            description="suite2p output",
            imaging_plane=imaging_plane,
            reference_images=image_series,
        )
        ophys_module = nwbfile.create_processing_module(
            name="ophys", description="optical physiology processed data"
        )
        ophys_module.add(img_seg)

        return nwbfile

    def test(self, nwbfile):
        for f, v in metadata.items():
            assert getattr(nwbfile, f) == v, f"{f}: {getattr(nwbfile, f)!r} vs. {v!r}"
        np.testing.assert_array_equal(
            nwbfile.acquisition[timeseries["name1"]].data[:], timeseries["data"]
        )
        np.testing.assert_array_equal(
            nwbfile.acquisition[timeseries["name1"]].timestamps[:],
            timeseries["timestamps"],
        )
        np.testing.assert_array_equal(
            nwbfile.stimulus[timeseries["name2"]].data[:], timeseries["data"]
        )
        np.testing.assert_array_equal(
            nwbfile.stimulus[timeseries["name2"]].timestamps[:],
            timeseries["timestamps"],
        )
        np.testing.assert_array_equal(
            nwbfile.trials.columns[0].data[:], timeseries["trials"]
        )
        PlaneSegmentation = (
            nwbfile.processing["ophys"]
            .data_interfaces["ImageSegmentation"]
            .plane_segmentations["PlaneSegmentation"]
        )
        assert PlaneSegmentation.imaging_plane.imaging_rate == ops["fs"]
        assert nwbfile.acquisition["TwoPhotonSeries"].rate == ops["fs"] * ops["nplanes"]
        assert (
            nwbfile.acquisition["TwoPhotonSeries"].external_file[:] == ops["filelist"]
        )
        np.testing.assert_array_equal(
            nwbfile.acquisition["TwoPhotonSeries"].dimension[:], [ops["Ly"], ops["Lx"]]
        )

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
CONST = {"serie_length": 10, "ncells": 10, "pix_dim": 150}
timeseries = {
    "name1": "my_awesome_timeserie1",
    "name2": "my_awesome_timeserie2",
    "data": np.random.random(CONST["serie_length"]),
    "timestamps": np.linspace(0, 0.1, CONST["serie_length"]),
    "unit": "squirrel squared",
    "trials": np.arange(0, 0.1, 0.02),
}
ophys = {
    "Ly": CONST["pix_dim"],
    "Lx": CONST["pix_dim"],
    "filelist": ["/path/to/tiff/files"],
    "fs": 4.5,
    "nplanes": 3,
    "ypix": np.random.randint(0, CONST["pix_dim"], CONST["ncells"]),
    "xpix": np.random.randint(0, CONST["pix_dim"], CONST["ncells"]),
    "lam": np.random.random(CONST["ncells"]),
    "iscell": np.random.choice(2, CONST["ncells"]),
    "traces": 100 * np.random.rand(CONST["ncells"], CONST["serie_length"]),
}


class FleischmannLab:
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
            imaging_rate=ophys["fs"],
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
            dimension=[ophys["Ly"], ophys["Lx"]],
            external_file=(ophys["filelist"] if "filelist" in ophys else [""]),
            imaging_plane=imaging_plane,
            starting_frame=[0],
            format="external",
            starting_time=0.0,
            rate=ophys["fs"] * ophys["nplanes"],
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

        for n in range(CONST["ncells"]):
            pixel_mask = np.array(
                [
                    ophys["ypix"][n],
                    ophys["xpix"][n],
                    ophys["lam"][n],
                ]
            )
            ps.add_roi(pixel_mask=pixel_mask.reshape((1, 3)))
        ps.add_column("iscell", "two columns - iscell & probcell", ophys["iscell"])
        rt_region = ps.create_roi_table_region(
            region=list(np.arange(0, CONST["ncells"])), description="all ROIs"
        )

        roi_resp_series = (
            pynwb.ophys.RoiResponseSeries(
                name="Plane_1",
                data=ophys["traces"],
                rois=rt_region,
                unit="lumens",
                rate=ophys["fs"],
            ),
        )
        fl = pynwb.ophys.Fluorescence(
            roi_response_series=roi_resp_series, name="Fluorescence"
        )
        ophys_module.add(fl)

        yield ("core", self.FILENAME, nwbfile)

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
        assert PlaneSegmentation.imaging_plane.imaging_rate == ophys["fs"]
        assert (
            nwbfile.acquisition["TwoPhotonSeries"].rate
            == ophys["fs"] * ophys["nplanes"]
        )
        assert (
            nwbfile.acquisition["TwoPhotonSeries"].external_file[:] == ophys["filelist"]
        )
        np.testing.assert_array_equal(
            nwbfile.acquisition["TwoPhotonSeries"].dimension[:],
            [ophys["Ly"], ophys["Lx"]],
        )
        np.testing.assert_array_equal(
            PlaneSegmentation["iscell"].data[:], ophys["iscell"]
        )

        roi_resp = (
            nwbfile.processing["ophys"]
            .data_interfaces["Fluorescence"]
            .roi_response_series["Plane_1"]
        )
        np.testing.assert_array_equal(roi_resp.data[:], ophys["traces"])

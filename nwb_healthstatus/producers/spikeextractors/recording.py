import datetime
from pathlib import Path
import tempfile

from appdirs import user_cache_dir
import datalad.api as dl
from pynwb import NWBFile
import spikeextractors as se


class _CommonBase:
    EXTENSIONS = set()

    # To be defined in subclass
    SCENARIOS = None

    def __init__(self):
        self.pt = Path(user_cache_dir("nwb-healthstatus", "dandi"), "ephy_testing_data")
        existant = self.pt.exists()
        self.dataset = dl.install(
            source="https://gin.g-node.org/NeuralEnsemble/ephy_testing_data",
            path=self.pt,
        )
        if existant:
            self.dataset.update(
                merge=True
            )  # to ensure that up to date if existed before

    def test(self, nwbfile):
        # TODO: not yet sure if anything
        pass


class Extractors(_CommonBase):
    # TODO: propose PR to spikeextractors to have these defined in accessible atribute/constant so
    # we do not have to copy/paste them
    # Changes introduced: removed Path.cwd() / "ephy_testing_data"  prefix -- should be a relpath under self.dataset
    SCENARIOS = [
        (
            se.BlackrockRecordingExtractor,
            "blackrock/blackrock_2_1",
            dict(
                filename=Path("blackrock", "blackrock_2_1", "l101210-001"),
                seg_index=0,
                nsx_to_load=5,
            ),
        ),
        (
            se.IntanRecordingExtractor,
            "intan",
            dict(file_path=Path("intan", "intan_rhd_test_1.rhd")),
        ),
        (
            se.IntanRecordingExtractor,
            "intan",
            dict(file_path=Path("intan", "intan_rhs_test_1.rhs")),
        ),
        # Klusta - no .prm config file in ephy_testing
        # (
        #     se.KlustaRecordingExtractor,
        #     "kwik",
        #     dict(folder_path=Path("kwik")),
        # ),
        #
        # Fails with assertion error:
        # (
        #     se.MEArecRecordingExtractor,
        #     "mearec/mearec_test_10s.h5",
        #     dict(file_path=Path("mearec", "mearec_test_10s.h5")),
        # ),
        (
            se.NeuralynxRecordingExtractor,
            "neuralynx/Cheetah_v5.7.4/original_data",
            dict(
                dirname=Path("neuralynx", "Cheetah_v5.7.4", "original_data"),
                seg_index=0,
            ),
        ),
        (
            se.NeuroscopeRecordingExtractor,
            "neuroscope/test1",
            dict(file_path=Path("neuroscope", "test1", "test1.dat")),
        ),
        # Nixio - RuntimeError: Cannot open non-existent file in ReadOnly mode!
        # (
        #     se.NIXIORecordingExtractor,
        #     "nix",
        #     dict(file_path=str(Path("neoraw.nix"))),
        # ),
        (
            se.OpenEphysRecordingExtractor,
            "openephys/OpenEphys_SampleData_1",
            dict(folder_path=Path("openephys", "OpenEphys_SampleData_1")),
        ),
        (
            se.OpenEphysRecordingExtractor,
            "openephysbinary/v0.4.4.1_with_video_tracking",
            dict(folder_path=Path("openephysbinary", "v0.4.4.1_with_video_tracking")),
        ),
        (
            se.OpenEphysNPIXRecordingExtractor,
            "openephysbinary/v0.5.3_two_neuropixels_stream",
            dict(
                folder_path=Path(
                    "openephysbinary",
                    "v0.5.3_two_neuropixels_stream",
                    "Record_Node_107",
                )
            ),
        ),
        (
            se.NeuropixelsDatRecordingExtractor,
            "openephysbinary/v0.5.3_two_neuropixels_stream",
            dict(
                file_path=Path(
                    "openephysbinary",
                    "v0.5.3_two_neuropixels_stream",
                    "Record_Node_107",
                    "experiment1",
                    "recording1",
                    "continuous",
                    "Neuropix-PXI-116.0",
                    "continuous.dat",
                ),
                settings_file=Path(
                    "openephysbinary",
                    "v0.5.3_two_neuropixels_stream",
                    "Record_Node_107",
                    "settings.xml",
                ),
            ),
        ),
        (
            se.PhyRecordingExtractor,
            "phy/phy_example_0",
            dict(folder_path=Path("phy", "phy_example_0")),
        ),
        # Plexon - AssertionError: This file have several channel groups spikeextractors support only one groups
        # (
        #     se.PlexonRecordingExtractor,
        #     "plexon",
        #     dict(filename=Path("plexon", "File_plexon_2.plx")),
        # ),
        (
            se.SpikeGLXRecordingExtractor,
            "spikeglx/Noise4Sam_g0",
            dict(
                file_path=Path(
                    "spikeglx",
                    "Noise4Sam_g0",
                    "Noise4Sam_g0_imec0",
                    "Noise4Sam_g0_t0.imec0.ap.bin",
                )
            ),
        ),
    ]

    def create(self):
        for se_class, dataset_path, se_kwargs in self.SCENARIOS:
            self.dataset.get(dataset_path)
            for k in [
                "filename",
                "file_path",
                "dirname",
                "folder_path",
                "settings_file",
            ]:
                if k in se_kwargs:
                    se_kwargs[k] = self.pt / se_kwargs[k]
            if "filename" in se_kwargs:
                se_kwargs["filename"] = str(se_kwargs["filename"])
            recording = se_class(**se_kwargs)
            nwbfile = NWBFile(
                identifier="testing",
                session_description="testing",
                session_start_time=datetime.datetime(
                    1970, 1, 1, tzinfo=datetime.timezone.utc
                ),
            )
            se.NwbRecordingExtractor.write_recording(
                recording, nwbfile=nwbfile, write_scaled=True
            )
            yield "spikeextractors", f"{self.__class__.__name__}/{se_class.__name__}/{dataset_path}", nwbfile


class Sorters(_CommonBase):
    # TODO: propose PR to spikeextractors to have these defined in accessible atribute/constant so
    # we do not have to copy/paste them
    SCENARIOS = [
        (
            se.BlackrockSortingExtractor,
            "blackrock/blackrock_2_1",
            dict(
                filename=Path("blackrock", "blackrock_2_1", "l101210-001"),
                seg_index=0,
                nsx_to_load=5,
            ),
        ),
        (
            se.KlustaSortingExtractor,
            "kwik",
            dict(file_or_folder_path=Path("kwik", "neo.kwik")),
        ),
        # Neuralynx - units_ids = nwbfile.units.id[:] - AttributeError: 'NoneType' object has no attribute 'id'
        # Is the GIN data OK? Or are there no units?
        # (
        #     se.NeuralynxSortingExtractor,
        #     "neuralynx/Cheetah_v5.7.4/original_data",
        #     dict(
        #         dirname=Path("neuralynx", "Cheetah_v5.7.4", "original_data"),
        #         seg_index=0
        #     )
        # ),
        # NIXIO - return [int(da.label) for da in self._spike_das]
        # TypeError: int() argument must be a string, a bytes-like object or a number, not 'NoneType'
        # (
        #     se.NIXIOSortingExtractor,
        #     "nix/nixio_fr.nix",
        #     dict(file_path=Path("nix", "nixio_fr.nix")),
        # ),
        (
            se.MEArecSortingExtractor,
            "mearec/mearec_test_10s.h5",
            dict(file_path=Path("mearec", "mearec_test_10s.h5")),
        ),
        (
            se.PhySortingExtractor,
            "phy/phy_example_0",
            dict(folder_path=Path("phy", "phy_example_0")),
        ),
        (
            se.PlexonSortingExtractor,
            "plexon",
            dict(filename=Path("plexon", "File_plexon_2.plx")),
        ),
        (
            se.SpykingCircusSortingExtractor,
            "spykingcircus/spykingcircus_example0",
            dict(
                file_or_folder_path=Path(
                    "spykingcircus", "spykingcircus_example0", "recording"
                ),
            ),
        ),
        # # Tridesclous - dataio error, GIN data is not correct?
        # (
        #     se.TridesclousSortingExtractor,
        #     "tridesclous/tdc_example0",
        #     dict(folder_path=Path("tridesclous", "tdc_example0")),
        # )
    ]

    def create(self):
        # Disabled because trying to convert the data to an NWBFile isn't
        # working
        return
        for se_class, dataset_path, se_kwargs in self.SCENARIOS:
            self.dataset.get(dataset_path)
            for k in [
                "filename",
                "file_or_folder_path",
                "file_path",
                "dirname",
                "folder_path",
            ]:
                if k in se_kwargs:
                    se_kwargs[k] = self.pt / se_kwargs[k]
            if "filename" in se_kwargs:
                se_kwargs["filename"] = str(se_kwargs["filename"])
            sorting = se_class(**se_kwargs)
            sf = sorting.get_sampling_frequency()
            if (
                sf is None
            ):  # need to set dummy sampling frequency since no associated acquisition in file
                sf = 30000
                sorting.set_sampling_frequency(sf)
            with tempfile.NamedTemporaryFile() as tf:
                se.NwbSortingExtractor.write_sorting(sorting, tf.name)
                with pynwb.NWBHDF5IO(tf.name, mode="r") as io:
                    nwbfile = io.read()
                yield "spikeextractors", f"{self.__class__.__name__}/{se_class.__name__}/{dataset_path}", nwbfile

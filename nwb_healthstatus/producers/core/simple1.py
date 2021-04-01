import datetime
import pynwb

metadata = dict(
    session_description= 'my first synthetic recording',
    identifier='EXAMPLE_ID',
    session_start_time=datetime.datetime(year=2021, month=3, day=3, tzinfo=datetime.timezone.utc),
    experimenter=('Dr. Bilbo Baggins',),
    lab='Bag End Laboratory',
    institution='University of Middle Earth at the Shire',
    experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
    session_id='LONELYMTN'
)

class Simple1:
    EXTENSIONS = set()
    FILENAME = "simple1.nwb"

    def create(self):
        return pynwb.NWBFile(**metadata)

    def test(self, nwbfile):
        # TODO: make it more specific to this example
        for f, v in metadata.items():
            assert getattr(nwbfile, f) == v, f"{f}: {getattr(nwbfile, f)!r} vs. {v!r}"

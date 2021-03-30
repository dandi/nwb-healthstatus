import hdmf
import pynwb
import datetime

metadata = dict(
    session_description= 'my first synthetic recording', 
    identifier='EXAMPLE_ID', 
    session_start_time=datetime.datetime(year=2021, month=3, day=3),
    experimenter='Dr. Bilbo Baggins',
    lab='Bag End Laboratory',
    institution='University of Middle Earth at the Shire',
    experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
    session_id='LONELYMTN'
)

def create():
    return pynwb.NWBFile(**metadata)


def test_basic(nwbfile):
    # TODO: make it more specific to this example
    #for f, v in metadata.items():
    #    assert getattr(nwbfile, f) == v
    pass


if __name__ == '__main__':
   base_filename = 'core_simple1'
   env_details = {
      'nwb': pynwb.__version__,
      'hdmf': hdmf.__version__,
   }
   suffix = '_'.join('{}:{}'.format(*i) for i in env_details.items())

   filename = f'/tmp/{base_filename}_{suffix}'

   ### this would be executed once for some combinations of hdmf/pynwb
   ### version and stored indefinetely somewhere
   nwbfile = create()
   with pynwb.NWBHDF5IO(filename + '.nwb', "w") as io:
        io.write(nwbfile) # , cache_spec=cache_spec) 
   # todo dump into '.yaml' the details of the spec

   ### CI run would load the file and give it away for testing
   with pynwb.NWBHDF5IO(filename + '.nwb', mode='r') as io:
        ## capture and display possible warnings
        obj = io.read()

        test_basic(obj)


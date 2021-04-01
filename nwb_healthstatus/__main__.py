from pathlib import Path
import click
import pynwb
from .base import get_cases_in_namespace
from .spec import load_spec

DEFAULT_SAMPLES_PATH = str(Path.home() / ".cache" / "nwb-healthstatus")

@click.group()
def main():
    pass

@main.group()
def sample():
    pass

@sample.command()
#@click.option("-e", "--environment")
@click.option("--overwrite", is_flag=True)
@click.option("--samples-path", type=click.Path(file_okay=False), default=DEFAULT_SAMPLES_PATH)
@click.argument("casefile", type=click.Path(exists=True, dir_okay=False), nargs=-1)
def create(casefile, overwrite, samples_path):
    sample_dir = Path(samples_path)
    for path in casefile:
        p = Path(path)
        producer = p.resolve().parent.name
        namespace = {}
        exec(p.read_text(), namespace)
        for casecls in get_cases_in_namespace(namespace):
            case = casecls()
            filepath = sample_dir / producer / case.FILENAME
            filepath.parent.mkdir(parents=True, exist_ok=True)
            if overwrite or not filepath.exists():
                nwbfile = case.create()
                with pynwb.NWBHDF5IO(str(filepath), "w") as io:
                    io.write(nwbfile) # , cache_spec=cache_spec)

@sample.command()
#@click.option("-e", "--environment")
@click.option("--samples-path", type=click.Path(exists=True, file_okay=False), default=DEFAULT_SAMPLES_PATH)
@click.argument("casefile", type=click.Path(exists=True, dir_okay=False), nargs=-1)
def test(casefile, samples_path):
    sample_dir = Path(samples_path)
    for path in casefile:
        p = Path(path)
        producer = p.resolve().parent.name
        namespace = {}
        exec(p.read_text(), namespace)
        for casecls in get_cases_in_namespace(namespace):
            case = casecls()
            filepath = sample_dir / producer / case.FILENAME
            with pynwb.NWBHDF5IO(str(filepath), mode='r') as io:
                ## TODO: Capture and display possible warnings
                obj = io.read()
            case.test(obj)

@main.group()
def environments():
    pass

@environments.command()
@click.option("-o", "--outdir", type=click.Path(file_okay=False), default="environments")
@click.argument("specfile", type=click.Path(exists=True, dir_okay=False))
def make_dockerfiles(specfile, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    spec = load_spec(specfile)
    for env in spec.environments:
        (outdir / f"Dockerfile.{env.name}").write_text(env.generate_dockerfile())

if __name__ == "__main__":
    main()

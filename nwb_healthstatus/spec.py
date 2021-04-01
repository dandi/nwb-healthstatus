from copy import deepcopy
from pathlib import Path
import re
import subprocess
from typing import List, Optional, Union
from deepmerge import always_merger
from pydantic import BaseModel, Field
import yaml

class Environment(BaseModel):
    base_image: str = Field(alias="base-image")
    name: str
    apt: List[str] = Field(default_factory=list)
    pip: List[str] = Field(default_factory=list)
    on_startup: Optional[str] = None

    def generate_dockerfile(self) -> str:
        cmd = [
            "neurodocker", "generate", "docker",
            "--base", self.base_image,
            "--pkg-manager=apt",
        ]
        if self.apt:
            cmd += ["--install"] + self.apt
        if self.pip:
            cmd += [
                "--miniconda",
                "create_env=local",
                "pip_install=" + " ".join(
                    re.sub(r'\s+', '', p) for p in self.pip
                )
            ]
        if self.on_startup:
            cmd += ["--add-to-entrypoint", self.on_startup]
        return subprocess.check_output(cmd, universal_newlines=True)


class Producer(BaseModel):
    name: str
    environments: List[str]


class Spec(BaseModel):
    environments: List[Environment]
    producers: List[Producer]


def load_spec(filename: Union[str, Path]) -> Spec:
    with open(filename) as fp:
        data = yaml.safe_load(fp)
    base_env = data.pop("base_environment")
    data["environments"] = [
        always_merger.merge(deepcopy(base_env), env)
        for env in data.get("environments", [])
    ]
    print(data["environments"])
    return Spec.parse_obj(data)

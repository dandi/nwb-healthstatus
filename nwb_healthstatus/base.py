from abc import ABC, abstractmethod
from functools import reduce
from inspect import isclass
from operator import or_
from types import ModuleType
from typing import ClassVar, Iterator, Set, Tuple, Type

from hdmf.container import Container
import pynwb


class SampleCase(ABC):
    #: Set of extensions needed by the sample case
    EXTENSIONS: ClassVar[Set[str]]

    @abstractmethod
    def create(self) -> Iterator[Tuple[str, str, pynwb.NWBFile]]:
        """ Creates a sample NWB file """
        ...

    @abstractmethod
    def test(self, data: Container) -> None:
        """
        Takes the data read from a sample file and asserts that it contains
        what it should
        """
        ...

    @classmethod
    def __subclasshook__(cls, C):
        if cls is SampleCase and {"EXTENSIONS", "create", "test"} <= reduce(
            or_, (B.__dict__.keys() for B in C.__mro__)
        ):
            return True
        return NotImplemented


def get_cases_in_module(module: ModuleType) -> Iterator[Type[SampleCase]]:
    for name in dir(module):
        obj = getattr(module, name)
        if isclass(obj) and issubclass(obj, SampleCase):
            yield obj


def get_cases_in_namespace(namespace: dict) -> Iterator[Type[SampleCase]]:
    for obj in namespace.values():
        if isclass(obj) and issubclass(obj, SampleCase):
            yield obj

from pathlib import Path
from typing import Any, Protocol

from GMLID.lib.toml import dump as TOML_dump, load as TOML_load

type AttributeSchema[T] = tuple[str, T]
type CatagorySchema = dict[str, AttributeSchema[Any]]
type DataSchema = dict[str, CatagorySchema]
type DataIO = dict[str, Any]
type FileIO = dict[str, dict[str, Any]]


class SchemaObj(Protocol):
    schema: DataSchema

    def __init__(self, values: dict[str, Any] | None, *args, **kwds) -> None: ...
    def pre_process(self): ...
    def post_process(self): ...


def create_schema[T: SchemaObj](source: Path, cls: type[T], ensure_exists: bool = False) -> T:
    if ensure_exists:
        data: FileIO = {}
        for group, catagory in cls.schema.items():
            data[group] = {}
            for name, (attr, default) in catagory.values():
                data[group][name] = default

        with open(source, "wb") as fp:
            TOML_dump(source, fp, indent=4)

    values: DataIO = {}
    for catagory in cls.schema.values():
        for attr, default in catagory.values():
            values[attr] = default
    obj = cls(values)
    obj.post_process()
    return obj


def load_schema[T: SchemaObj](source: Path, cls: type[T], ensure_exists: bool = False) -> T:
    if not source.exists:
        return create_schema(source, cls, ensure_exists)

    with open(source, "rt") as fp:
        data: FileIO = TOML_load(fp)

    values: DataIO = {}
    for group, catagory in cls.schema.items():
        for name, (attr, _) in catagory.items():
            values[attr] = data.get(group, {}).get(name)

    obj = cls(values)
    obj.post_process()
    return obj


def dump_schema(source: Path, data: SchemaObj) -> dict[str, Any]:
    data.pre_process()
    values: FileIO = {}
    for group, catagory in data.schema.items():
        values[group] = {}
        for name, (attr, default) in catagory.items():
            values[group][name] = getattr(data, attr, default)

    with open(source, "wb") as fp:
        TOML_dump(fp)
    return values

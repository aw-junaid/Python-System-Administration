#!/usr/bin/env python3
"""
config_validation.py
--------------------
Enforce strong typing and constraints on runtime configuration/settings
using plain dataclasses -- no external dependency required (works as a
lightweight alternative to pydantic for simple cases).

Usage as a library:
    from config_validation import validated_config, Field

    @validated_config
    class AppConfig:
        host: str
        port: int = Field(default=8080, validator=lambda v: 1 <= v <= 65535)
        debug: bool = False

    cfg = AppConfig(host="0.0.0.0", port=9000)   # OK
    cfg = AppConfig(host="0.0.0.0", port=99999)  # raises ValueError

Run directly for a demo:
    python config_validation.py
"""

import dataclasses
import typing


class Field:
    """Marks a dataclass field with an optional default and validator."""

    def __init__(self, default=dataclasses.MISSING, validator=None):
        self.default = default
        self.validator = validator


def validated_config(cls):
    """
    Class decorator: turns a plain annotated class into a dataclass that
    validates, on construction:
      - every field's runtime type against its annotation
      - any `Field(validator=...)` constraint
    Raises TypeError for type mismatches and ValueError for failed
    validators, both with a clear message pointing at the offending
    field.
    """
    annotations = typing.get_type_hints(cls)
    validators = {}
    dataclass_fields = {}

    for name in annotations:
        raw_default = getattr(cls, name, dataclasses.MISSING)
        if isinstance(raw_default, Field):
            validators[name] = raw_default.validator
            dataclass_fields[name] = raw_default.default
        else:
            dataclass_fields[name] = raw_default

    for name, default in dataclass_fields.items():
        setattr(cls, name, default)

    # dataclasses.dataclass() only wires a call to __post_init__ into the
    # generated __init__ if __post_init__ already exists on the class AT
    # DECORATION TIME -- so this must be attached before dataclass(cls),
    # not after.
    original_post_init = getattr(cls, "__post_init__", None)

    def __post_init__(self):
        for name, expected_type in annotations.items():
            value = getattr(self, name)
            if not _type_matches(value, expected_type):
                raise TypeError(
                    f"{cls.__name__}.{name} expected {expected_type}, "
                    f"got {type(value).__name__} ({value!r})"
                )
            validator = validators.get(name)
            if validator is not None and not validator(value):
                raise ValueError(
                    f"{cls.__name__}.{name} failed validation: {value!r}"
                )
        if original_post_init:
            original_post_init(self)

    cls.__post_init__ = __post_init__
    dc = dataclasses.dataclass(cls)
    return dc


def _type_matches(value, expected_type):
    origin = typing.get_origin(expected_type)
    if origin is typing.Union:  # handles Optional[...]
        return any(_type_matches(value, t) for t in typing.get_args(expected_type))
    if origin is not None:
        return isinstance(value, origin)
    return isinstance(value, expected_type)


if __name__ == "__main__":
    @validated_config
    class AppConfig:
        host: str
        port: int = Field(default=8080, validator=lambda v: 1 <= v <= 65535)
        debug: bool = False

    print("Demo 1: valid configuration\n")
    cfg = AppConfig(host="0.0.0.0", port=9000, debug=True)
    print(" ->", cfg)

    print("\nDemo 2: wrong type for 'port'\n")
    try:
        AppConfig(host="0.0.0.0", port="not-a-number")
    except TypeError as e:
        print(" -> Caught expected TypeError:", e)

    print("\nDemo 3: 'port' fails its validator (out of range)\n")
    try:
        AppConfig(host="0.0.0.0", port=99999)
    except ValueError as e:
        print(" -> Caught expected ValueError:", e)

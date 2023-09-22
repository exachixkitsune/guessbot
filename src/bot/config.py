from __future__ import annotations

import dataclasses
import yaml


@dataclasses.dataclass(frozen=True)
class Config:
    default_channel: str = dataclasses.field(default="")
    prefix: str = dataclasses.field(default="!")
    live_mode: bool = dataclasses.field(default=False)
    use_latest_reply: bool = dataclasses.field(default=True)
    report_invalid: bool = dataclasses.field(default=False)

    def asdict(self) -> None:
        return dataclasses.asdict(self)


def load_config_from_file(filename: str) -> Config:
    with open(filename) as json_file:
        config_dict = yaml.load(json_file)

    return Config(**config_dict)

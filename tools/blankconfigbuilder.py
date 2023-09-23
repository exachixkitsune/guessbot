# Licence: BSD-3-Clause
# 2023 (C) exachixkitsune

from __future__ import annotations

from bot import config
import yaml

def create_blank_config(filename: str = 'config/config.yaml') -> None:
    blank_config = config.Config()
    
    with open(filename,'w', encoding="utf-8") as yaml_file:
        yaml.dump(blank_config.asdict(), yaml_file)
        
"""
Set of tests to check config class
"""

from __future__ import annotations

import dataclasses
import pytest
import yaml

from bot import config


class TestConfig:
    """
    Tests the config unit
    """

    @staticmethod
    def test_basic_config() -> None:
        """
        Tests config gets initiated
        """
        this_config = config.Config()

        assert this_config.default_channel == ""
        assert this_config.prefix == "!"
        assert this_config.live_mode is False
        assert this_config.use_latest_reply is True
        assert this_config.report_invalid is False
        assert this_config.stopguess_delay == 5
        assert this_config.closest_without_going_over is False

    @staticmethod
    def test_basic_config_asdict() -> None:
        """
        Tests config dict works
        """
        this_config = config.Config()
        assert this_config.asdict() == {
            "default_channel": "",
            "prefix": "!",
            "live_mode": False,
            "use_latest_reply": True,
            "report_invalid": False,
            "stopguess_delay": 5,
            "closest_without_going_over": False,
        }

    @staticmethod
    def test_files_to_overwrite() -> None:
        """
        Test it fails to overwrite
        """
        this_config = config.Config()

        with pytest.raises(dataclasses.FrozenInstanceError):
            this_config.default_channel = "exachixkitsune"

    @staticmethod
    def test_file_import(tmpdir) -> None:
        """
        Test that it reads in a file successfully
        """
        filename = tmpdir / "file.yaml"
        test_config_dict = {
            "default_channel": "a",
            "prefix": "?",
            "live_mode": True,
            "use_latest_reply": False,
            "report_invalid": True,
            "stopguess_delay": 10,
            "closest_without_going_over": True,
        }

        with open(filename, "w", encoding="utf-8") as yaml_file_dump:
            yaml.dump(test_config_dict, yaml_file_dump)

        read_config = config.load_config_from_file(filename)

        assert test_config_dict == read_config.asdict()

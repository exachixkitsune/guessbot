#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2021 Benedict Harcourt <ben.harcourt@harcourtprogramming.co.uk>
#
# SPDX-License-Identifier: BSD-2-Clause
# Modified from the above

from __future__ import annotations

import logging
import sys


Logger = logging.Logger


def init(filepath: str = None) -> None:
    logger = logging.getLogger("foxbot")

    if sys.stdout.isatty():
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(name)s:%(levelname)s] %(message)s", datefmt="%H:%M:%S"
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    else:
        handler = logging.FileHandler(filepath / "foxbot.log")
        handler.setFormatter(logging.Formatter("[%(name)s:%(levelname)s] %(message)s"))

        logger.addHandler(handler)
        logger.setLevel(logging.INFO)


def get_logger(name: str = "") -> logging.Logger:
    if not name:
        return logging.getLogger("foxbot")

    return logging.getLogger("foxbot." + name)

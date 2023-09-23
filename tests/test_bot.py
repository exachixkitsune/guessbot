"""
Set of tests to check the main bot functionality works
Assumes generally that without a token no connection will be made.
"""

from __future__ import annotations

import pytest

from bot import bot
from bot.config import Config
from bot import log


class TestBot:
    """
    Test Class
    """

    test_bot: bot.Bot

    def setup_bot(self, filepath) -> None:
        """
        Reinitialises the bot from scratch
        """
        log.init(filepath)

        test_config = Config({"default_channel": "", "prefix": "!"})

        self.test_bot = bot.Bot("", test_config, log.get_logger())

    @pytest.mark.asyncio
    async def test_event_ready(self, tmpdir) -> None:
        """
        Test that event_ready works
        """
        self.setup_bot(tmpdir)

        await self.test_bot.event_ready()

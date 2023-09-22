from __future__ import annotations

from twitchio.ext import Client, Message

from bot.config import Config
from bot import log
from bot.guess_handler import guess_handler

from enum import Enum
import re


class botState(Enum):
    NOT_PROCESSING = 0
    COLLECTING_VALS = 1
    HOLDING_FOR_ANSWER = 2


class Bot(Client):
    config: Config
    bot_state: botState
    regexp_pattern = re.compile(r"^(?P<value>[-+]?\d+\.?\d*)")
    guess_handler: guess_handler

    def __init__(
        self, token: str, channel: str, config: Config, logger: log.Logger
    ) -> None:
        super().__init__(token=token, prefix=config.prefix())

        self.config = config
        self.logger = logger
        self.bot_state = botState.NOT_PROCESSING

        self.guess_handler = guess_handler(self.config.use_latest_reply)

    async def event_ready(self) -> None:
        self.logger.info("Bot Awake. My name is %s", self.nick)
        self.loop.create_task(
            self.join(self.config.default_channel), name="join-channel"
        )

    async def join(self, channel: str) -> None:
        self.logger.info("Joining Channel %s", channel)
        await self.join_channels(channel)

    async def event_message(self, message: Message) -> None:
        # Ignore loop-back messages
        if message.echo:
            return

        if self.config.live_mode:
            print("Received %s::%s", message.author.name, message.content)

        if message.author.is_mod:
            # Check for mod commands
            content = message.content.lower()
            if content.startswith(self.config.prefix):
                if content.startswith(self.config.prefix + "startguessing"):
                    # Clear setup and start collection
                    return
                elif content.startswith(self.config.prefix + "stopguessing"):
                    # Summarise results
                    return
                elif content.startswith(self.config.prefix + "score"):
                    # give score
                    return
                elif content.startswith(self.config.prefix + "addguess "):
                    # hard-adds a guess
                    return
                elif content.startswith(self.config.prefix + "stats"):
                    # gives stat information
                    return

        # Only do full message check if in recording mode
        if self.bot_state == botState.COLLECTING_VALS:
            if self.is_guess(message.content):
                await self.record_guess(message.author.name, message.content)
            elif message.content.lower().startswith(self.config.prefix + "guess "):
                await self.record_guess(
                    message.author.namem,
                    message.content[len(self.config.prefix + "guess ") :],
                )

    def is_guess(self, message: str) -> bool:
        # Is this a number?
        return self.regexp_pattern.search(message) is not None

    async def record_guess(self, name: str, message: str):
        self.guess_handler.accept_guess(name, message)

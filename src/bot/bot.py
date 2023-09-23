from __future__ import annotations

import twitchio
from twitchio import Message, Chatter
from twitchio.ext import commands

from bot.config import Config
from bot import log
from bot.guess_handler import guess_handler

import asyncio
from enum import Enum
import re


class botState(Enum):
    NOT_PROCESSING = 0
    COLLECTING_VALS = 1
    HOLDING_FOR_ANSWER = 2


class Bot(commands.Bot):
    config: Config
    bot_state: botState
    regexp_pattern = re.compile(r"^(?P<value>[-+]?\d+\.?\d*)")
    guess_handler: guess_handler

    def __init__(self, token: str, config: Config, logger: log.Logger) -> None:
        super().__init__(token=token, prefix=config.prefix)

        self.config = config
        self.logger = logger
        self.bot_state = botState.NOT_PROCESSING
        self.reset_guesses()

    async def event_ready(self) -> None:
        self.logger.info("Bot Awake. My name is %s", self.nick)
        self.loop.create_task(
            self.join(self.config.default_channel), name="join-channel"
        )

    async def join(self, channel: str) -> None:
        self.logger.info("Joining Channel %s", channel)
        await self.join_channels([channel])

    async def event_message(self, message: Message) -> None:
        # Ignore loop-back messages
        if message.echo:
            return

        if self.config.live_mode:
            print(f"Received {message.author.name}::{message.content}")

        # Only do full message check if in recording mode
        if self.bot_state == botState.COLLECTING_VALS:
            if self.is_guess(message.content):
                await self.record_guess(message.author.name, message.content)
                return
            elif message.content.lower().startswith(self.config.prefix + "guess "):
                await self.record_guess(
                    message.author.name,
                    message.content[len(self.config.prefix + "guess ") :],
                )
                return

        # Commmands are only availible to mods:
        if self.is_elevated_permissions(message.author):
            await self.handle_commands(message)

    def is_guess(self, message: str) -> bool:
        # Is this a number?
        return self.regexp_pattern.search(message) is not None

    def reset_guesses(self) -> None:
        self.guess_handler = guess_handler(self.config.use_latest_reply)

    async def send_error_message(
        self, message: str, ping_name: str = None, context: commands.Context = None
    ):
        """
        Return an error message, either as a reply to the context, or to whoever is asked to be pinged.
        """
        if context is None:
            message = f"@{ping_name} " + message
            self.logger.info(f"sending message::{message}")
            target = self.get_channel(self.config.default_channel)
            await target.send(message)
        else:
            self.logger.info(f"sending reply::{message}")
            await context.reply(message)

    async def record_guess(
        self,
        name: str,
        message: str,
        ping_name: str = None,
        context: commands.Context = None,
    ) -> None:
        """
        Check the value from "message" is a positive integer; report back if not.
        Two checks: Integer, and Positive
        Then hand over to guess handler.
        """
        if ping_name is None:
            ping_name = name

        try:
            value_int = int(self.regexp_pattern.match(message)[0])
        except ValueError:
            self.logger.info(
                f"Input message returned ValueError -  ({name}:{message}) - not an integer"
            )
            await self.send_error_reply(
                "Positive whole numbers only please", ping_name, context
            )
            return None
        except Exception:
            self.logger.error(
                f"Alternative error when handling message in record_guess ({name}:{message})"
            )
            return None

        if value_int < 0:
            self.logger.info("value_int error ({value}")
            self.logger.error(
                "Converting value to Input message is negative ({name}:{message})"
            )
            await self.send_error_message(
                "Positive whole numbers only please", ping_name, context
            )
            return None

        # Feed to guess handler
        self.logger.info(f"Recording guess {value_int} from {name}")
        self.guess_handler.accept_guess(name, value_int)
        return None

    def is_elevated_permissions(self, author: Chatter) -> bool:
        return author.is_mod or author.is_broadcaster

    # Commands
    @commands.command()
    async def startguessing(self, ctx: commands.Context) -> None:
        if not self.is_elevated_permissions(ctx.author):
            return

        if self.bot_state == botState.NOT_PROCESSING:
            self.logger.info(
                "Received startguessing commands, conditions met so clearing guesses and opening."
            )
            self.reset_guesses()
            self.bot_state = botState.COLLECTING_VALS
            await ctx.send("Give guesses now! Positive integers only")
        else:
            self.logger.warning("Tried to start guessing, but not in the correct state")

    @commands.command()
    async def stopguessing(self, ctx: commands.Context) -> None:
        if not self.is_elevated_permissions(ctx.author):
            return

        if self.bot_state == botState.COLLECTING_VALS:
            self.logger.info(
                f"Asked to stop guessing. Going to delay by {self.config.stopguess_delay} seconds"
            )
            await ctx.send("Guessing window closed")
            await asyncio.sleep(self.config.stopguess_delay)
            self.logger.info(f"Guessing window closed")
            self.bot_state = botState.HOLDING_FOR_ANSWER
            stats = self.guess_handler.stats()
            await ctx.send(
                f"Collected {stats['count']}, between {stats['min']} and {stats['max']}"
            )
        else:
            self.logger.warning("Tried to stop guessing, but not in the correct state")

    @commands.command()
    async def score(self, ctx: commands.Context, scoreval: int) -> None:
        if not self.is_elevated_permissions(ctx.author):
            return

        if self.bot_state == botState.COLLECTING_VALS:
            self.logger.warning("Asked to make score, but still collecting.")
            await ctx.reply("Please call !stopguessing before asking for a score")
        else:
            # Produce score in either case
            (result_names, result_values) = self.guess_handler.get_score(
                scoreval, self.config.closest_without_going_over
            )

            message = (
                "Winners: "
                + ", ".join(result_names)
                + ". Guesses of: "
                + str(result_values)[1:-1]
            )
            self.logger.info(f"Sending message::{message}")
            await ctx.send(message)

    @commands.command()
    async def addguess(
        self,
        ctx: commands.Context,
        guessval: str,
        user: str | None,
    ) -> None:
        """
        command to add the guess to the list; doesn't have the normal protections as seen in event_message
        """
        if not self.is_elevated_permissions(ctx.author):
            return

        if not self.is_guess(guessval):
            self.logger.info(f"addguess command: guessval ({guessval}) not a guess")
            await ctx.reply(f"addguess command didn't have a guess value")
            return

        self.logger.info(f"addguess command, with {guessval} and {user}")

        if isinstance(user, (twitchio.Chatter, twitchio.PartialChatter)):
            user = user.name
        if user is None:
            user = ctx.author.name

        await self.record_guess(user, guessval, ctx.author.name, ctx)

    @commands.command()
    async def stats(self, ctx: commands.Context) -> None:
        if not self.is_elevated_permissions(ctx.author):
            return

        stats = self.guess_handler.stats()
        message = f"{stats['count']} results between {stats['min']}-{stats['max']}. Mean:{stats['mean']}, StDev:{stats['stdev']}. Median:{stats['median']}"

        self.logger.info(f"Stats Message:{message}")
        await ctx.send(message)

    @commands.command()
    async def guesscommands(self, ctx: commands.Context) -> None:
        if not self.is_elevated_permissions(ctx.author):
            await ctx.reply("My commands are moderator-only")
            return

        prefix = self.config.prefix
        await ctx.reply(
            "{prefix}startguessing, {prefix}stopguessing, {prefix}score (result), {prefix}stats. {prefix}addguess (guess) (name)."
        )

    @commands.command()
    async def verify(self, ctx: commands.Context) -> None:
        if not self.is_elevated_permissions(ctx.author):
            return

        message = f"Hello {ctx.author.name}, I am totally awake"
        self.logger.info(f"Sending message::{message}")
        await ctx.send(message)

    @commands.command()
    async def sleep(self, ctx: commands.Context) -> None:
        if not self.is_elevated_permissions(ctx.author):
            return

        self.logger.info("Received sleep command")
        await self.close()

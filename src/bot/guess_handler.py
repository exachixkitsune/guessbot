from __future__ import annotations

from typing import Dict

import statistics


class guess_handler:
    use_latest_reply: bool
    guesses: Dict

    def __init__(self, use_latest_reply: bool = True):
        self.use_latest_reply = use_latest_reply
        self.guesses = {}

    def accept_guess(self, name: str, value: int) -> None:
        if self.use_latest_reply:
            self.guesses[name] = value
        else:
            if name not in self.guesses.keys():
                self.guesses[name] = value

    def stats(self) -> Dict:
        raw_values = list(self.guesses.values())

        return {
            "min": min(raw_values),
            "max": max(raw_values),
            "mean": statistics.mean(raw_values),
            "stdev": statistics.stdev(raw_values),
            "median": statistics.median(raw_values),
            "multimode": statistics.multimode(raw_values),
            "quartiles": statistics.quantiles(raw_values, n=4),
        }

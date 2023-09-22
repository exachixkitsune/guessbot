from __future__ import annotations

from bot.guess_handler import guess_handler

# pragma pylint: disable=R0903
#  Disable "too few public methods" for test cases - most test files will be classes used for
#  grouping and then individual tests alongside these


class TestGuessHandler:
    @staticmethod
    def test_guess_handler_initially() -> None:
        """
        Specifically test is the card is blank on initiation
        """
        this_guess_handler = guess_handler()

        assert this_guess_handler.use_latest_reply is True
        assert not this_guess_handler.guesses

    @staticmethod
    def test_guess_handler_initially_v2() -> None:
        """
        Specifically test is the card is blank on initiation
        """
        this_guess_handler = guess_handler(False)

        assert this_guess_handler.use_latest_reply is False
        assert not this_guess_handler.guesses

    @staticmethod
    def test_guess_handler_add1() -> None:
        """
        Test adding things works
        """
        this_guess_handler = guess_handler()

        this_guess_handler.accept_guess("a", 1)
        assert this_guess_handler.guesses == {"a": 1}

        this_guess_handler.accept_guess("b", 2)
        assert this_guess_handler.guesses == {"a": 1, "b": 2}

    @staticmethod
    def test_guess_handler_replace_uselatest() -> None:
        """
        Test if accepting a guess replaces
        """
        this_guess_handler = guess_handler(True)

        this_guess_handler.accept_guess("a", 1)
        this_guess_handler.accept_guess("b", 2)
        this_guess_handler.accept_guess("c", 3)

        assert this_guess_handler.guesses == {"a": 1, "b": 2, "c": 3}

        this_guess_handler.accept_guess("a", 3)

        assert this_guess_handler.guesses == {"a": 3, "b": 2, "c": 3}

    @staticmethod
    def test_guess_handler_replace_notuselatest() -> None:
        """
        Test if accepting a guess does not replace
        """
        this_guess_handler = guess_handler(False)

        this_guess_handler.accept_guess("a", 1)
        this_guess_handler.accept_guess("b", 2)
        this_guess_handler.accept_guess("c", 3)
        
        assert this_guess_handler.guesses == {"a": 1, "b": 2, "c": 3}

        this_guess_handler.accept_guess("a", 3)

        assert this_guess_handler.guesses == {"a": 1, "b": 2, "c": 3}

    @staticmethod
    def test_guess_handler_stats() -> None:
        """
        Test if accepting a guess does not replace
        """
        this_guess_handler = guess_handler(True)

        contents = {"a": 1, "b": 2, "c": 3, "d":4, "e":5, "f":6, "g":7, "g2":7, "g3":7, "h":8}
        for i_key in contents.keys():
            this_guess_handler.accept_guess(i_key, contents[i_key])
        
        assert this_guess_handler.guesses == contents
        
        stats = this_guess_handler.stats()
        assert stats['min'] == 1
        assert stats['max'] == 8
        assert stats['mean'] == 5
        assert (stats['stdev'] - 2.4037) < 0.0001
        assert stats['median'] == 5.5
        assert stats['multimode'] == [7]
        assert stats['quartiles'] == [2.75, 5.5, 7.0]
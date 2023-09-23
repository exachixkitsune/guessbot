import yaml

from bot import bot, config, log


def load_token(tokenfile: str) -> str:
    with open(tokenfile, "r") as yaml_file:
        token_dict = yaml.safe_load(yaml_file)

    return token_dict["token"]


def runbot(
    tokenfile: str = "config/token.yaml", configfile: str = "config/config.yaml"
):
    bot_config = config.load_config_from_file(configfile)
    token = load_token(tokenfile)

    log.init()

    this_bot = bot.Bot(token, bot_config, log.get_logger())

    this_bot.run()


if __name__ == "__main__":
    runbot()

from dotenv import load_dotenv


def configure():
    load_dotenv()


def main():
    configure()
    from utils.tgbot.tg_bot import run
    run()


if __name__ == '__main__':
    main()

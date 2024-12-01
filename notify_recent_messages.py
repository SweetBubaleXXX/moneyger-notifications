from app.application import create_container


def main():
    container = create_container()
    container.email_service().notify_recent_messages(container.message_storage())


if __name__ == "__main__":
    main()

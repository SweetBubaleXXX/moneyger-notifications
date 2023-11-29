from smtplib import SMTP, SMTP_SSL
from urllib.parse import urlparse


def create_smtp_connection(
    url: str,
    username: str | None = None,
    password: str | None = None,
    starttls: bool = False,
    ssl_tls: bool = False,
) -> SMTP:
    parsed_url = urlparse(url)
    connection_params = {
        "host": parsed_url.hostname,
        "port": parsed_url.port,
    }
    if ssl_tls:
        connection = SMTP_SSL(**connection_params)
    else:
        connection = SMTP(**connection_params)
        if starttls:
            connection.starttls()
    if username and password:
        connection.login(username, password)
    return connection

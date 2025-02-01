import urllib.parse

import locale

locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")


def create_email_link(email_address, subject="", body=""):
    """
    Create a properly encoded mailto link for an email address with an optional subject and body.

    Args:
        email_address (str): The recipient email address.
        subject (str): The subject of the email (optional).
        body (str): The body content of the email (optional).

    Returns:
        str: A correctly formatted mailto link for embedding in a webpage.
    """
    # Base mailto link
    mailto_link = f"mailto:{urllib.parse.quote(email_address)}"

    # Create query parameters
    params = []
    if subject:
        params.append(f"subject={urllib.parse.quote(subject)}")
    if body:
        params.append(f"body={urllib.parse.quote(body)}")

    # Append parameters if available
    if params:
        mailto_link += "?" + "&".join(params)

    return mailto_link

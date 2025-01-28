import urllib.parse


def create_email_link(email_address, subject="", body=""):
    """
    Create a mailto link for an email address with optional subject and body.

    Args:
        email_address (str): The email address to send to.
        subject (str): The subject of the email (optional).
        body (str): The body content of the email (optional).

    Returns:
        str: A mailto link that can be used in a web page.
    """
    # Base mailto link
    mailto_link = f"mailto:{urllib.parse.quote(email_address)}"

    # Add subject and body if provided
    params = {}
    if subject:
        params["subject"] = subject
    if body:
        params["body"] = body

    # Encode parameters and append to the mailto link
    if params:
        query_string = urllib.parse.urlencode(params)
        mailto_link += f"?{query_string}"

    return mailto_link

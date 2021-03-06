import logging
from slacker import Slacker
from settings import SLACK_TOKEN, BASE_URL
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def safe_post_to_slack(channel, message):
    try:
        _post_to_slack(channel, message)
    except Exception as e:
        logger.error('Slack error: {}: Original message in channel ({}) - {}'.format(e, channel, message))


def _post_to_slack(channel, message):
    if not SLACK_TOKEN:
        logger.info(message)
        return None

    slack = Slacker(SLACK_TOKEN)
    response = slack.chat.post_message(
        channel, message, as_user=False, icon_emoji=":beaker:", username="Beaker (engineering-minion)",
    )
    return response.raw


def send_welcome_email(user, referrer):
    email_content = """
    Hi there {full_name}--

    {referrer} has added you as a collaborator in seqr.

    Please click this link to set up your account:
    {base_url}users/set_password/{password_token}

    Thanks!
    """.format(
        full_name=user.get_full_name(),
        referrer=referrer.get_full_name() or referrer.email,
        base_url=BASE_URL,
        password_token=user.password,
    )
    user.email_user('Set up your seqr account', email_content, fail_silently=False)


def send_html_email(email_body, **kwargs):
    email_message = EmailMultiAlternatives(
        body=strip_tags(email_body),
        **kwargs,
    )
    email_message.attach_alternative(email_body, 'text/html')
    email_message.send()

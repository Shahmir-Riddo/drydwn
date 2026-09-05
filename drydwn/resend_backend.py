"""
Custom Django email backend that sends mail via the Resend Python SDK.

Usage
-----
In settings.py:

    EMAIL_BACKEND = 'drydwn.resend_backend.ResendEmailBackend'

Requires the ``RESEND_API_KEY`` environment variable to be set and the
``resend`` package to be installed (``pip install resend``).
"""

import os
import logging

from django.core.mail.backends.base import BaseEmailBackend

import resend
from resend.exceptions import ResendError

logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    """
    A Django email backend that delivers messages through the Resend SDK
    instead of SMTP.

    Supports:
    - Plain-text and HTML bodies (including multipart/alternative)
    - Multiple recipients, CC, BCC, reply-to
    - File attachments (in-memory content via Django's EmailMessage API)
    - Custom headers
    - Proper error handling per Resend SDK conventions
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)

        api_key = os.environ.get('RESEND_API_KEY')
        if not api_key:
            msg = (
                "RESEND_API_KEY environment variable is not set. "
                "Please set it before using the Resend email backend."
            )
            if not self.fail_silently:
                raise ValueError(msg)
            logger.error(msg)

        resend.api_key = api_key

    # ------------------------------------------------------------------
    # Public interface required by Django
    # ------------------------------------------------------------------

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of
        messages sent successfully.
        """
        if not email_messages:
            return 0

        sent_count = 0
        for message in email_messages:
            try:
                if self._send(message):
                    sent_count += 1
            except Exception as exc:
                if not self.fail_silently:
                    raise
                logger.exception("Failed to send email via Resend: %s", exc)

        return sent_count

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _send(self, message):
        """Convert a Django EmailMessage to Resend params and send it."""
        if not message.recipients():
            return False

        params = self._build_params(message)

        try:
            response = resend.Emails.send(params)
            logger.debug("Resend email sent successfully: %s", response)
            return True
        except ResendError:
            if not self.fail_silently:
                raise
            logger.exception("Resend API error while sending email")
            return False

    def _build_params(self, message):
        """
        Map a Django ``EmailMessage`` (or ``EmailMultiAlternatives``)
        to a ``resend.Emails.SendParams`` dict.
        """
        params = {
            'from': message.from_email,
            'to': list(message.to),
            'subject': message.subject,
        }

        # ---- Body ---------------------------------------------------
        # Django's EmailMultiAlternatives stores the plain-text body in
        # ``message.body`` and HTML alternatives in ``message.alternatives``.
        html_body = None
        if hasattr(message, 'alternatives'):
            for content, mimetype in message.alternatives:
                if mimetype == 'text/html':
                    html_body = content
                    break

        if html_body:
            params['html'] = html_body
            # Also include plain-text fallback when available
            if message.body:
                params['text'] = message.body
        elif message.content_subtype == 'html':
            # Caller set ``content_subtype = 'html'`` on a plain EmailMessage
            params['html'] = message.body
        else:
            params['text'] = message.body

        # ---- Optional recipient lists --------------------------------
        if message.cc:
            params['cc'] = list(message.cc)
        if message.bcc:
            params['bcc'] = list(message.bcc)
        if message.reply_to:
            params['reply_to'] = list(message.reply_to)

        # ---- Custom headers ------------------------------------------
        if message.extra_headers:
            params['headers'] = message.extra_headers

        # ---- Attachments ---------------------------------------------
        attachments = self._build_attachments(message)
        if attachments:
            params['attachments'] = attachments

        return params

    @staticmethod
    def _build_attachments(message):
        """
        Convert Django attachment tuples ``(filename, content, mimetype)``
        into the Resend SDK format.
        """
        if not message.attachments:
            return []

        resend_attachments = []
        for attachment in message.attachments:
            if isinstance(attachment, tuple) and len(attachment) >= 2:
                filename, content = attachment[0], attachment[1]
                # Django stores attachment content as bytes or str
                if isinstance(content, str):
                    content = content.encode('utf-8')
                resend_attachments.append({
                    'filename': filename or 'attachment',
                    'content': list(content),
                })

        return resend_attachments

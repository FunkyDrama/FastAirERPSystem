import json

import qrcode
import aiosmtplib
import asyncio
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from notifications_service.app.core.config import email_settings
from notifications_service.app.worker import celery_app

env = Environment(loader=FileSystemLoader("notifications_service/app/templates"))


@celery_app.task(name="users.send_email")
def send_booking_email(to_email: str, booking_id: str, ticket_number: str, passenger_name: str):
    """
    Send an email with booking details, including a QR code representing the ticket.

    This function sends a booking confirmation email to the specified email address.
    The email includes the booking ID, ticket number, and a QR code as an attachment
    for quick access to the booking. To customize the email content, a predefined
    HTML template is rendered with the booking details. The QR code is generated in
    PNG format and embedded into the email.

    The mail service connects securely using SMTP credentials from the application's
    email settings.

    :param to_email: Recipient's email address where the booking confirmation will
        be sent.
    :type to_email: str
    :param booking_id: Unique identifier for the booking associated with the ticket.
    :type booking_id: str
    :param ticket_number: Unique identifier for the ticket issued.
    :type ticket_number: str
    :param passenger_name: Full name of the passenger for whom the ticket is issued.
    :type passenger_name: str
    :return: None
    :rtype: None
    """

    async def _send():
        qr_data = {
            "booking_id": booking_id,
            "ticket_number": ticket_number,
            "passenger_name": passenger_name,
        }
        qr = qrcode.make(json.dumps(qr_data))
        buf = BytesIO()
        qr.save(buf, format="PNG")
        qr_bytes = buf.getvalue()

        template = env.get_template("booking_email.html.j2")
        html = template.render(
            booking_id=booking_id,
            ticket_number=ticket_number,
            passenger_name=passenger_name,
        )

        msg = MIMEMultipart("related")
        msg["Subject"] = f"Your FastAir Ticket – {passenger_name}"
        msg["From"] = email_settings.EMAIL_FROM
        msg["To"] = to_email

        alt = MIMEMultipart("alternative")
        alt.attach(MIMEText(html, "html"))
        msg.attach(alt)

        img = MIMEImage(qr_bytes, _subtype="png")
        img.add_header("Content-ID", "<qrcode>")
        img.add_header("Content-Disposition", "inline", filename="qrcode.png")
        msg.attach(img)

        smtp = aiosmtplib.SMTP(
            hostname=email_settings.EMAIL_HOST,
            port=email_settings.EMAIL_PORT,
        )
        await smtp.connect()
        await smtp.login(
            email_settings.EMAIL_HOST_USER, email_settings.EMAIL_HOST_PASSWORD
        )
        await smtp.send_message(msg)
        await smtp.quit()

    asyncio.run(_send())

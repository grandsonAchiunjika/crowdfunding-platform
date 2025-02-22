import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class PayChanguService:
    """Handles interactions with PayChangu API."""

    @staticmethod
    def initiate_payment(amount, currency, phone_number, email, callback_url):
        """Initiate a mobile money payment using Mpamba or Airtel Money."""
        url = f"{settings.PAYCHANGU_BASE_URL}/v1/payments"
        payload = {
            "amount": amount,
            "currency": currency,
            "phone_number": phone_number,
            "email": email,
            "callback_url": callback_url
        }
        headers = {
            "Authorization": f"Bearer {settings.PAYCHANGU_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)

            # Check if the response was successful
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"PayChangu API error: {response.status_code} - {response.text}")
                return {"error": f"Payment initiation failed with status code {response.status_code}"}

        except requests.exceptions.RequestException as e:
            # Catch any HTTP request errors
            logger.error(f"Error making request to PayChangu API: {str(e)}")
            return {"error": "Error connecting to the payment service. Please try again later."}

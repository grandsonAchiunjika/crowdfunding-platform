import stripe
from django.conf import settings
from .models import Transaction, Donation

# Set up Stripe with the secret key
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_payment(donation_id, token):
    """
    Process a Stripe payment for a donation.
    :param donation_id: The ID of the donation being paid for.
    :param token: The Stripe payment token received from the frontend.
    :return: A dictionary with transaction details.
    """
    try:
        donation = Donation.objects.get(id=donation_id)
        amount_in_cents = int(donation.amount * 100)  # Stripe uses cents

        # Create a Stripe charge
        charge = stripe.Charge.create(
            amount=amount_in_cents,
            currency="usd",
            source=token,
            description=f"Donation for campaign: {donation.campaign.title}",
        )

        # Create a transaction record in the database
        transaction = Transaction.objects.create(
            user=donation.user,
            donation=donation,
            amount=donation.amount,
            transaction_type="donation",
            status="completed",
        )

        # Update the campaign's raised amount
        campaign = donation.campaign
        campaign.raised_amount += donation.amount
        campaign.save()

        return {"success": True, "transaction_id": transaction.id}

    except stripe.error.CardError as e:
        return {"success": False, "error": str(e)}

    except Exception as e:
        return {"success": False, "error": f"An error occurred: {str(e)}"}

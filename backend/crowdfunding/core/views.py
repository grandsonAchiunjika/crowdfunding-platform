import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction as db_transaction
from django.db.models import Q, Sum
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Campaign, Donation, Comment, Transaction
from .serializers import CampaignSerializer, DonationSerializer, CommentSerializer, TransactionSerializer
from .payments import create_stripe_payment
from django.shortcuts import get_object_or_404

# Set up Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY  # Make sure you have this in your settings

# -------------------------
# Campaign ViewSet
# -------------------------
class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'], url_path=r'user/(?P<user_id>\d+)')
    def user_campaigns(self, request, user_id=None):
        """Returns all campaigns created by a specific user."""
        campaigns = self.queryset.filter(creator_id=user_id)
        serializer = self.get_serializer(campaigns, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='search')
    def search_campaigns(self, request):
        """Allows users to search for campaigns by title or description."""
        query = request.query_params.get('q', '')
        campaigns = self.queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
        serializer = self.get_serializer(campaigns, many=True)
        return Response(serializer.data)

    # -------------------------
    # Stripe Checkout Session Creation
    # -------------------------
    @action(detail=True, methods=['post'], url_path='create-checkout-session')
    def create_checkout_session(self, request, pk=None):
        """
        Create a Stripe Checkout session for a campaign donation.
        """
        campaign = get_object_or_404(Campaign, pk=pk)

        try:
            success_url = request.data.get('success_url', request.build_absolute_uri('/success/'))
            cancel_url = request.data.get('cancel_url', request.build_absolute_uri('/cancel/'))

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': campaign.title,
                                'description': campaign.description,
                            },
                            'unit_amount': int(campaign.donation_amount * 100),  # Stripe requires the amount in cents
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
            )

            return JsonResponse({
                'id': checkout_session.id
            })

        except stripe.error.StripeError as e:
            return JsonResponse({'error': f"Stripe error: {e.error.message}"}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# -------------------------
# Donation ViewSet
# -------------------------
class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Handles donation creation and updates campaign funds."""
        with db_transaction.atomic():
            donation = serializer.save()
            campaign = donation.campaign

            if not campaign.is_active:
                raise ValueError("This campaign is no longer active.")

            # Update campaign raised amount
            campaign.raised_amount += donation.amount
            campaign.save()

            # Create a transaction record
            Transaction.objects.create(
                user=donation.user,
                donation=donation,
                amount=donation.amount,
                transaction_type="donation",
                status="completed"
            )

    @action(detail=False, methods=['get'], url_path='recent')
    def recent_donations(self, request):
        """Returns the 5 most recent donations by the authenticated user."""
        donations = self.get_queryset().order_by('-created_at')[:5]
        serializer = self.get_serializer(donations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path=r'summary/(?P<campaign_id>\d+)')
    def donation_summary(self, request, campaign_id=None):
        """Returns total donation amount for a given campaign."""
        total_donations = self.queryset.filter(campaign_id=campaign_id).aggregate(Sum('amount'))
        total_amount = total_donations.get('amount__sum', 0) or 0
        return Response({'campaign_id': campaign_id, 'total_donated': total_amount})

# -------------------------
# Comment ViewSet
# -------------------------
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Filters comments by campaign if campaign_id is provided."""
        queryset = super().get_queryset()
        campaign_id = self.request.query_params.get('campaign_id')
        return queryset.filter(campaign_id=campaign_id) if campaign_id else queryset

# -------------------------
# Transaction ViewSet
# -------------------------
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ['created_at', 'amount']

    def get_queryset(self):
        """Limits transactions to the authenticated user."""
        queryset = Transaction.objects.filter(user=self.request.user)

        # Optional filters by date
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset

    @action(detail=False, methods=['get'], url_path='recent')
    def recent_transactions(self, request):
        """Returns the 5 most recent transactions of the authenticated user."""
        transactions = self.get_queryset().order_by('-created_at')[:5]
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='summary')
    def transaction_summary(self, request):
        """Returns a summary of the authenticated user's transactions."""
        total_transactions = self.get_queryset().aggregate(Sum('amount'))
        total_amount = total_transactions.get('amount__sum', 0) or 0
        return Response({'total_transactions': total_amount})

# -------------------------
# Stripe Payment ViewSet
# -------------------------
class PaymentViewSet(viewsets.ViewSet):
    """
    Handles Stripe payments for donations.
    """

    @action(detail=False, methods=["post"])
    def process_payment(self, request):
        """
        API endpoint to process a Stripe donation payment.
        Expected data: {"donation_id": 1, "token": "stripe_token"}
        """
        donation_id = request.data.get("donation_id")
        token = request.data.get("token")

        if not donation_id or not token:
            return Response({"error": "Missing donation ID or token"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment_response = create_stripe_payment(donation_id, token)

            if payment_response.get("success"):
                return Response({"message": "Payment successful", "transaction_id": payment_response.get("transaction_id")}, status=status.HTTP_200_OK)

            return Response({"error": payment_response.get("error")}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"Payment processing failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

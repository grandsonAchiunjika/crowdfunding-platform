from rest_framework import viewsets, permissions
from django.db.models import Q, Sum
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Campaign, Donation, Comment, Transaction
from .serializers import CampaignSerializer, DonationSerializer, CommentSerializer, TransactionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from django.db import transaction as db_transaction
from .payments import create_stripe_payment


# Campaign ViewSet
class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Custom endpoint for user-specific campaigns
    @action(detail=False, methods=['get'], url_path=r'user/(?P<user_id>\d+)')
    def user_campaigns(self, request, user_id=None):
        """Returns all campaigns created by a specific user"""
        campaigns = self.queryset.filter(creator_id=user_id)
        serializer = self.get_serializer(campaigns, many=True)
        return Response(serializer.data)

    # Custom endpoint for searching campaigns
    @action(detail=False, methods=['get'], url_path='search')
    def search_campaigns(self, request):
        """Allows users to search for campaigns by title or description"""
        query = request.query_params.get('q', '')
        campaigns = self.queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
        serializer = self.get_serializer(campaigns, many=True)
        return Response(serializer.data)


# Donation ViewSet
class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        with db_transaction.atomic():  # Ensures atomicity
            donation = serializer.save()

            # ✅ Update Campaign's raised amount
            campaign = donation.campaign
            campaign.raised_amount += donation.amount
            campaign.save()

            # ✅ Create a transaction for this donation
            transaction = Transaction.objects.create(
                user=donation.user,
                donation=donation,
                amount=donation.amount,
                transaction_type="donation",
                status="completed"
            )
    # Custom endpoint for recent donations
    @action(detail=False, methods=['get'], url_path='recent')
    def recent_donations(self, request):
        """Returns the 5 most recent donations by the authenticated user"""
        donations = self.get_queryset().order_by('-created_at')[:5]
        serializer = self.get_serializer(donations, many=True)
        return Response(serializer.data)

    # Custom endpoint for donation summary per campaign
    @action(detail=False, methods=['get'], url_path=r'summary/(?P<campaign_id>\d+)')
    def donation_summary(self, request, campaign_id=None):
        """Returns total donation amount for a given campaign"""
        total_donations = self.queryset.filter(campaign_id=campaign_id).aggregate(Sum('amount'))
        total_amount = total_donations.get('amount__sum', 0) or 0
        return Response({'campaign_id': campaign_id, 'total_donated': total_amount})


# Comment ViewSet
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Optional: Filter comments by campaign for authenticated users
    def get_queryset(self):
        """Only show comments related to the campaign being viewed."""
        queryset = super().get_queryset()
        campaign_id = self.request.query_params.get('campaign_id', None)
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        return queryset


# Transaction ViewSet
class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Limit transactions to the current authenticated user."""
        return self.queryset.filter(user=self.request.user)

    # Custom endpoint for recent transactions
    @action(detail=False, methods=['get'], url_path='recent')
    def recent_transactions(self, request):
        """Returns the 5 most recent transactions by the authenticated user"""
        transactions = self.get_queryset().order_by('-created_at')[:5]
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

    # Custom endpoint for transaction summary per user
    @action(detail=False, methods=['get'], url_path='summary')
    def transaction_summary(self, request):
        """Returns a summary of all transactions for the authenticated user"""
        total_transactions = self.queryset.aggregate(Sum('amount'))
        total_amount = total_transactions.get('amount__sum', 0) or 0
        return Response({'total_transactions': total_amount})


# Payment ViewSet
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

        payment_response = create_stripe_payment(donation_id, token)

        if payment_response["success"]:
            return Response({"message": "Payment successful", "transaction_id": payment_response["transaction_id"]}, status=status.HTTP_200_OK)
        else:
            return Response({"error": payment_response["error"]}, status=status.HTTP_400_BAD_REQUEST)

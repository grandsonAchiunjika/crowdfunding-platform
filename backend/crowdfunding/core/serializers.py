from rest_framework import serializers
from django.db import transaction
from .models import Campaign, Donation, Comment, Transaction

# Serializer for Campaigns
class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'


# Serializer for Donations
class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = '__all__'
    
    def create(self, validated_data):
        with transaction.atomic():  # Ensure data integrity
            donation = super().create(validated_data)
            campaign = donation.campaign
            campaign.raised_amount += donation.amount  # Correct field update
            campaign.save()
        return donation

# Serializer for Comments
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


# Serializer for Transactions
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

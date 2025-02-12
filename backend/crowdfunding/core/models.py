from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# Custom User Model
class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.username


# Campaign Model
class Campaign(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="campaigns")
    created_at = models.DateTimeField(auto_now_add=True)

    def update_raised_amount(self):
        """Recalculate and update the total amount raised."""
        total_donations = self.donations.aggregate(models.Sum('amount'))['amount__sum'] or 0.00
        self.raised_amount = total_donations
        self.save()

    def __str__(self):
        return self.title


# Donation Model
class Donation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="donations")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="donations")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'campaign')  # Ensure each user can donate only once per campaign

    def __str__(self):
        return f"{self.user.username} donated {self.amount} to {self.campaign.title}"


# Transaction Model
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("donation", "Donation"),
        ("withdrawal", "Withdrawal"),
    ]
    TRANSACTION_STATUS = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name="transactions", null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES, default="donation")
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} of {self.amount} - {self.status}"


# Comment Model
class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} commented on {self.campaign.title}"


# SIGNAL: Update Campaign Raised Amount & Create Transaction when Donation is made
@receiver(post_save, sender=Donation)
def update_campaign_on_donation(sender, instance, created, **kwargs):
    if created:
        # Update campaign raised amount
        instance.campaign.update_raised_amount()

        # Create a new transaction for this donation
        Transaction.objects.create(
            user=instance.user,
            donation=instance,
            amount=instance.amount,
            transaction_type="donation",
            status="completed"
        )

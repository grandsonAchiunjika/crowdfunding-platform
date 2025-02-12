from django.contrib import admin
from .models import CustomUser, Campaign, Donation, Transaction, Comment


admin.site.register(CustomUser)
admin.site.register(Campaign)
admin.site.register(Donation)
admin.site.register(Transaction)
admin.site.register(Comment)

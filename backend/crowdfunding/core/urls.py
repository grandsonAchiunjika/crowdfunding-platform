from django.urls import path, include  
from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, DonationViewSet, CommentViewSet, TransactionViewSet, PaymentViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings

# Initialize the router
router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet, basename='campaign')  
router.register(r'donations', DonationViewSet, basename='donation')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'payments', PaymentViewSet, basename='payment')


# PayPal-specific URL for processing payments
urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    *router.urls,  # Include all registered viewsets
]
if settings.DEBUG:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]

from django.urls import path, include  # Make sure to import include
from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, DonationViewSet, CommentViewSet, TransactionViewSet, PaymentViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


# Initialize the router
router = DefaultRouter()

# Register the viewsets with the router
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'donations', DonationViewSet, basename='donation')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'payments', PaymentViewSet, basename='payment')

# The URLs for API endpoints
urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    *router.urls,
    # Include the router URLs here
    path('api/v1/', include(router.urls)),  # Correct inclusion of router URLs
]


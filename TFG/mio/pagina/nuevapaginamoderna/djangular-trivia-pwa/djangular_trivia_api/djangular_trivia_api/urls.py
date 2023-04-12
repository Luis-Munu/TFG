from django.urls import path

from .views import PropertyListView, ZoneListView

urlpatterns = [
    # Add a URL pattern for your ZeroC Ice RPC endpoint
    path('api/properties/', PropertyListView.as_view(), name='property_list'),
    path('api/zones/', ZoneListView.as_view(), name='zone_list'),
]
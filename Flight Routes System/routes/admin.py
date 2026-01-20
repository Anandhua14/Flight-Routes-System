"""
Admin configuration for the Flight Routes System.
"""
from django.contrib import admin
from .models import Airport, Route


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    """Admin interface for Airport model."""
    list_display = ['code', 'name', 'position']
    list_filter = ['position']
    search_fields = ['code', 'name']
    ordering = ['position']
    readonly_fields = ['code']  # Code is primary key, shouldn't be changed after creation


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    """Admin interface for Route model."""
    list_display = ['source', 'destination', 'distance', 'created_at']
    list_filter = ['created_at', 'source', 'destination']
    search_fields = ['source__code', 'source__name', 'destination__code', 'destination__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    # Use select_related for efficient queries
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('source', 'destination')

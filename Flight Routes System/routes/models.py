"""
Models for the Flight Routes System.

This module defines the Airport and Route models with proper relationships,
constraints, and optimizations.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Max, Min, Q


class Airport(models.Model):
    """
    Airport model representing airports in the flight route system.
    
    Attributes:
        code: IATA airport code (3 characters, unique, primary key)
        name: Full name of the airport
        position: Sequential position in the route system (used for left/right traversal)
    """
    code = models.CharField(
        max_length=3,
        unique=True,
        primary_key=True,
        help_text="IATA airport code (3 characters)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Full name of the airport"
    )
    position = models.IntegerField(
        unique=True,
        help_text="Position in the route sequence (used for left/right traversal)"
    )
    
    class Meta:
        ordering = ['position']  # Default ordering by position
        indexes = [
            models.Index(fields=['position']),  # Index for efficient position queries
            models.Index(fields=['code']),  # Index for code lookups
        ]
        verbose_name = "Airport"
        verbose_name_plural = "Airports"
    
    def __str__(self):
        """String representation of the airport."""
        return f"{self.code} - {self.name}"
    
    def clean(self):
        """Validate airport data."""
        super().clean()
        # Ensure code is uppercase
        if self.code:
            self.code = self.code.upper()
        # Validate code length
        if self.code and len(self.code) != 3:
            raise ValidationError({'code': 'Airport code must be exactly 3 characters.'})
        # Validate position uniqueness
        if self.position is not None:
            existing_airport = Airport.objects.filter(position=self.position).exclude(pk=self.pk).first()
            if existing_airport:
                raise ValidationError({
                    'position': f'Position {self.position} is already taken by airport {existing_airport.code} ({existing_airport.name}).'
                })
    
    def save(self, *args, **kwargs):
        """Override save to ensure code is uppercase."""
        self.full_clean()
        super().save(*args, **kwargs)


class Route(models.Model):
    """
    Route model representing flight routes between airports.
    
    Attributes:
        source: Source airport (ForeignKey to Airport)
        destination: Destination airport (ForeignKey to Airport)
        distance: Flight distance in kilometers
        created_at: Timestamp when the route was created
    """
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name='outgoing_routes',
        help_text="Source airport for this route"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name='incoming_routes',
        help_text="Destination airport for this route"
    )
    distance = models.IntegerField(
        help_text="Flight distance in kilometers"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the route was created"
    )
    
    class Meta:
        ordering = ['-created_at']  # Order by creation date (newest first)
        indexes = [
            models.Index(fields=['source', 'destination']),  # Composite index for route lookups
            models.Index(fields=['distance']),  # Index for distance queries
        ]
        # Prevent duplicate routes between the same airports
        unique_together = [['source', 'destination']]
        verbose_name = "Route"
        verbose_name_plural = "Routes"
    
    def __str__(self):
        """String representation of the route."""
        return f"{self.source.code} → {self.destination.code} ({self.distance} km)"
    
    def clean(self):
        """Validate route data."""
        super().clean()
        # Prevent circular routes (airport to itself)
        if self.source == self.destination:
            raise ValidationError(
                {'destination': 'Source and destination airports cannot be the same.'}
            )
        # Validate distance is positive
        if self.distance <= 0:
            raise ValidationError({'distance': 'Distance must be a positive integer.'})
    
    def save(self, *args, **kwargs):
        """Override save to validate route before saving."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_longest_distance_airport(cls):
        """
        Get the airport that has the route with the longest distance.
        Considers both outgoing and incoming routes.
        
        Returns:
            tuple: (airport, max_distance) or (None, None) if no routes exist
        """
        # Get the maximum distance from all routes
        max_distance_result = cls.objects.aggregate(max_distance=Max('distance'))
        max_distance = max_distance_result.get('max_distance')
        
        if max_distance is None:
            return None, None
        
        # Find airports that have routes with this maximum distance
        # Check both outgoing and incoming routes
        airports_with_max_distance = Airport.objects.filter(
            Q(outgoing_routes__distance=max_distance) | 
            Q(incoming_routes__distance=max_distance)
        ).distinct().select_related()
        
        # Return the first airport found (or could return all if multiple)
        airport = airports_with_max_distance.first()
        return airport, max_distance
    
    @classmethod
    def get_shortest_route(cls):
        """
        Get the shortest distance route between any two airports.
        
        Returns:
            Route object with shortest distance, or None if no routes exist
        """
        return cls.objects.select_related('source', 'destination').order_by('distance').first()

"""
Unit tests for the Flight Routes System.

Tests cover:
- Model validation
- Form validation
- View functionality
- Query optimizations
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Airport, Route
from .forms import AirportRouteForm, SearchForm


class AirportModelTest(TestCase):
    """Test cases for Airport model."""
    
    def setUp(self):
        """Set up test data."""
        self.airport1 = Airport.objects.create(
            code='JFK',
            name='John F. Kennedy International Airport',
            position=1
        )
        self.airport2 = Airport.objects.create(
            code='LAX',
            name='Los Angeles International Airport',
            position=2
        )
    
    def test_airport_creation(self):
        """Test creating an airport."""
        self.assertEqual(self.airport1.code, 'JFK')
        self.assertEqual(self.airport1.name, 'John F. Kennedy International Airport')
        self.assertEqual(self.airport1.position, 1)
    
    def test_airport_code_uppercase(self):
        """Test that airport code is automatically uppercased."""
        airport = Airport(code='ord', name='Chicago O\'Hare', position=3)
        airport.save()
        self.assertEqual(airport.code, 'ORD')
    
    def test_airport_code_unique(self):
        """Test that airport codes must be unique."""
        with self.assertRaises(IntegrityError):
            Airport.objects.create(
                code='JFK',
                name='Duplicate Airport',
                position=5
            )
    
    def test_airport_str(self):
        """Test airport string representation."""
        self.assertEqual(str(self.airport1), 'JFK - John F. Kennedy International Airport')


class RouteModelTest(TestCase):
    """Test cases for Route model."""
    
    def setUp(self):
        """Set up test data."""
        self.airport1 = Airport.objects.create(
            code='JFK',
            name='John F. Kennedy International Airport',
            position=1
        )
        self.airport2 = Airport.objects.create(
            code='LAX',
            name='Los Angeles International Airport',
            position=2
        )
        self.route = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=360
        )
    
    def test_route_creation(self):
        """Test creating a route."""
        self.assertEqual(self.route.source, self.airport1)
        self.assertEqual(self.route.destination, self.airport2)
        self.assertEqual(self.route.distance, 360)
    
    def test_circular_route_prevention(self):
        """Test that circular routes (same source and destination) are prevented."""
        route = Route(source=self.airport1, destination=self.airport1, distance=100)
        with self.assertRaises(ValidationError):
            route.full_clean()
    
    def test_duplicate_route_prevention(self):
        """Test that duplicate routes are prevented."""
        with self.assertRaises(IntegrityError):
            Route.objects.create(
                source=self.airport1,
                destination=self.airport2,
                distance=400
            )
    
    def test_negative_distance_prevention(self):
        """Test that negative distance is prevented."""
        route = Route(source=self.airport1, destination=self.airport2, distance=-10)
        with self.assertRaises(ValidationError):
            route.full_clean()
    
    def test_route_str(self):
        """Test route string representation."""
        self.assertEqual(str(self.route), 'JFK → LAX (360 km)')
    
    def test_get_longest_distance_airport(self):
        """Test finding airport with longest distance route."""
        airport3 = Airport.objects.create(code='ORD', name='Chicago O\'Hare', position=3)
        Route.objects.create(source=self.airport2, destination=airport3, distance=500)
        
        airport, max_distance = Route.get_longest_distance_airport()
        self.assertEqual(max_distance, 500)
        self.assertIn(airport, [self.airport2, airport3])
    
    def test_get_shortest_route(self):
        """Test finding shortest route."""
        airport3 = Airport.objects.create(code='ORD', name='Chicago O\'Hare', position=3)
        Route.objects.create(source=self.airport2, destination=airport3, distance=180)
        
        shortest = Route.get_shortest_route()
        self.assertEqual(shortest.distance, 180)


class AirportRouteFormTest(TestCase):
    """Test cases for AirportRouteForm."""
    
    def setUp(self):
        """Set up test data."""
        self.airport1 = Airport.objects.create(
            code='JFK',
            name='John F. Kennedy International Airport',
            position=1
        )
        self.airport2 = Airport.objects.create(
            code='LAX',
            name='Los Angeles International Airport',
            position=2
        )
    
    def test_valid_form(self):
        """Test form with valid data."""
        form_data = {
            'source': self.airport1.pk,
            'destination': self.airport2.pk,
            'distance': 360
        }
        form = AirportRouteForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_circular_route_validation(self):
        """Test form validation prevents circular routes."""
        form_data = {
            'source': self.airport1.pk,
            'destination': self.airport1.pk,
            'distance': 360
        }
        form = AirportRouteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Source and destination airports cannot be the same', str(form.errors))
    
    def test_duplicate_route_validation(self):
        """Test form validation prevents duplicate routes."""
        Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=360
        )
        form_data = {
            'source': self.airport1.pk,
            'destination': self.airport2.pk,
            'distance': 400
        }
        form = AirportRouteForm(data=form_data)
        self.assertFalse(form.is_valid())


class SearchFormTest(TestCase):
    """Test cases for SearchForm."""
    
    def setUp(self):
        """Set up test data."""
        self.airport1 = Airport.objects.create(
            code='JFK',
            name='John F. Kennedy International Airport',
            position=1
        )
    
    def test_valid_form(self):
        """Test form with valid data."""
        form_data = {
            'starting_airport': self.airport1.pk,
            'direction': 'right',
            'n': 2
        }
        form = SearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_n_value(self):
        """Test form validation for negative N value."""
        form_data = {
            'starting_airport': self.airport1.pk,
            'direction': 'right',
            'n': -1
        }
        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())

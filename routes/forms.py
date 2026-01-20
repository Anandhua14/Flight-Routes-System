"""
Forms for the Flight Routes System.

This module defines forms for adding routes and searching for Nth node.
"""
from django import forms
from .models import Airport, Route


class AirportForm(forms.ModelForm):
    """
    Form for adding a new airport.
    
    Fields:
        code: IATA airport code (3 characters)
        name: Full name of the airport
        position: Position in the route sequence
    """
    code = forms.CharField(
        label="Airport Code (IATA)",
        max_length=3,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., JFK',
            'maxlength': '3',
            'style': 'text-transform: uppercase;'
        }),
        help_text="3-letter IATA airport code"
    )
    name = forms.CharField(
        label="Airport Name",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., John F. Kennedy International Airport'
        }),
        help_text="Full name of the airport"
    )
    position = forms.IntegerField(
        label="Position",
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Position in route sequence (must be unique)',
            'min': '1'
        }),
        help_text="Position in the route sequence (used for left/right traversal). Each position number must be unique."
    )
    
    class Meta:
        model = Airport
        fields = ['code', 'name', 'position']
    
    def clean_code(self):
        """Validate and normalize airport code."""
        code = self.cleaned_data.get('code', '').upper().strip()
        if len(code) != 3:
            raise forms.ValidationError('Airport code must be exactly 3 characters.')
        if not code.isalpha():
            raise forms.ValidationError('Airport code must contain only letters.')
        return code
    
    def clean_position(self):
        """Validate position uniqueness."""
        position = self.cleaned_data.get('position')
        if position is not None:
            # Check if position is already taken by another airport
            existing_airport = Airport.objects.filter(position=position).exclude(
                pk=self.instance.pk if self.instance.pk else None
            ).first()
            if existing_airport:
                raise forms.ValidationError(
                    f'Position {position} is already taken by airport {existing_airport.code} ({existing_airport.name}). '
                    f'Please choose a different position.'
                )
        return position


class AirportRouteForm(forms.ModelForm):
    """
    Form for adding a new route between airports.
    
    Fields:
        source: Source airport (dropdown)
        destination: Destination airport (dropdown)
        distance: Flight distance in kilometers
    """
    source = forms.ModelChoiceField(
        queryset=Airport.objects.all().order_by('code'),
        label="Source Airport",
        empty_label="Select source airport",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the source airport"
    )
    destination = forms.ModelChoiceField(
        queryset=Airport.objects.all().order_by('code'),
        label="Destination Airport",
        empty_label="Select destination airport",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the destination airport"
    )
    distance = forms.IntegerField(
        label="Distance (km)",
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Distance in kilometers',
            'min': '1'
        }),
        help_text="Flight distance in kilometers"
    )
    
    class Meta:
        model = Route
        fields = ['source', 'destination', 'distance']
    
    def __init__(self, *args, **kwargs):
        """Initialize form and optimize queryset."""
        super().__init__(*args, **kwargs)
        # Optimize queryset if needed (though ModelChoiceField handles this)
        self.fields['source'].queryset = Airport.objects.all().order_by('code')
        self.fields['destination'].queryset = Airport.objects.all().order_by('code')
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        source = cleaned_data.get('source')
        destination = cleaned_data.get('destination')
        
        # Prevent circular routes
        if source and destination and source == destination:
            raise forms.ValidationError(
                "Source and destination airports cannot be the same."
            )
        
        # Check for duplicate routes
        if source and destination:
            existing_route = Route.objects.filter(
                source=source,
                destination=destination
            ).exists()
            if existing_route and not self.instance.pk:
                raise forms.ValidationError(
                    f"A route from {source.code} to {destination.code} already exists."
                )
        
        return cleaned_data


class SearchForm(forms.Form):
    """
    Form for searching Nth left/right node (Question 1).
    
    Fields:
        starting_airport: Starting airport (dropdown)
        direction: Direction to traverse ('left' or 'right')
        n: Number of positions to traverse
    """
    DIRECTION_CHOICES = [
        ('left', 'Left (lower position numbers)'),
        ('right', 'Right (higher position numbers)'),
    ]
    
    starting_airport = forms.ModelChoiceField(
        queryset=Airport.objects.all().order_by('code'),
        label="Starting Airport",
        empty_label="Select starting airport",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the starting airport"
    )
    direction = forms.ChoiceField(
        choices=DIRECTION_CHOICES,
        label="Direction",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Direction to traverse"
    )
    n = forms.IntegerField(
        label="Number of Positions (N)",
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of positions to traverse',
            'min': '1'
        }),
        help_text="Number of positions to traverse"
    )
    
    def __init__(self, *args, **kwargs):
        """Initialize form."""
        super().__init__(*args, **kwargs)
        self.fields['starting_airport'].queryset = Airport.objects.all().order_by('code')

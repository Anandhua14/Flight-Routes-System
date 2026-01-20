"""
Views for the Flight Routes System.

This module contains all views for handling user requests including:
- Home page
- Adding routes
- Question 1: Finding Nth left/right node
- Question 2: Longest distance node
- Question 3: Shortest distance route
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Airport, Route
from .forms import AirportRouteForm, SearchForm, AirportForm


class HomeView(TemplateView):
    """Home page view with navigation to all functionalities."""
    template_name = 'routes/home.html'
    
    def get_context_data(self, **kwargs):
        """Add context data for home page."""
        context = super().get_context_data(**kwargs)
        context['airport_count'] = Airport.objects.count()
        context['route_count'] = Route.objects.count()
        return context


class AddRouteView(TemplateView):
    """View for adding a new route between airports."""
    template_name = 'routes/add_route.html'
    
    def get_context_data(self, **kwargs):
        """Get context data including the form."""
        context = super().get_context_data(**kwargs)
        context['form'] = AirportRouteForm()
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle form submission."""
        form = AirportRouteForm(request.POST)
        if form.is_valid():
            try:
                # Use atomic transaction to ensure data integrity
                with transaction.atomic():
                    route = form.save()
                messages.success(
                    request,
                    f"Route from {route.source.code} to {route.destination.code} "
                    f"({route.distance} km) added successfully!"
                )
                return redirect('routes:add_route')
            except Exception as e:
                messages.error(request, f"Error adding route: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
        
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)


class NthNodeSearchView(TemplateView):
    """
    View for Question 1: Finding Nth left/right node.
    
    Given a starting airport, traverses N positions in the specified direction
    based on the position field and returns the airport at that position.
    """
    template_name = 'routes/nth_node_search.html'
    
    def get_context_data(self, **kwargs):
        """Get context data including the search form."""
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm()
        context['result'] = None
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle search form submission."""
        form = SearchForm(request.POST)
        result = None
        error_message = None
        
        if form.is_valid():
            starting_airport = form.cleaned_data['starting_airport']
            direction = form.cleaned_data['direction']
            n = form.cleaned_data['n']
            
            try:
                # Get the starting position
                start_position = starting_airport.position
                
                # Calculate target position based on direction
                if direction == 'left':
                    target_position = start_position - n
                else:  # direction == 'right'
                    target_position = start_position + n
                
                # Find airport at target position
                # Use efficient query with index
                target_airport = Airport.objects.filter(position=target_position).first()
                
                if target_airport:
                    result = {
                        'starting_airport': starting_airport,
                        'direction': direction,
                        'n': n,
                        'target_airport': target_airport,
                        'start_position': start_position,
                        'target_position': target_position,
                    }
                else:
                    error_message = (
                        f"No airport found at position {target_position}. "
                        f"The position is out of bounds."
                    )
            except Exception as e:
                error_message = f"Error performing search: {str(e)}"
        
        context = {
            'form': form,
            'result': result,
            'error_message': error_message,
        }
        return render(request, self.template_name, context)


class LongestDurationView(TemplateView):
    """
    View for Question 2: Displaying the airport with longest distance route.
    
    Shows the airport that has the route with the longest distance,
    considering both outgoing and incoming routes.
    """
    template_name = 'routes/longest_duration.html'
    
    def get_context_data(self, **kwargs):
        """Get context data with longest distance airport."""
        context = super().get_context_data(**kwargs)
        
        # Use the optimized class method
        airport, max_distance = Route.get_longest_distance_airport()
        
        context['airport'] = airport
        context['max_distance'] = max_distance
        
        # Get all routes with this maximum distance for display
        if max_distance:
            # Optimize query with select_related
            routes = Route.objects.filter(
                Q(source=airport) | Q(destination=airport),
                distance=max_distance
            ).select_related('source', 'destination')
            context['routes'] = routes
        else:
            context['routes'] = Route.objects.none()
        
        return context


class ShortestRouteView(TemplateView):
    """
    View for Question 3: Displaying the shortest distance route.
    
    Shows the shortest distance route between any two airports.
    Handles cases where multiple routes might have the same shortest distance.
    """
    template_name = 'routes/shortest_route.html'
    
    def get_context_data(self, **kwargs):
        """Get context data with shortest route(s)."""
        context = super().get_context_data(**kwargs)
        
        # Get the shortest route using optimized query
        shortest_route = Route.get_shortest_route()
        
        if shortest_route:
            # Get all routes with the same shortest distance
            shortest_distance = shortest_route.distance
            # Optimize query with select_related
            shortest_routes = Route.objects.filter(
                distance=shortest_distance
            ).select_related('source', 'destination').order_by('source__code', 'destination__code')
            
            context['shortest_route'] = shortest_route
            context['shortest_distance'] = shortest_distance
            context['shortest_routes'] = shortest_routes
        else:
            context['shortest_route'] = None
            context['shortest_distance'] = None
            context['shortest_routes'] = Route.objects.none()
        
        return context


class AddAirportView(TemplateView):
    """View for adding a new airport."""
    template_name = 'routes/add_airport.html'
    
    def get_context_data(self, **kwargs):
        """Get context data including the form."""
        context = super().get_context_data(**kwargs)
        context['form'] = AirportForm()
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle form submission."""
        form = AirportForm(request.POST)
        if form.is_valid():
            try:
                # Use atomic transaction to ensure data integrity
                with transaction.atomic():
                    airport = form.save()
                messages.success(
                    request,
                    f"Airport {airport.code} ({airport.name}) added successfully!"
                )
                return redirect('routes:add_airport')
            except Exception as e:
                messages.error(request, f"Error adding airport: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
        
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)


class AirportListView(ListView):
    """View for listing all airports with delete option."""
    model = Airport
    template_name = 'routes/airport_list.html'
    context_object_name = 'airports'
    ordering = ['position']
    paginate_by = 20
    
    def get_queryset(self):
        """Optimize queryset."""
        return Airport.objects.all().order_by('position')


class RouteListView(ListView):
    """View for listing all routes with delete option."""
    model = Route
    template_name = 'routes/route_list.html'
    context_object_name = 'routes'
    ordering = ['-created_at']
    paginate_by = 20
    
    def get_queryset(self):
        """Optimize queryset with select_related."""
        return Route.objects.select_related('source', 'destination').order_by('-created_at')


@require_http_methods(["POST"])
def delete_airport(request, code):
    """
    View for deleting an airport.
    
    Prevents deletion if airport has associated routes.
    """
    airport = get_object_or_404(Airport, code=code)
    
    # Check if airport has associated routes
    outgoing_count = airport.outgoing_routes.count()
    incoming_count = airport.incoming_routes.count()
    total_routes = outgoing_count + incoming_count
    
    if total_routes > 0:
        messages.error(
            request,
            f"Cannot delete airport {airport.code} because it has {total_routes} "
            f"associated route(s). Please delete the routes first."
        )
        return redirect('routes:airport_list')
    
    try:
        with transaction.atomic():
            airport_name = airport.name
            airport_code = airport.code
            airport.delete()
        messages.success(
            request,
            f"Airport {airport_code} ({airport_name}) deleted successfully!"
        )
    except Exception as e:
        messages.error(request, f"Error deleting airport: {str(e)}")
    
    return redirect('routes:airport_list')


@require_http_methods(["POST"])
def delete_route(request, pk):
    """View for deleting a route."""
    route = get_object_or_404(Route.objects.select_related('source', 'destination'), pk=pk)
    
    try:
        with transaction.atomic():
            source_code = route.source.code
            dest_code = route.destination.code
            distance = route.distance
            route.delete()
        messages.success(
            request,
            f"Route from {source_code} to {dest_code} ({distance} km) deleted successfully!"
        )
    except Exception as e:
        messages.error(request, f"Error deleting route: {str(e)}")
    
    return redirect('routes:route_list')

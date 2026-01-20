"""
URL configuration for the routes app.
"""
from django.urls import path
from . import views

app_name = 'routes'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('add-airport/', views.AddAirportView.as_view(), name='add_airport'),
    path('airports/', views.AirportListView.as_view(), name='airport_list'),
    path('airports/<str:code>/delete/', views.delete_airport, name='delete_airport'),
    path('add-route/', views.AddRouteView.as_view(), name='add_route'),
    path('routes/', views.RouteListView.as_view(), name='route_list'),
    path('routes/<int:pk>/delete/', views.delete_route, name='delete_route'),
    path('nth-node/', views.NthNodeSearchView.as_view(), name='nth_node'),
    path('longest-duration/', views.LongestDurationView.as_view(), name='longest_duration'),
    path('shortest-route/', views.ShortestRouteView.as_view(), name='shortest_route'),
]

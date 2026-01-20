# Flight Routes System

A Django web application for managing flight routes between airports with functionalities to search and analyze route connections.

## Features

- **Airport Management**: Create and manage airports with IATA codes, names, and positions
- **Route Management**: Add flight routes between airports with duration tracking
- **Nth Node Search**: Find airports N positions left or right from a starting airport
- **Longest Duration Analysis**: Identify airports with routes having the longest duration
- **Shortest Route Analysis**: Find the shortest duration route between any two airports
- **Admin Interface**: Full Django admin interface for managing data
- **Optimized Queries**: Efficient database queries using select_related, prefetch_related, and indexes
- **Data Validation**: Prevents circular routes, duplicate routes, and invalid data

## Project Structure

```
flight_routes/
├── flight_routes/          # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── routes/                  # Main application
│   ├── migrations/
│   ├── templates/
│   │   └── routes/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── add_route.html
│   │       ├── nth_node_search.html
│   │       ├── longest_duration.html
│   │       └── shortest_route.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   └── urls.py
├── manage.py
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or navigate to the project directory:**
   ```bash
   cd "E:\Flight Routes System"
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional, for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data (optional):**
   ```bash
   python manage.py loaddata sample_data.json
   ```

8. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

9. **Access the application:**
   - Open your browser and navigate to: `http://127.0.0.1:8000/`
   - Admin interface: `http://127.0.0.1:8000/admin/`

## Usage

### Adding Routes

1. Navigate to "Add Route" from the home page
2. Select source and destination airports from the dropdowns
3. Enter the flight duration in minutes
4. Click "Add Route"

### Finding Nth Node (Question 1)

1. Navigate to "Nth Node Search"
2. Select a starting airport
3. Choose direction (left = lower positions, right = higher positions)
4. Enter the number of positions to traverse (N)
5. Click "Search" to find the airport at that position

### Longest Duration (Question 2)

1. Navigate to "Longest Duration"
2. The system automatically displays the airport with the route having the longest duration
3. All routes with this maximum duration are shown

### Shortest Route (Question 3)

1. Navigate to "Shortest Route"
2. The system automatically displays the shortest duration route
3. If multiple routes have the same shortest duration, all are shown

## Database Models

### Airport
- `code` (CharField, max_length=3, unique, primary key): IATA airport code
- `name` (CharField, max_length=100): Full airport name
- `position` (IntegerField): Position in route sequence

### Route
- `source` (ForeignKey to Airport): Source airport
- `destination` (ForeignKey to Airport): Destination airport
- `duration` (IntegerField): Flight duration in minutes
- `created_at` (DateTimeField): Timestamp of creation

## Optimization Features

- **Database Indexes**: Added on frequently queried fields (position, code, duration)
- **Query Optimization**: Uses `select_related()` and `prefetch_related()` to avoid N+1 queries
- **Atomic Transactions**: Database operations use transactions for data integrity
- **Efficient Aggregations**: Uses Django's aggregation functions for optimized queries

## Testing

Run the test suite:
```bash
python manage.py test routes
```

The test suite includes:
- Model validation tests
- Form validation tests
- View functionality tests
- Query optimization tests

## Example Data

Sample airports and routes:
- **Airports**: JFK (position 1), LAX (position 2), ORD (position 3), DFW (position 4)
- **Routes**: 
  - JFK → LAX (360 min)
  - LAX → ORD (240 min)
  - ORD → DFW (180 min)

## Technical Details

- **Django Version**: 4.2+
- **Database**: SQLite (development), configurable for production
- **Frontend**: Bootstrap 5 for responsive design
- **Python Version**: 3.8+

## Best Practices Implemented

- ✅ Class-Based Views for better code organization
- ✅ Form validation with meaningful error messages
- ✅ Database indexes for performance
- ✅ Atomic transactions for data integrity
- ✅ Comprehensive comments and docstrings
- ✅ PEP 8 compliant code
- ✅ Unit tests for core functionality
- ✅ Admin interface configuration
- ✅ Responsive design with Bootstrap

## Troubleshooting

### Migration Issues
If you encounter migration issues:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files
If static files don't load:
```bash
python manage.py collectstatic
```

## License

This project is provided as-is for educational and development purposes.

## Author

Flight Routes System - Django Implementation

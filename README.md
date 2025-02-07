# Hack The North Backend Challenge

A Flask REST API for managing hackers and their activity scans during an event.
The API allows organizers to track hacker participation in activities and manage
hacker information.

## Setup

1. Install Docker and Docker Compose
2. Clone this repository
3. Start the application:

```bash
docker-compose up --build
```

## App Structure

- `main.py`: Entry point and API routes
- `app/`: Main application package
  - `database/`: Database related code
    - `models.py`: Database queries and operations
    - `schema.py`: Table definitions and initialization
    - `triggers.py`: SQLite triggers
  - `models/`: Data models
    - `user.py`: User and Scan classes
  - `utils/`: Utility functions
    - `data_loader.py`: Loads example data on initial startup

## Database Schema

The database consists of three main tables: Hackers, Activities, and Scans.

### Hackers Table

- `id` (int): Primary key, auto-incrementing identifier
- `name` (text): Hacker's full name
- `email` (text): Unique email address, used as stable identifier
- `phone` (text): Contact phone number
- `badge_code` (text): Unique identifier for physical badge
- `updated_at` (timestamp): Last modification time
- `created_at` (timestamp): Account creation time
- Has many: Scans (one hacker can have multiple scans)

### Activities Table

- `id` (int): Primary key, auto-incrementing identifier
- `activity_name` (text): Unique name of the activity
- `activity_category` (text): Category (e.g., meal, workshop)
- `is_active` (boolean): Whether activity is currently available
- `created_at` (timestamp): When activity was added
- Has many: Scans (one activity can have multiple scans)

### Scans Table

- `id` (int): Primary key, auto-incrementing identifier
- `hacker_id` (int): Foreign key to Hackers table (belongs to one hacker)
- `activity_id` (int): Foreign key to Activities table (belongs to one activity)
- `scanned_at` (timestamp): When scan occurred
- `created_at` (timestamp): Record creation time
- Foreign Keys:
  - `hacker_id` references `hackers(id)`
  - `activity_id` references `activities(id)`

### Relationships

- One-to-many between Hackers and Scans
- One-to-many between Activities and Scans
- Scans table acts as a join table tracking participation

## API Endpoints

#### `GET /users`

Returns list of all users with their scan history.

#### GET /users/<email>

Returns specific user's data and scan history.

#### PUT /users/<email>

Updates user information. Accepts:

```json
{
  "name": "John Smith",
  "phone": "+1 (555) 123-4567",
  "badge_code": "new-badge-code"
}
```

- Email cannot be modified
- Badge codes must be unique
- All fields optional (partial updates supported)

### Activity Scanning

#### PUT /scan/<email>

Records a new activity scan. Accepts:

```json
{
  "activity_name": "Lunch",
  "activity_category": "meal"
}
```

Returns:

```json
{
  "activity_name": "Lunch",
  "activity_category": "meal",
  "scanned_at": "2024-02-05 15:30:00"
}
```

- One scan per activity per user per day
- Creates new activities automatically
- Updates user's last activity timestamp

### Analytics

#### GET /scans

Returns activity statistics with optional filters:

- `min_frequency`: Minimum scan count
- `max_frequency`: Maximum scan count
- `activity_category`: Filter by category

Example: `/scans?min_frequency=5&activity_category=meal`

## Design Decisions

### Data Model

- Users identified by unique email
- Activities created dynamically
- Scans track participation with timestamps
- Badge codes unique but reassignable

### Performance

- Cached analytics (5-min TTL)
- SQLite indexes on common queries
- Efficient partial updates
- Transaction support

### Error Handling

- Descriptive error messages
- Appropriate HTTP status codes
- Transaction rollbacks
- Duplicate scan prevention

## Assumptions

- No auth required (would add in production)
- SQLite sufficient for demo (would use PostgreSQL in prod)
- One scan per activity per day is sufficient
- Analytics can be slightly delayed (5-min cache)
- Badge codes may need to be reassigned
- Email addresses are permanent identifiers

## Future Improvements

1. Authentication & authorization
2. Rate limiting
3. Comprehensive testing
4. Activity management endpoints
5. Swagger/OpenAPI documentation
6. Monitoring & logging
7. PostgreSQL for better concurrency
8. Pagination for large requests (e.g. `GET/users`)

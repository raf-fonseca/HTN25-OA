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

The database consists of four main tables: Hackers, Activities, Scans, and
Checked In Users.

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

### Checked In Users Table

- `id` (int): Primary key, auto-incrementing identifier
- `hacker_id` (int): Foreign key to Hackers table, unique
- `checked_in_at` (timestamp): When user was checked in
- Foreign Keys:
  - `hacker_id` references `hackers(id)`

### Relationships

- One-to-many between Hackers and Scans
- One-to-many between Activities and Scans
- One-to-one between Hackers and Checked In Users
- Scans table acts as a join table tracking participation

## API Endpoints

`GET /users`

Returns list of all users with their scan history. Supports filtering by
check-in status.

Query Parameters:

- `checked_in`: Filter by check-in status
  - `true`: Returns only users who have checked in
  - `false`: Returns only users who have not checked in
  - If omitted, returns all users

Example Request:

```
/users?checked_in=true
```

Example Response:

```json
[
  {
    "badge_code": "soon-hundred-rise-program",
    "email": "nancy02@example.com",
    "is_checked_in": true,
    "name": "Alan Johnson",
    "phone": "(267)834-3238",
    "scans": [
      {
        "activity_category": "meal",
        "activity_name": "sunday_breakfast",
        "scanned_at": "2025-01-17T03:47:43-05:00"
      }
    ],
    "updated_at": "2025-02-07T13:39:31-05:00"
  }
  ...
]
```

`GET /users/<email>`

Returns specific user's data and scan history. Returns 404 if user does not
exist.

Example Request:

```
/users/fward@example.org
```

Example Response:

```json
{
  "badge_code": "laugh-resource-apply-staff",
  "email": "fward@example.org",
  "is_checked_in": false,
  "name": "Amanda Hicks",
  "phone": "001-624-335-0468x678",
  "scans": [
    {
      "activity_category": "activity",
      "activity_name": "opening_ceremony",
      "scanned_at": "2025-01-18T11:09:59.389324"
    },
    {
      "activity_category": "meal",
      "activity_name": "friday_dinner",
      "scanned_at": "2025-01-19T15:07:23.944351"
    }
  ],
  "updated_at": "2025-02-07T13:39:31-05:00"
}
```

#### PUT /users/<email>

Updates user information. Returns 404 if user does not exist.

Example Request:

```bash
curl -X PUT http://localhost:3000/users/nancy02@example.com \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alan Smith",
    "phone": "(267)834-3239",
    "badge_code": "new-badge-code"
  }'
```

Example Response:

```json
{
  "badge_code": "new-badge-code",
  "email": "nancy02@example.com",
  "is_checked_in": true,
  "name": "Alan Smith",
  "phone": "(267)834-3239",
  "scans": [],
  "updated_at": "2025-02-07T13:40:31-05:00"
}
```

### Check-in Management

#### PUT /checkin

Registers and checks in a new user. Returns 400 if user already exists.

Example Request:

```bash
curl -X PUT http://localhost:3000/checkin \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "email": "john@example.com",
    "phone": "+1555123456",
    "badge_code": "HTN2024-123"
  }'
```

Example Response:

```json
[
  {
    "badge_code": "HTN2024-123",
    "email": "john@example.com",
    "is_checked_in": true,
    "name": "John Smith",
    "phone": "+1555123456",
    "scans": [],
    "updated_at": "2025-02-07T13:41:31-05:00"
  }
]
```

#### PUT /checkout/<email>

Checks out a user. Returns 404 if user does not exist.

Example Request:

```bash
curl -X PUT http://localhost:3000/checkout/john@example.com
```

Example Response:

```json
[
  {
    "badge_code": "HTN2024-123",
    "email": "john@example.com",
    "is_checked_in": false,
    "name": "John Smith",
    "phone": "+1555123456",
    "scans": [],
    "updated_at": "2025-02-07T13:42:31-05:00"
  }
]
```

### Activity Management

#### PUT /scan/<email>

Records a new activity scan. Returns 404 if user does not exist.

Example Request:

```bash
curl -X PUT http://localhost:3000/scan/john@example.com \
  -H "Content-Type: application/json" \
  -d '{
    "activity_name": "lunch",
    "activity_category": "meal"
  }'
```

Example Response:

```json
{
  "badge_code": "HTN2024-123",
  "email": "john@example.com",
  "is_checked_in": true,
  "name": "John Smith",
  "phone": "+1555123456",
  "scans": [
    {
      "activity_category": "meal",
      "activity_name": "lunch",
      "scanned_at": "2025-02-07T13:43:31-05:00"
    }
  ],
  "updated_at": "2025-02-07T13:43:31-05:00"
}
```

#### GET /scans

Returns activity statistics with optional filters.

Query Parameters:

- `min_frequency`: Minimum scan count
- `max_frequency`: Maximum scan count
- `activity_category`: Filter by category

Example Request:

```
/scans?min_frequency=5&activity_category=meal
```

Example Response:

```json
{
  "activities": [
    {
      "activity_name": "lunch",
      "activity_category": "meal",
      "scan_count": 10
    },
    {
      "activity_name": "dinner",
      "activity_category": "meal",
      "scan_count": 8
    }
  ],
  "total_activities": 2,
  "cached_at": "2025-02-07T13:44:31-05:00"
}
```

## Important Decisions

### Data Model

- Users identified by unique email
- Activities created dynamically
- Scans track participation with timestamps
- Badge codes unique but reassignable
- Check-in status managed through dedicated table
- All timestamps in EST timezone (UTC-5)

### Check-in Logic

- Check-in status independent of scan history
- Users can be checked in without any scans
- Check-in status persists until explicit checkout
- Only one active check-in per user
- Check-in time recorded for auditing

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

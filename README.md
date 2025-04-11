# QR Code Feedback System

A modern feedback system that uses QR codes to collect customer feedback for different branches.

## Features

- 10-point rating scale (1-10) with color coding:
  - 1-6: Red (Negative)
  - 7-8: Yellow (Neutral)
  - 9-10: Green (Positive)
- Feedback categories:
  - Service Rating
  - Cleanliness Rating
  - Staff Rating
  - Waiting Time Rating
  - Overall Rating
- Admin panel for viewing feedback
- QR code generation for each branch
- Modern, responsive UI with gradients and animations
- Georgian language interface

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up PostgreSQL database:
   ```bash
   createdb feedback_system
   ```
4. Create a `.env` file with the following variables:
   ```
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://username:password@localhost:5432/feedback_system
   ```
5. Run the application:
   ```bash
   python app.py
   ```

## Deployment

The application is configured for deployment on Render.com:

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Add the following environment variables:
   - `FLASK_ENV`: production
   - `SECRET_KEY`: (generate a secure key)
   - `DATABASE_URL`: (will be automatically set by Render's PostgreSQL add-on)

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);
```

### Branches Table
```sql
CREATE TABLE branches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL
);
```

### Feedback Table
```sql
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER REFERENCES branches(id),
    service_rating INTEGER NOT NULL,
    cleanliness_rating INTEGER NOT NULL,
    staff_rating INTEGER NOT NULL,
    waiting_time_rating INTEGER NOT NULL,
    overall_rating INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## License

MIT 
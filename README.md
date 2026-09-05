<div align="center">

# 🎬 BookMySeat

### A Django-based Online Movie Ticket Booking Platform

A full-stack movie booking web application built with **Django**, **PostgreSQL/Supabase**, and **Razorpay**, featuring movie browsing, secure authentication, seat reservation, online payments, and an advanced admin analytics dashboard.

</div>

---

## 🚀 Features

### 🎥 Movie Management
- Browse available movies
- Movie posters and trailers
- Movie rating, cast, description, genres and languages
- YouTube trailer integration
- TMDB movie ID support

### 👤 User Authentication
- User registration and login
- Email verification
- Secure password hashing using Django authentication
- Password reset through email
- User profile management

### 💺 Seat Booking
- Theater and show-time selection
- Seat availability checking
- Temporary seat reservation
- Prevents duplicate active seat reservations
- Booking confirmation after successful payment

### 💳 Online Payment
- Razorpay payment integration
- Payment order creation
- Payment success/failure handling
- Payment status tracking
- Razorpay webhook event handling
- Idempotency protection for payment operations

### 📊 Admin Analytics Dashboard
The project includes an admin analytics system designed for large datasets.

- Total revenue
  - Daily
  - Weekly
  - Monthly
- Most popular movies based on bookings
- Busiest theaters based on seat occupancy
- Peak booking hours
- Cancellation rates
- Database-level aggregation
- Optimized queries and indexes
- Caching support
- Role-based admin access
- Protection against unauthorized API access

### 🔐 Security
- Django's built-in password hashing
- Login/session based authentication
- Admin-only dashboard access
- CSRF protection
- Secure YouTube URL validation
- YouTube `youtube-nocookie.com` embed URLs
- Payment idempotency protection
- Webhook replay protection

---

## 🛠️ Technologies Used

<div align="center">

| Technology | Purpose |
|---|---|
| 🐍 Python | Backend programming |
| 🎯 Django | Web framework |
| 🗄️ SQLite | Local development database |
| 🐘 PostgreSQL | Production database |
| ⚡ Supabase | Hosted PostgreSQL database |
| 💳 Razorpay | Online payments |
| 🌐 HTML5 | Frontend structure |
| 🎨 CSS3 | Frontend styling |
| ☕ JavaScript | Frontend interactions |
| 🔴 Redis / Django Cache | Analytics caching |
| 🚀 Vercel | Frontend/deployment hosting |

</div>

---

## 📁 Project Structure

```text
bookmyseat/
│
├── bookings/
│   ├── migrations/
│   ├── services/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── services.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── movies/
│   ├── management/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── users/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── bookmyseat/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── celery.py
│   └── wsgi.py
│
├── templates/
│   ├── bookings/
│   ├── movies/
│   └── users/
│
├── staticfiles/
├── data.json
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd bookmyseat
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DATABASE_URL=your-database-url

RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-email-password
```

> ⚠️ Never upload `.env` or secret credentials to GitHub.

---

## 🗄️ Database Setup

### Local SQLite

For local development, Django can use:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

Run:

```bash
python manage.py migrate
```

### PostgreSQL / Supabase

For production, PostgreSQL can be used through Supabase.

Set the database connection string in the environment:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
```

Then run:

```bash
python manage.py migrate
```

To transfer Django data from a local database:

```bash
python manage.py dumpdata --indent 2 > data.json
```

After configuring the PostgreSQL/Supabase database:

```bash
python manage.py loaddata data.json
```

---

## 🧪 Run the Project

```bash
python manage.py check
```

```bash
python manage.py migrate
```

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## 📊 Admin Analytics Optimization

The analytics dashboard is designed to avoid loading thousands of booking records into Python memory.

Instead of:

```python
bookings = Booking.objects.all()

for booking in bookings:
    # calculate statistics in Python
    pass
```

the application should use Django ORM aggregation:

```python
from django.db.models import Count, Sum

total_bookings = Booking.objects.count()

popular_movies = (
    Booking.objects
    .values("movie__name")
    .annotate(total=Count("id"))
    .order_by("-total")
)
```

Revenue can be calculated using database aggregation:

```python
from django.db.models import Sum

revenue = PaymentOrder.objects.filter(
    status="paid"
).aggregate(
    total=Sum("amount_paise")
)
```

This allows the database to perform the heavy aggregation instead of loading the complete dataset into application memory.

---

## ⚡ Database Indexing

Important fields should be indexed to improve analytics performance.

Examples:

```python
class PaymentOrder(models.Model):

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    expires_at = models.DateTimeField(
        db_index=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["status", "expires_at"]),
            models.Index(fields=["user", "status"]),
        ]
```

For booking analytics, indexes can also be added to frequently filtered fields such as:

```python
booked_at
movie
theater
payment_order
```

After changing models:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🔐 Admin Dashboard Access

The analytics dashboard must only be accessible to authorized administrators.

Example:

```python
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    ...
```

For API endpoints, the same authorization rules should be applied so that users cannot directly access admin analytics APIs.

---

## 💾 Caching

Analytics can be expensive when the database contains a large number of bookings.

Caching can reduce repeated database calculations.

Example:

```python
from django.core.cache import cache

analytics = cache.get("admin_analytics")

if analytics is None:
    analytics = {
        # database aggregation results
    }

    cache.set(
        "admin_analytics",
        analytics,
        timeout=300
    )
```

The cache can be refreshed periodically instead of recalculating every metric for every request.

---

## 📈 Large Dataset Support

The analytics implementation is intended to support datasets containing at least:

```text
50,000+ bookings
```

Performance considerations:

- Database-level `Count()`
- Database-level `Sum()`
- `Avg()`, `Max()`, `Min()` where required
- `values()` and `annotate()`
- Proper database indexes
- Date/time filtering at database level
- Pagination for large admin lists
- Redis or Django cache
- Avoiding `.all()` followed by Python loops
- Avoiding unnecessary database queries

---

## 🔑 Admin Credentials

For security reasons, **do not publish the real admin password inside this GitHub README**.

For an academic/project report, provide the test/admin credentials separately through the required submission channel.

Django stores user passwords using password hashing rather than plain text.

Create an admin account using:

```bash
python manage.py createsuperuser
```

Then access Django admin:

```text
http://127.0.0.1:8000/admin/
```

---

## 🧪 Testing

Run all tests:

```bash
python manage.py test
```

Check the project configuration:

```bash
python manage.py check
```

---

## 🚀 Deployment

Typical deployment architecture:

```text
                    ┌─────────────────┐
                    │      User       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Web Frontend   │
                    │     Vercel      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Django Backend  │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
        ┌──────────────┐          ┌──────────────┐
        │  Supabase    │          │ Razorpay     │
        │ PostgreSQL   │          │ Payments     │
        └──────────────┘          └──────────────┘
```

---

## 🎯 Main Project Goal

BookMySeat is designed to provide a complete movie ticket booking experience while demonstrating:

- Django backend development
- Database design
- Authentication and authorization
- Payment integration
- Seat reservation logic
- Database optimization
- Aggregation queries
- Caching
- Security
- Production deployment

---

## 👨‍💻 Developer

**BookMySeat Project**

Built with ❤️ using Django and modern web technologies.

---

<div align="center">

### ⭐ If you like this project, consider giving it a star on GitHub!

**BookMySeat — Movie Ticket Booking System 🎬**

</div>

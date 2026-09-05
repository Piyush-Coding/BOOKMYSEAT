from datetime import timedelta

from django.core.cache import cache
from django.db.models import (
    Count,
    Sum,
    F,
    FloatField,
    ExpressionWrapper,
    Q,
)
from django.db.models.functions import TruncDate, ExtractHour
from django.utils import timezone

from .models import PaymentOrder
from movies.models import Booking, Movie, Theater


CACHE_TIMEOUT = 60  # 1 minute


def get_dashboard_analytics():
    cache_key = "admin_dashboard_analytics"

    cached_data = cache.get(cache_key)

    if cached_data is not None:
        return cached_data

    now = timezone.now()

    today = now.date()

    week_start = today - timedelta(days=today.weekday())

    month_start = today.replace(day=1)

    # ------------------------------------------------
    # REVENUE
    # ------------------------------------------------

    paid_orders = PaymentOrder.objects.filter(
        status=PaymentOrder.STATUS_PAID
    )

    daily_revenue = (
        paid_orders
        .filter(paid_at__date=today)
        .aggregate(total=Sum("amount_paise"))
        ["total"]
        or 0
    )

    weekly_revenue = (
        paid_orders
        .filter(paid_at__date__gte=week_start)
        .aggregate(total=Sum("amount_paise"))
        ["total"]
        or 0
    )

    monthly_revenue = (
        paid_orders
        .filter(paid_at__date__gte=month_start)
        .aggregate(total=Sum("amount_paise"))
        ["total"]
        or 0
    )

    # Convert paise -> rupees
    daily_revenue = daily_revenue / 100
    weekly_revenue = weekly_revenue / 100
    monthly_revenue = monthly_revenue / 100

    # ------------------------------------------------
    # MOST POPULAR MOVIES
    # ------------------------------------------------

    popular_movies = list(
        Movie.objects
        .annotate(
            booking_count=Count("booking")
        )
        .order_by("-booking_count")[:10]
        .values(
            "id",
            "name",
            "booking_count",
        )
    )

    # ------------------------------------------------
    # BUSIEST THEATERS
    # ------------------------------------------------

    busiest_theaters = list(
        Theater.objects
        .annotate(
            total_seats=Count("seats", distinct=True),
            booked_seats=Count(
                "seats",
                filter=Q(seats__booking__isnull=False),
                distinct=True,
            ),
        )
        .annotate(
            occupancy_rate=ExpressionWrapper(
                F("booked_seats") * 100.0 / F("total_seats"),
                output_field=FloatField(),
            )
        )
        .order_by("-occupancy_rate")[:10]
        .values(
            "id",
            "name",
            "total_seats",
            "booked_seats",
            "occupancy_rate",
        )
    )

    # ------------------------------------------------
    # PEAK BOOKING HOURS
    # ------------------------------------------------

    peak_hours = list(
        Booking.objects
        .annotate(
            hour=ExtractHour("booked_at")
        )
        .values("hour")
        .annotate(
            booking_count=Count("id")
        )
        .order_by("-booking_count")
    )

    # ------------------------------------------------
    # CANCELLATION RATE
    # ------------------------------------------------

    total_orders = PaymentOrder.objects.count()

    cancelled_orders = PaymentOrder.objects.filter(
        status=PaymentOrder.STATUS_CANCELLED
    ).count()

    cancellation_rate = (
        (cancelled_orders / total_orders) * 100
        if total_orders > 0
        else 0
    )

    data = {
        "daily_revenue": daily_revenue,
        "weekly_revenue": weekly_revenue,
        "monthly_revenue": monthly_revenue,

        "popular_movies": popular_movies,

        "busiest_theaters": busiest_theaters,

        "peak_hours": peak_hours,

        "total_orders": total_orders,
        "cancelled_orders": cancelled_orders,
        "cancellation_rate": round(cancellation_rate, 2),
    }

    cache.set(
        cache_key,
        data,
        CACHE_TIMEOUT
    )

    return data
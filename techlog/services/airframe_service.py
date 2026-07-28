# techlog/services/airframe_service.py
"""
Reusable, session-cached data-fetching functions for airframe-related objects.
"""

from django.core.cache import cache
from techlog.api import TechlogClient
from techlog.mapping import from_api, from_api_many
from techlog.state import Airframe, AirframeDefect, Action, Company, FluidInstance, FlightFluid, CurrentFlight, Operator

CACHE_TIMEOUT = 60 * 15  # 15 minutes, tune as needed
client = TechlogClient()

def user_can_access_airframe(request, airframe_id):
    """
    Placeholder permission check.
    Once CrewAssignment exists, replace this with a real check, e.g.:
        return request.user.crew_assignments.filter(
            airframe_id=airframe_id, active=True
        ).exists()
    Returning False here should force a cache miss/refetch (and later, a 403).
    """
    return True


def _cache_key(request, airframe_id, name):
    session_key = request.session.session_key or "anon"
    return f"{session_key}:airframe:{airframe_id}:{name}"


def _get_cached_or_fetch(request, airframe_id, name, fetch_fn):
    if not user_can_access_airframe(request, airframe_id):
        # No access — don't serve stale/cached data.
        # Placeholder for now; later this can raise PermissionDenied instead.
        cache.delete(_cache_key(request, airframe_id, name))
        return fetch_fn()  # or raise, once permissions are real

    key = _cache_key(request, airframe_id, name)
    value = cache.get(key)
    if value is None:
        value = fetch_fn()
        cache.set(key, value, CACHE_TIMEOUT)
    return value

def get_airframe(request, airframe_id):
    return _get_cached_or_fetch(
        request, airframe_id, "airframe",
        lambda: from_api(Airframe, client.get(f"airframes/{airframe_id}/"))
    )

def get_current_flight(request, airframe_id):
    return _get_cached_or_fetch(
        request, airframe_id, "current_flight",
        lambda: from_api(CurrentFlight, client.get(f"airframes/{airframe_id}/current_flight/"))
    )


def get_airframe_defects(request, airframe_id):
    return _get_cached_or_fetch(
        request, airframe_id, "defects",
        lambda: from_api_many(AirframeDefect, client.get(f"airframes/{airframe_id}/defects/"))
    )


def get_defect_actions(request, airframe_id):
    return _get_cached_or_fetch(
        request, airframe_id, "actions",
        lambda: from_api_many(Action, client.get(f"airframes/{airframe_id}/actions/"))
    )


def get_fluid_tanks(request, airframe_id):
    return _get_cached_or_fetch(
        request, airframe_id, "fluid_tanks",
        lambda: from_api_many(FluidInstance, client.get(f"airframes/{airframe_id}/fluids/"))
    )


def get_departure_fluids(request, airframe_id):
    return _get_cached_or_fetch(
        request, airframe_id, "departure_fluids",
        lambda: from_api_many(FlightFluid, client.get(f"airframes/{airframe_id}/current_flight/fluids/0/"))
    )


def get_arrival_fluids(request, airframe_id):
    return _get_cached_or_fetch(
        request, airframe_id, "arrival_fluids",
        lambda: from_api_many(FlightFluid, client.get(f"airframes/{airframe_id}/current_flight/fluids/1/"))
    )


def invalidate_airframe_cache(request, airframe_id):
    """Call this whenever underlying data changes (e.g. after a POST/save),
    so the next GET refetches instead of serving stale cached data."""
    for name in ("airframe", "current_flight", "defects", "actions", "fluid_tanks", "departure_fluids", "arrival_fluids"):
        cache.delete(_cache_key(request, airframe_id, name))
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.models import Tenant

limiter = Limiter(key_func=get_remote_address)


TIER_LIMITS = {
    "DEVELOPER": "100/minute",
    "BUSINESS": "1000/minute",
    "ENTERPRISE": "10000/minute",
}


def get_limit_for_tenant(tenant: Tenant) -> str:
    return TIER_LIMITS.get(getattr(tenant, "tier", "DEVELOPER"), "100/minute")

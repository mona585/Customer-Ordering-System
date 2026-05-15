"""Role slug constants — single source of truth for RBAC slugs."""

ROLE_CUSTOMER = "customer"
ROLE_ADMIN = "admin"
ROLE_DELIVERY = "delivery"
ROLE_CHEF = "chef"

DEFAULT_ROLE_SLUGS = (ROLE_CUSTOMER, ROLE_ADMIN, ROLE_DELIVERY, ROLE_CHEF)

STAFF_ROLE_SLUGS = frozenset({ROLE_ADMIN, ROLE_DELIVERY, ROLE_CHEF})
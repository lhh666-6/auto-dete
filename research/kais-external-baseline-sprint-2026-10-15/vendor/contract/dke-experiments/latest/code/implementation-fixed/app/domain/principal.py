"""Prototype fact-admission role policy.

Authentication and session integrity are host responsibilities.  This
allow-list is the independent commit-time authorization recheck; it is not an
authentication mechanism or a security-isolation claim.
"""

from collections.abc import Mapping
from threading import RLock

FACT_ADMISSION_ROLE = "fact-admitter"


class PrincipalAuthorizationError(PermissionError):
    code = "PRINCIPAL_NOT_AUTHORIZED"


class PrincipalRolePolicy:
    """Thread-safe, revocable principal-to-role allow-list."""

    def __init__(self, assignments: Mapping[str, frozenset[str]]) -> None:
        self._assignments = {
            principal_id: set(roles) for principal_id, roles in assignments.items()
        }
        self._lock = RLock()

    def require(self, principal_id: object, role: str) -> None:
        with self._lock:
            allowed = (
                isinstance(principal_id, str)
                and bool(principal_id)
                and role in self._assignments.get(principal_id, set())
            )
        if not allowed:
            raise PrincipalAuthorizationError(f"principal is not authorized for role {role}")

    def revoke(self, principal_id: str, role: str) -> None:
        with self._lock:
            self._assignments.setdefault(principal_id, set()).discard(role)


def prototype_principal_policy(
    principal_ids: tuple[str, ...] = (
        "reviewer",
        "reviewer-1",
        "reviewer-2",
        "reviewer-a",
        "reviewer-b",
    ),
) -> PrincipalRolePolicy:
    """Return the explicit demo/test allow-list used by local repositories."""

    return PrincipalRolePolicy(
        {principal_id: frozenset({FACT_ADMISSION_ROLE}) for principal_id in principal_ids}
    )

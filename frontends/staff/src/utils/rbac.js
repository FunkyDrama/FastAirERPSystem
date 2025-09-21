import {ROLES} from "./roles";

export function hasAccess(userRole, rolesAllowed) {
    if (!userRole) return false;

    const role = String(userRole).toLowerCase();

    if (role === ROLES.SUPERVISOR) return true;

    if (!rolesAllowed) return true;

    const list = Array.isArray(rolesAllowed) ? rolesAllowed : [rolesAllowed];
    const normalized = list.map((r) => String(r).toLowerCase());

    return normalized.includes(role);
}

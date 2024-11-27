# app/utils/permissions.py
from typing import Dict, Set
from .enums import RoleEnum, ResourceEnum, PermissionEnum

ROLE_PERMISSIONS: Dict[RoleEnum, Dict[ResourceEnum, Set[PermissionEnum]]] = {
    RoleEnum.SUPER_ADMIN: {
        ResourceEnum.USERS: {
            PermissionEnum.CREATE,
            PermissionEnum.READ,
            PermissionEnum.UPDATE,
            PermissionEnum.DELETE,
            PermissionEnum.LIST
        },
        ResourceEnum.COMPANIES: {
            PermissionEnum.CREATE,
            PermissionEnum.READ,
            PermissionEnum.UPDATE,
            PermissionEnum.DELETE,
            PermissionEnum.LIST
        },
        ResourceEnum.SETTINGS: {
            PermissionEnum.CREATE,
            PermissionEnum.READ,
            PermissionEnum.UPDATE,
            PermissionEnum.DELETE
        },
        ResourceEnum.EMAILS: {
            PermissionEnum.CREATE,
            PermissionEnum.READ,
            PermissionEnum.UPDATE,
            PermissionEnum.DELETE,
            PermissionEnum.LIST
        },
        ResourceEnum.THREAT_ANALYSIS: {
            PermissionEnum.CREATE,
            PermissionEnum.READ,
            PermissionEnum.UPDATE,
            PermissionEnum.DELETE,
            PermissionEnum.LIST
        }
    },
    RoleEnum.COMPANY_ADMIN: {
        ResourceEnum.USERS: {
            PermissionEnum.CREATE,
            PermissionEnum.READ,
            PermissionEnum.UPDATE,
            PermissionEnum.LIST
        },
        ResourceEnum.COMPANIES: {
            PermissionEnum.READ,
            PermissionEnum.UPDATE
        },
        ResourceEnum.SETTINGS: {
            PermissionEnum.READ,
            PermissionEnum.UPDATE
        },
        ResourceEnum.EMAILS: {
            PermissionEnum.READ,
            PermissionEnum.UPDATE,
            PermissionEnum.LIST
        },
        ResourceEnum.THREAT_ANALYSIS: {
            PermissionEnum.READ,
            PermissionEnum.LIST
        }
    },
    RoleEnum.USER: {
        ResourceEnum.USERS: {
            PermissionEnum.READ,
            PermissionEnum.UPDATE
        },
        ResourceEnum.SETTINGS: {
            PermissionEnum.READ,
            PermissionEnum.UPDATE
        },
        ResourceEnum.EMAILS: {
            PermissionEnum.READ,
            PermissionEnum.LIST
        },
        ResourceEnum.THREAT_ANALYSIS: {
            PermissionEnum.READ
        }
    }
}

def get_default_permissions(role: RoleEnum) -> dict:
    """Convert enum-based permissions to dict format for database storage."""
    permissions = {}
    role_perms = ROLE_PERMISSIONS.get(role, {})
    
    for resource, perms in role_perms.items():
        permissions[resource.value] = [perm.value for perm in perms]
    
    return permissions
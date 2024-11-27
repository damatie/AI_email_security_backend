# app/utils/enums.py
from enum import Enum

class UserStatusEnum(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class RoleEnum(Enum):
    SUPER_ADMIN = "super_admin"
    COMPANY_ADMIN = "company_admin"
    USER = "user"

class ResourceEnum(Enum):
    USERS = "users"
    COMPANIES = "companies"
    SETTINGS = "settings"
    EMAILS = "emails"
    THREAT_ANALYSIS = "threat_analysis"

class PermissionEnum(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"

class EmailProviderEnum(str, Enum):
    """Enum for supported email providers"""
    GMAIL = "gmail"
    OUTLOOK = "outlook"

class ThreatTypeEnum(str, Enum):
    """Enum for different types of email threats"""
    PHISHING = "phishing"
    SPAM = "spam"
    MALWARE = "malware"
    SUSPICIOUS = "suspicious"
    CLEAN = "clean"


class ThreatSeverityEnum(str, Enum):
    """Enum for threat severity levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"
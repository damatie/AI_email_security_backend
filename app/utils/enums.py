from enum import Enum

class UserStatusEnum(Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"

class RoleEnum(Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    COMPANY_ADMIN = "COMPANY_ADMIN"
    COMPANY_MANAGER = "COMPANY_MANAGER"
    COMPANY_ANALYST = "COMPANY_ANALYST"
    COMPANY_USER = "COMPANY_USER"         
    SUPPORT_AGENT = "SUPPORT_AGENT"
    INDIVIDUAL_USER = "INDIVIDUAL_USER" 

class ResourceEnum(Enum):
    USERS = "USERS"
    COMPANIES = "COMPANIES"
    SETTINGS = "SETTINGS"
    EMAILS = "EMAILS"
    THREAT_ANALYSIS = "THREAT_ANALYSIS"
    INTEGRATIONS = "INTEGRATIONS"
    DASHBOARD = "DASHBOARD"

class UserTypeEnum(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"

class PermissionEnum(Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LIST = "LIST"
    MANAGE = "MANAGE"
    EXECUTE = "EXECUTE"


class PlanTypeEnum(str, Enum):
    INDIVIDUAL_PLAN = "INDIVIDUAL_PLAN"
    COMPANY_PLAN = "COMPANY_PLAN"

class EmailProviderEnum(str, Enum):
    GMAIL = "GMAIL"
    OUTLOOK = "OUTLOOK"
    YAHOO = "YAHOO"
    EXCHANGE = "EXCHANGE"
    IMAP = "IMAP"

class ThreatTypeEnum(str, Enum):
    PHISHING = "PHISHING"
    SPAM = "SPAM"
    MALWARE = "MALWARE"
    SUSPICIOUS = "SUSPICIOUS"
    CLEAN = "CLEAN"
    BEC = "BEC"
    IMPERSONATION = "IMPERSONATION"

class ThreatSeverityEnum(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"

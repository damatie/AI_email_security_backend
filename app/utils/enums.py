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
    MALICIOUS = "MALICIOUS"
    SUSPICIOUS = "SUSPICIOUS"
    SAFE = "SAFE"
    BEC = "BEC"
    IMPERSONATION = "IMPERSONATION"

class ThreatSeverityEnum(str, Enum):
    HIGH = "HIGH"
    MEDIUM_HIGH= "MEDIUM-HIGH"
    MEDIUM = "MEDIUM"
    MEDIUM_LOW = "MEDIUM-LOW"
    LOW = "LOW"
    NONE = "NONE"
class ConfidenceLevelEnum(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class RiskLevelEnum(str, Enum):
    HIGH_RISK = "HIGH RISK"
    MEDIUM_RISK = "MEDIUM RISK"
    LOW_RISK = "LOW RISK"

class ProductNameEnum(str, Enum):
    EMAIL_SECURITY_SUITE="Email Security Suite"

class ServiceStatusEnum(str, Enum):
    UNAVAILABLE = "UNAVAILABLE"
    COMING_SOON = "COMING_SOON"
    AVAILABLE = "AVAILABLE"
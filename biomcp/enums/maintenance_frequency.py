from enum import StrEnum


class MaintenanceFrequency(StrEnum):
    ANNUALLY = "annually"
    AS_NEEDED = "asNeeded"
    BIANNUALLY = "biannually"
    CONTINUALLY = "continually"
    DAILY = "daily"
    IRREGULAR = "irregular"
    MONTHLY = "monthly"
    NOT_PLANNED = "notPlanned"
    OTHER_MAINTENANCE_PERIOD = "otherMaintenancePeriod"
    UNKNOWN = "unknown"
    UNKOWN = "unkown"
    WEEKLY = "weekly"
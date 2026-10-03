# core/models.py
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path

class ExecutionMode(Enum):
    REPAIR_ONLY = 1
    REPAIR_CLONE_ADAPT = 2

class ErrorClassification(Enum):
    AUTO_SAFE = "AUTO_SAFE"
    AUTO_ADAPT = "AUTO_ADAPT"
    REQUIRES_PORT = "REQUIRES_PORT"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    UNKNOWN = "UNKNOWN"

class DuplicateType(Enum):
    EXACT_DUPLICATE = "EXACT_DUPLICATE"
    FUNCTIONAL_DUPLICATE = "FUNCTIONAL_DUPLICATE"
    PARTIAL_DUPLICATE = "PARTIAL_DUPLICATE"
    RELATED = "RELATED"
    MISSING = "MISSING"

class ExecutionStatus(Enum):
    SUCCESS = "SUCCESS"
    SUCCESS_WITH_REVIEW = "SUCCESS_WITH_REVIEW"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"
    INFRASTRUCTURE_FAILURE = "INFRASTRUCTURE_FAILURE"

@dataclass
class DiagnosticItem:
    code: str
    message: str
    file_path: str
    line: int
    column: int
    severity: str = "error"
    classification: ErrorClassification = ErrorClassification.UNKNOWN

@dataclass
class PatchRecord:
    file_path: str
    operation: str
    reason: str
    source: str
    before_content: str
    after_content: str
    dependencies: List[str] = field(default_factory=list)
    confidence: float = 1.0
    validation: str = "pending"

@dataclass
class ProvenanceRecord:
    source_repo: str
    source_commit: str
    source_path: str
    source_symbol: str
    target_path: str
    target_symbol: str
    operation: str
    adaptation_details: str
    dependencies: List[str]
    validated: bool

@dataclass
class FailedAdaptation:
    file_path: str
    source_path: str
    target_path: str
    operation: str
    problem: str
    failed_code: str
    target_context: str
    expected_adaptation: str
    reason: str
    status: str = "REQUIRES_MANUAL_REVIEW"

@dataclass
class ResourceResolutionRecord:
    file_path: str
    original_reference: str
    search_strategy: str
    result: str
    actual_path: Optional[str]
    action_taken: str
    annotation: Optional[str] = None

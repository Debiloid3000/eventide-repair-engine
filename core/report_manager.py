# core/report_manager.py
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from core.models import (
    ExecutionMode, ExecutionStatus, FailedAdaptation, 
    ResourceResolutionRecord, ProvenanceRecord
)

class ReportManager:
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = int(time.time())

    def generate_all_reports(
        self,
        mode: ExecutionMode,
        status: ExecutionStatus,
        initial_errors: int,
        fixed_errors: int,
        remaining_errors: int,
        failed_adaptations: List[FailedAdaptation],
        resource_records: List[ResourceResolutionRecord],
        provenance_records: List[ProvenanceRecord]
    ) -> Dict[str, Path]:
        
        generated = {}
        
        # 1. Summary Markdown
        summary_md_path = self.reports_dir / f"repair_summary_{self.timestamp}.md"
        summary_md_content = f"""# EVENTIDE REPAIR ENGINE SUMMARY

- **Execution Mode**: {mode.name}
- **Status**: {status.value}
- **Timestamp**: {self.timestamp}

## Build & Diagnostic Statistics
- **Initial Diagnostics**: {initial_errors}
- **Fixed Diagnostics**: {fixed_errors}
- **Remaining Diagnostics**: {remaining_errors}

## Features & Adaptations
- **Ported Items**: {len(provenance_records)}
- **Failed Adaptations**: {len(failed_adaptations)}
- **Resource Lookups**: {len(resource_records)}
"""
        summary_md_path.write_text(summary_md_content, encoding="utf-8")
        generated["summary_md"] = summary_md_path

        # 2. Failed Adaptations MD
        failed_md_path = self.reports_dir / f"failed_adaptations_{self.timestamp}.md"
        failed_lines = ["# FAILED ADAPTATIONS REPORT\n"]
        for fa in failed_adaptations:
            failed_lines.append(f"""### FILE: `{fa.file_path}`
- **SOURCE**: `{fa.source_path}`
- **TARGET**: `{fa.target_path}`
- **OPERATION**: `{fa.operation}`
- **PROBLEM**: `{fa.problem}`
- **REASON**: {fa.reason}

```csharp
// FAILED CODE / CONTEXT
{fa.failed_code}

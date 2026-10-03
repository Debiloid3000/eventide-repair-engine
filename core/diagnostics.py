import re
from typing import List
from core.models import DiagnosticItem, ErrorClassification

class DiagnosticParser:
    DIAG_REGEX = re.compile(
        r'^(?P<file>[^(]+)\((?P<line>\d+),(?P<col>\d+)\):\s+(?P<sev>error|warning)\s+(?P<code>CS\d+):\s+(?P<msg>.*)$'
    )

    def parse_output(self, build_stdout: str) -> List[DiagnosticItem]:
        diagnostics = []
        for line in build_stdout.splitlines():
            m = self.DIAG_REGEX.match(line.strip())
            if m:
                item = DiagnosticItem(
                    code=m.group("code"), message=m.group("msg"), file_path=m.group("file").strip(),
                    line=int(m.group("line")), column=int(m.group("col")), severity=m.group("sev"),
                    classification=self._classify(m.group("code"), m.group("msg"))
                )
                diagnostics.append(item)
        return diagnostics

    def _classify(self, code: str, msg: str) -> ErrorClassification:
        if code in ("CS0246", "CS0234"): return ErrorClassification.AUTO_SAFE
        if code in ("CS0103", "CS0117", "CS1061"): return ErrorClassification.AUTO_ADAPT
        if code in ("CS0115", "CS1501", "CS1503", "CS1729"): return ErrorClassification.AUTO_ADAPT
        return ErrorClassification.MANUAL_REVIEW

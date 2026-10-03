from typing import Tuple

class AdaptationEngine:
    def adapt_code(self, source_code: str, file_path: str) -> Tuple[str, bool, str]:
        adapted = source_code
        adapted = adapted.replace("IEntity ", "EntityUid ")
        if "ObsoleteGenesisMethod" in adapted:
            return adapted, False, "Found obsolete method that requires manual reimplementation."
        return adapted, True, "Auto-adapted successfully"

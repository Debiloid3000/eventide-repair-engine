# core/config.py
import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path

@dataclass
class EngineConfig:
    mode: int = 1
    target_dir: str = "."
    max_iterations: int = 10
    dry_run: bool = False
    configuration: str = "Debug"
    
    repositories: Dict[str, str] = field(default_factory=lambda: {
        "upstream": "https://github.com/space-syndicate/space-station-14.git",
        "genesis": "https://github.com/BrigChill3000/genesis-station-14.git",
        "sunrise": "https://github.com/makura-games/sunrise-station.git",
        "deadspace": "https://github.com/dead-space-server/dead-space-14.git",
        "goob": "https://github.com/space-syndicate/Goob-Station.git"
    })
    
    reference_policy: Dict[str, bool] = field(default_factory=lambda: {
        "use_additional_sources_only_when_compatible": True,
        "do_not_force_reference_code": True
    })
    
    genesis: Dict[str, bool] = field(default_factory=lambda: {
        "enabled": True,
        "primary_port_source": True,
        "selective_port": True,
        "adaptation": True
    })
    
    resources: Dict[str, bool] = field(default_factory=lambda: {
        "textures_read_only": True,
        "recursive_rsi_search": True,
        "legacy_genesis_paths": True
    })
    
    safety: Dict[str, bool] = field(default_factory=lambda: {
        "preserve_user_changes": True,
        "destructive_git_operations": False,
        "automatic_rollback": True
    })

    @classmethod
    def load_from_file(cls, path: str) -> "EngineConfig":
        p = Path(path)
        if not p.exists():
            return cls()
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        cfg = cls()
        for k, v in data.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)
        return cfg

# core/resource_resolver.py
import os
import re
from pathlib import Path
from typing import Optional, List, Tuple
from core.models import ResourceResolutionRecord

class ResourceReferenceResolver:
    """
    Решает ссылки на .rsi, текстуры и звуки.
    Реализует СТРОГОЕ правило: Resources/Textures = READ ONLY.
    Никогда не создает, не удаляет, не перемещает и не перезаписывает файлы в Textures.
    """
    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir).resolve()
        self.resources_dir = self.target_dir / "Resources"
        self.textures_dir = self.resources_dir / "Textures"
        self.legacy_hardsuit_dir = self.textures_dir / "_Genesis" / "Clothing" / "Head" / "Hardsuits"

    def resolve_rsi_reference(self, file_path: Path, raw_reference: str) -> ResourceResolutionRecord:
        clean_ref = raw_reference.strip('"\' ')
        filename = Path(clean_ref).name

        # 1. Проверка точного совпадения относительно Resources
        direct_path = self.resources_dir / clean_ref
        if direct_path.exists():
            return ResourceResolutionRecord(
                file_path=str(file_path),
                original_reference=raw_reference,
                search_strategy="EXACT_DIRECT_MATCH",
                result="EXISTS",
                actual_path=clean_ref,
                action_taken="PRESERVED"
            )

        # 2. Рекурсивный поиск по имени файла во всех допустимых директориях Resources
        found_path = self._recursive_find_rsi(filename)
        if found_path:
            # Вычисляем путь относительно Resources/
            rel_path = found_path.relative_to(self.resources_dir).as_posix()
            return ResourceResolutionRecord(
                file_path=str(file_path),
                original_reference=raw_reference,
                search_strategy="RECURSIVE_RSI_SEARCH",
                result="FOUND_RELOCATED",
                actual_path=rel_path,
                action_taken="UPDATED_PROTOTYPE_REFERENCE"
            )

        # 3. Если не найден — проставляем аннотацию без создания и копирования файлов
        return ResourceResolutionRecord(
            file_path=str(file_path),
            original_reference=raw_reference,
            search_strategy="RECURSIVE_RSI_SEARCH",
            result="NOT_FOUND",
            actual_path=None,
            action_taken="PRESERVED_WITH_ANNOTATION",
            annotation="# Нету текстуры!"
        )

    def _recursive_find_rsi(self, filename: str) -> Optional[Path]:
        if not self.resources_dir.exists():
            return None
        
        for root, dirs, files in os.walk(self.resources_dir):
            if filename in dirs or filename in files:
                candidate = Path(root) / filename
                if candidate.name == filename:
                    return candidate
        return None

    def fix_prototype_file_resources(self, prototype_path: Path) -> List[ResourceResolutionRecord]:
        if not prototype_path.exists():
            return []

        content = prototype_path.read_text(encoding="utf-8")
        records = []
        
        # Находим ссылки на RSI в YAML
        rsi_matches = re.findall(r'sprite:\s*["\']?([^"\'\n]+\.rsi)["\']?', content)
        
        new_content = content
        for rsi_ref in set(rsi_matches):
            rec = self.resolve_rsi_reference(prototype_path, rsi_ref)
            records.append(rec)
            
            if rec.result == "FOUND_RELOCATED" and rec.actual_path:
                new_content = new_content.replace(rsi_ref, rec.actual_path)
            elif rec.result == "NOT_FOUND" and rec.annotation:
                # Добавляем комментарий на следующей строке без разрушения структуры YAML
                pattern = f'(sprite:\\s*["\']?{re.escape(rsi_ref)}["\']?)'
                replacement = f'\\1  {rec.annotation}'
                new_content = re.sub(pattern, replacement, new_content)

        if new_content != content:
            prototype_path.write_text(new_content, encoding="utf-8")

        return records

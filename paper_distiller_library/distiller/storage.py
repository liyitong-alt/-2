import json
from pathlib import Path
from typing import Any, Dict


class StorageManager:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def paper_dir(self, paper_id: str) -> Path:
        return self.base_dir / paper_id

    def ensure_paper_dir(self, paper_id: str) -> Path:
        path = self.paper_dir(paper_id)
        path.mkdir(parents=True, exist_ok=True)
        (path / "exports").mkdir(exist_ok=True)
        return path

    def save_pdf(self, paper_id: str, filename: str, content: bytes) -> Path:
        paper_dir = self.ensure_paper_dir(paper_id)
        pdf_path = paper_dir / filename
        pdf_path.write_bytes(content)
        return pdf_path

    def save_json(self, paper_id: str, name: str, payload: Dict[str, Any]) -> Path:
        path = self.ensure_paper_dir(paper_id) / name
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def load_json(self, paper_id: str, name: str) -> Dict[str, Any]:
        path = self.paper_dir(paper_id) / name
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def export_path(self, paper_id: str, filename: str) -> Path:
        return self.ensure_paper_dir(paper_id) / "exports" / filename

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


class InteractionStore:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.interactions_dir = self.base_dir / "interactions"
        self.runs_dir = self.base_dir / "runs"
        self.interactions_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def save_interaction(self, payload: dict) -> Path:
        record = dict(payload)
        record.setdefault("interaction_id", uuid.uuid4().hex)
        record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

        scope_id = record.get("scope_id") or "global"
        timestamp_slug = record["timestamp"].replace(":", "-")
        file_path = self.interactions_dir / f"{scope_id}_{timestamp_slug}_{record['interaction_id']}.json"

        with open(file_path, "w", encoding="utf-8") as handle:
            json.dump(record, handle, ensure_ascii=False, indent=2)

        return file_path

    def load_interactions(self, scope_id: str | None = None, only_unevaluated: bool = False) -> list[dict]:
        records = []
        for path in sorted(self.interactions_dir.glob("*.json")):
            with open(path, "r", encoding="utf-8") as handle:
                record = json.load(handle)
            if scope_id and record.get("scope_id") != scope_id:
                continue
            if only_unevaluated and record.get("evaluated"):
                continue
            records.append(record)
        return records

    def mark_evaluated(self, interaction_ids: list[str]) -> None:
        """Write evaluated=True back to each interaction file."""
        id_set = set(interaction_ids)
        for path in self.interactions_dir.glob("*.json"):
            with open(path, "r", encoding="utf-8") as handle:
                record = json.load(handle)
            if record.get("interaction_id") in id_set:
                record["evaluated"] = True
                with open(path, "w", encoding="utf-8") as handle:
                    json.dump(record, handle, ensure_ascii=False, indent=2)

    def load_run_history(self) -> list[dict]:
        """Return all past evaluation summaries, newest first."""
        summaries = []
        for summary_path in sorted(self.runs_dir.glob("*/summary.json"), reverse=True):
            try:
                with open(summary_path, "r", encoding="utf-8") as handle:
                    summaries.append(json.load(handle))
            except Exception:
                continue
        return summaries

    def create_run_dir(self, scope_id: str | None = None) -> Path:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        run_name = f"{timestamp}_{scope_id or 'all'}"
        run_dir = self.runs_dir / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir
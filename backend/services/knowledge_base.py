import json
import os
from typing import Optional


class StandardKnowledgeBase:
    def __init__(self, kb_path: str):
        self.kb_path = kb_path
        self.data = {}
        self._index = {}
        if os.path.exists(kb_path):
            with open(kb_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            self._build_index()

    def _build_index(self):
        for category in self.data.get("defects", []):
            code = category.get("code", "")
            if code:
                self._index[code] = category

    def query_by_category(self, defect_code: str) -> dict:
        defect_code = defect_code.upper()
        return self._index.get(defect_code, {"error": f"未找到缺陷代码: {defect_code}"})

    def query_by_grade(self, defect_code: str, grade: int) -> dict:
        defect_code = defect_code.upper()
        category = self._index.get(defect_code)
        if not category:
            return {"error": f"未找到缺陷代码: {defect_code}"}
        for g in category.get("grades", []):
            if g.get("level") == grade:
                return {
                    "code": defect_code,
                    "name": category.get("name", ""),
                    "grade": g,
                }
        return {"error": f"未找到 {defect_code} 的 {grade} 级定义"}

    def search(self, keyword: str) -> list:
        results = []
        keyword_lower = keyword.lower()
        for code, category in self._index.items():
            name = category.get("name", "")
            desc = category.get("description", "")
            if keyword_lower in name or keyword_lower in desc or keyword_lower in code.lower():
                results.append(category)
            for g in category.get("grades", []):
                if keyword_lower in g.get("criteria", "").lower():
                    results.append({"code": code, "name": name, "grade": g})
        return results

    def list_all_codes(self) -> list:
        return [
            {"code": c.get("code"), "name": c.get("name"), "type": c.get("type")}
            for c in self.data.get("defects", [])
        ]

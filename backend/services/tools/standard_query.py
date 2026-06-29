import json
from services.tools.base import BaseTool


class StandardQueryTool(BaseTool):
    name = "query_standard"
    description = (
        "查询CJJ 181-2012标准中的缺陷定义、等级判据和修复建议。"
        "当需要确认某类缺陷的等级划分标准，或需要了解某等级对应的修复方法时使用此工具。"
    )

    def __init__(self, kb):
        self.kb = kb

    def get_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "defect_code": {
                            "type": "string",
                            "description": "缺陷类别代码: PL(破裂)/CK(错口)/SG(树根)/SL(渗漏)/TL(脱落)/ZW(障碍物)",
                        },
                        "grade": {
                            "type": "integer",
                            "description": "查询指定等级(1-4)。不提供则返回全部等级定义。",
                            "minimum": 1,
                            "maximum": 4,
                        },
                    },
                    "required": ["defect_code"],
                },
            },
        }

    def validate_params(self, params):
        if "defect_code" not in params:
            return {"valid": False, "error": "缺少 defect_code"}
        valid = [
            "PL", "CK", "SG", "SL", "TL", "ZW",
            "BX", "FS", "QF", "TJ", "AJ", "CR", "CJ", "JG", "CQ", "FZ",
        ]
        if params["defect_code"].upper() not in valid:
            return {"valid": False, "error": f"无效代码 '{params['defect_code']}'"}
        return {"valid": True, "error": None}

    def execute(self, defect_code: str, grade: int = None) -> str:
        defect_code = defect_code.upper()
        if grade:
            result = self.kb.query_by_grade(defect_code, grade)
        else:
            result = self.kb.query_by_category(defect_code)
        return json.dumps(result, ensure_ascii=False, indent=2)

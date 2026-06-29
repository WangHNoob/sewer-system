import json
from services.tools.base import BaseTool


class ReportGenerationTool(BaseTool):
    name = "generate_report"
    description = "基于评估结果生成Word格式的结构化评估报告。在完成评估后调用此工具。"

    def get_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "assessment_results": {"type": "string", "description": "评估结果JSON字符串"},
                        "image_path": {"type": "string", "description": "原始CCTV图像路径"},
                        "output_path": {"type": "string", "description": "报告输出路径(.docx)"},
                    },
                    "required": ["assessment_results", "output_path"],
                },
            },
        }

    def validate_params(self, params):
        for key in ["assessment_results", "output_path"]:
            if key not in params:
                return {"valid": False, "error": f"缺少 {key}"}
        return {"valid": True, "error": None}

    def execute(self, assessment_results: str, output_path: str, image_path: str = None) -> str:
        from services.report_generator import SingleReportGenerator

        gen = SingleReportGenerator()
        gen.generate(json.loads(assessment_results), output_path, image_path)
        return f"报告已生成: {output_path}"

import json
from pathlib import Path
from services.tools.base import BaseTool


class ImageAssessmentTool(BaseTool):
    name = "assess_image"
    description = (
        "对排水管道CCTV图像进行缺陷评估。接收检测结果，执行先验转换，调用多模态大模型评估缺陷等级。"
    )

    def get_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_path": {"type": "string", "description": "CCTV图像文件路径"},
                        "detection_json": {"type": "string", "description": "检测模型JSON结果字符串"},
                    },
                    "required": ["image_path", "detection_json"],
                },
            },
        }

    def validate_params(self, params):
        if "image_path" not in params:
            return {"valid": False, "error": "缺少 image_path"}
        if not Path(params["image_path"]).exists():
            return {"valid": False, "error": f"文件不存在: {params['image_path']}"}
        if "detection_json" not in params:
            return {"valid": False, "error": "缺少 detection_json"}
        try:
            json.loads(params["detection_json"])
        except Exception:
            return {"valid": False, "error": "detection_json 格式错误"}
        return {"valid": True, "error": None}

    def execute(self, image_path: str, detection_json: str) -> str:
        from services.prior_converter import StructuredPriorConverter
        from services.llm_provider import LLMProvider
        from services.prompts import SYSTEM_PROMPT, BATCH_EVALUATION_PROMPT

        detection = json.loads(detection_json)
        prior = StructuredPriorConverter().convert(detection)
        prompt = BATCH_EVALUATION_PROMPT.format(prior=prior)

        return LLMProvider().chat_with_image(SYSTEM_PROMPT, prompt, image_path=image_path)

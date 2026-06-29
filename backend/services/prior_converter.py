class StructuredPriorConverter:
    EVAL_CONFIDENCE_THRESHOLD = 0.85

    def convert(self, detection_result: dict) -> str:
        detections = detection_result["detections"]

        if not detections:
            return (
                "检测模型未在该图像中检测到任何缺陷（置信度阈值0.5以上）。"
                "请注意：可能存在漏检情况，请对全图进行补充分析。"
            )

        high_conf = [
            d for d in detections if d["confidence"] >= self.EVAL_CONFIDENCE_THRESHOLD
        ]
        low_conf = [
            d for d in detections if d["confidence"] < self.EVAL_CONFIDENCE_THRESHOLD
        ]

        lines = []
        if high_conf:
            lines.append("以下为高置信度检测结果（可作为可靠先验）：")
            for d in high_conf:
                b = d["bbox_pixels"]
                lines.append(
                    f"检测发现：图像中检测到{d['class_name']}缺陷，"
                    f"位置位于图像坐标[{b['x1']}, {b['y1']}]到[{b['x2']}, {b['y2']}]区域，"
                    f"位于{d['position_description']}，"
                    f"检测置信度{d['confidence']*100:.0f}%。"
                )

        if low_conf:
            lines.append("\n以下为低置信度检测结果（仅供参考，请审慎对待）：")
            for d in low_conf:
                b = d["bbox_pixels"]
                lines.append(
                    f"疑似{d['class_name']}缺陷，"
                    f"位置[{b['x1']}, {b['y1']}]到[{b['x2']}, {b['y2']}]，"
                    f"置信度{d['confidence']*100:.0f}%，请结合图像全局信息审慎判断。"
                )

        return "\n".join(lines)

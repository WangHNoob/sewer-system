import os
import io
import logging
from PIL import Image


class PipelineDefectDetector:
    CLASS_MAP = {
        0: {"code": "PL", "name": "破裂"},
        1: {"code": "CK", "name": "错口"},
        2: {"code": "SG", "name": "树根"},
        3: {"code": "SL", "name": "渗漏"},
        4: {"code": "TL", "name": "脱落"},
        5: {"code": "ZW", "name": "障碍物"},
    }

    CONFIDENCE_THRESHOLD = 0.5

    def __init__(self, model_path: str, device: str = "cuda:0"):
        self.device = device
        self.model = None
        self.model_loaded = False

        if os.path.exists(model_path):
            from ultralytics import YOLO

            self.model = YOLO(model_path)
            self.model_loaded = True
        else:
            logging.warning(
                f"检测模型文件不存在: {model_path}，检测功能将不可用。"
                f"请将训练好的模型放入该路径。"
            )

    def _empty_result(self, img: Image.Image) -> dict:
        orig_w, orig_h = img.size
        return {
            "detections": [],
            "image_size": {"width": orig_w, "height": orig_h},
            "total_defects": 0,
        }

    def detect_from_bytes(self, image_bytes: bytes, img_size: int = 640) -> dict:
        img = Image.open(io.BytesIO(image_bytes))
        if not self.model_loaded:
            return self._empty_result(img)
        return self._run_detect(img, img_size)

    def detect_from_path(self, image_path: str, img_size: int = 640) -> dict:
        img = Image.open(image_path)
        if not self.model_loaded:
            return self._empty_result(img)
        return self._run_detect(img, img_size)

    def detect_batch(self, image_paths: list, img_size: int = 640) -> list:
        images = [Image.open(p) for p in image_paths]
        if not self.model_loaded:
            return [self._empty_result(img) for img in images]
        results_list = self.model.predict(
            source=[img for img in images],
            imgsz=img_size,
            conf=self.CONFIDENCE_THRESHOLD,
            device=self.device,
            half=True,
            verbose=False,
        )
        return [self._parse_single(r, img) for r, img in zip(results_list, images)]

    def _run_detect(self, img: Image.Image, img_size: int) -> dict:
        results = self.model.predict(
            source=img,
            imgsz=img_size,
            conf=self.CONFIDENCE_THRESHOLD,
            device=self.device,
            half=True,
            verbose=False,
        )
        return self._parse_single(results[0], img)

    def _parse_single(self, result, img: Image.Image) -> dict:
        orig_w, orig_h = img.size
        detections = []

        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                xywhn = box.xywhn[0].tolist()
                xyxy = box.xyxy[0].tolist()
                cls_info = self.CLASS_MAP.get(cls_id, {"code": "UNK", "name": "未知"})

                detections.append({
                    "class_code": cls_info["code"],
                    "class_name": cls_info["name"],
                    "bbox": {
                        "x_center": round(xywhn[0], 4),
                        "y_center": round(xywhn[1], 4),
                        "width": round(xywhn[2], 4),
                        "height": round(xywhn[3], 4),
                    },
                    "bbox_pixels": {
                        "x1": int(xyxy[0]),
                        "y1": int(xyxy[1]),
                        "x2": int(xyxy[2]),
                        "y2": int(xyxy[3]),
                    },
                    "confidence": round(conf, 4),
                    "position_description": self._describe_position(xywhn),
                })

        detections.sort(key=lambda d: d["confidence"], reverse=True)
        return {
            "detections": detections,
            "image_size": {"width": orig_w, "height": orig_h},
            "total_defects": len(detections),
        }

    @staticmethod
    def _describe_position(xywhn):
        xc, yc = xywhn[0], xywhn[1]
        h = "左侧" if xc < 0.33 else ("右侧" if xc > 0.67 else "中部")
        v = "上部" if yc < 0.33 else ("下部" if yc > 0.67 else "中部")
        return f"图像{v}{h}区域"

    def close(self):
        if self.model is not None:
            del self.model

import os
from services.prompts import SYSTEM_PROMPT, BATCH_EVALUATION_PROMPT


class BatchEngine:
    def __init__(self, task_id: str, llm_provider: str = "cloud"):
        self.task_id = task_id
        self.llm_provider = llm_provider

    async def run(self):
        from services.detector import PipelineDefectDetector
        from services.prior_converter import StructuredPriorConverter
        from services.llm_provider import LLMProvider
        from services.report_generator import BatchReportGenerator
        from routers.batch import batch_tasks

        task = batch_tasks[self.task_id]
        task.status = "detecting"

        detector = PipelineDefectDetector(model_path="models/detector/best.pt")
        all_detections = detector.detect_batch(task.image_paths)

        task.status = "evaluating"
        converter = StructuredPriorConverter()
        llm = LLMProvider()

        all_assessments = []

        for i, (image_path, detection) in enumerate(
            zip(task.image_paths, all_detections)
        ):
            task.current_image = os.path.basename(image_path)
            task.processed = i

            try:
                prior_text = converter.convert(detection)
                eval_prompt = BATCH_EVALUATION_PROMPT.format(prior=prior_text)

                assessment_text = llm.chat_with_image(
                    system_prompt=SYSTEM_PROMPT,
                    user_text=eval_prompt,
                    image_path=image_path,
                )

                all_assessments.append({
                    "image_path": image_path,
                    "image_name": os.path.basename(image_path),
                    "detection": detection,
                    "assessment_text": assessment_text,
                    "status": "success",
                })
            except Exception as e:
                task.errors.append({
                    "image": os.path.basename(image_path),
                    "error": str(e),
                })
                all_assessments.append({
                    "image_path": image_path,
                    "image_name": os.path.basename(image_path),
                    "detection": detection,
                    "assessment_text": None,
                    "status": "error",
                    "error": str(e),
                })

        task.status = "generating_report"
        generator = BatchReportGenerator()
        report_path = os.path.join(
            "outputs/reports", f"batch_report_{self.task_id}.docx"
        )
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        generator.generate(all_assessments=all_assessments, output_path=report_path)

        task.status = "completed"
        task.report_path = report_path
        task.processed = task.total_images

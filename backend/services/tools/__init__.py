from services.tools.standard_query import StandardQueryTool
from services.tools.image_assessment import ImageAssessmentTool
from services.tools.report_generation import ReportGenerationTool
from services.knowledge_base import StandardKnowledgeBase


def get_all_tools():
    kb = StandardKnowledgeBase("data/knowledge_base/cjj181_2012.json")
    return [
        StandardQueryTool(kb),
        ImageAssessmentTool(),
        ReportGenerationTool(),
    ]

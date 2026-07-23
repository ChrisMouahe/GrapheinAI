"""MultiChartPipelineAgent orchestrating parallel sub-chart extractions and cross-chart fusion."""

from concurrent.futures import ThreadPoolExecutor
import logging
from pathlib import Path
from typing import Any

from src.agents.pipeline_agent import PipelineAgent
from src.agents.multi_chart_fusion import MultiChartFusionEngine
from src.models.chart import PipelineResult
from src.models.multi_chart import MultiChartPipelineResult
from src.models.user import UserProfile
from src.utils.multi_chart_detector import MultiChartDetector

logger = logging.getLogger("MultiChartPipelineAgent")


class MultiChartPipelineAgent:
    """Agent running multi-chart detection, parallel independent extraction, and cross-chart fusion."""

    def __init__(self, pipeline_agent: PipelineAgent | None = None) -> None:
        self.detector = MultiChartDetector()
        self.pipeline_agent = pipeline_agent or PipelineAgent()
        self.fusion_engine = MultiChartFusionEngine()

    def process_multi_chart_document(
        self,
        image_path: Path | str,
        question: str = "Analyser l'ensemble des graphiques",
        session_id: str = "multi_chart_session",
        target_language: str = "fr",
        user_profile: UserProfile | None = None,
    ) -> MultiChartPipelineResult:
        """Processes a multi-chart image, running parallel extractions per sub-chart and performing cross-chart fusion.

        Args:
            image_path: Path to image containing 1 or more charts.
            question: Target user prompt question.
            session_id: Active session identifier.
            target_language: Target language ("fr" or "en").
            user_profile: UserProfile for personalization.

        Returns:
            MultiChartPipelineResult model containing individual chart analyses and global briefing.
        """
        img_p = Path(image_path)
        logger.info(f"MultiChartPipelineAgent starting multi-chart processing for '{img_p.name}' [session={session_id}]")

        # 1. Detect and segment sub-charts
        detection = self.detector.detect_charts(img_p)
        logger.info(f"MultiChartDetector identified {detection.total_charts_detected} charts.")

        individual_results: dict[str, PipelineResult] = {}

        # 2. Execute parallel extractions per sub-chart
        def _process_single_chart(det_chart) -> tuple[str, PipelineResult | None]:
            try:
                crop_path = Path(det_chart.cropped_image_path) if det_chart.cropped_image_path else img_p
                res = self.pipeline_agent.answer(
                    image=crop_path,
                    question=question,
                    session_id=f"{session_id}_{det_chart.chart_id}",
                    target_language=target_language,
                    user_profile=user_profile,
                )
                return det_chart.chart_id, res
            except Exception as ex:
                logger.error(f"Fault-tolerant exception on sub-chart '{det_chart.chart_id}': {ex}")
                return det_chart.chart_id, None

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(_process_single_chart, chart) for chart in detection.detected_charts]
            for f in futures:
                cid, res = f.result()
                if res is not None:
                    individual_results[cid] = res

        # Fallback if all sub-chart extractions failed
        if not individual_results:
            fallback_res = self.pipeline_agent.answer(
                image=img_p,
                question=question,
                session_id=session_id,
                target_language=target_language,
                user_profile=user_profile,
            )
            individual_results["chart_1"] = fallback_res

        # 3. Perform Cross-Chart Fusion & Comparative Analysis
        comparisons, global_summary, global_recs = self.fusion_engine.fuse_multi_chart_results(
            detection_result=detection,
            individual_results=individual_results,
            user_profile=user_profile,
            target_language=target_language,
        )

        return MultiChartPipelineResult(
            session_id=session_id,
            detection_result=detection,
            individual_results=individual_results,
            cross_chart_comparisons=comparisons,
            global_summary=global_summary,
            global_recommendations=global_recs,
        )

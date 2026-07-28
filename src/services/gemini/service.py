"""GeminiService implementing BaseAIService with Single Extraction Strategy, SHA256 Caching, Quota Tracking, and Exponential Backoff."""

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any
from PIL import Image

from src.services.gemini.base import BaseAIService, FullChartExtraction, SeriesData
from src.services.gemini.cache import ChartCacheManager
from src.services.gemini.prompts import (
    CHAR_EXTRACTION_SYSTEM_PROMPT,
    INTERPRETATION_PROMPT_TEMPLATE,
    QA_PROMPT_TEMPLATE,
    RECOMMENDATION_PROMPT_TEMPLATE,
)
from src.services.gemini.quota import GeminiQuotaManager
from src.services.gemini.retry import exponential_backoff_retry
from src.services.gemini.router import QuestionRouter, RouteTarget

try:
    from google import genai
    from google.genai import types
    HAVE_GENAI_SDK = True
except ImportError:
    genai = None
    types = None
    HAVE_GENAI_SDK = False

logger = logging.getLogger("GeminiService")


class GeminiService(BaseAIService):
    """Central Enterprise AI Service interfacing with Gemini Flash Vision VLM."""

    DEFAULT_MODEL: str = "gemini-3.5-flash"

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = DEFAULT_MODEL,
        cache_manager: ChartCacheManager | None = None,
        quota_manager: GeminiQuotaManager | None = None,
        question_router: QuestionRouter | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name
        self.client = None

        self.cache_manager = cache_manager or ChartCacheManager()
        self.quota_manager = quota_manager or GeminiQuotaManager()
        self.question_router = question_router or QuestionRouter()

        self._init_client()

    def _init_client(self) -> None:
        """Initializes the google-genai Client."""
        self.api_key = self.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if self.api_key and HAVE_GENAI_SDK and genai is not None:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("GeminiService: Client initialized successfully.")
            except Exception as e:
                logger.warning(f"GeminiService: Client initialization error: {e}")

    def extract_chart(self, image_data: bytes | Path | str) -> FullChartExtraction:
        """Extracts complete structured data from a chart image in a SINGLE PASS (with SHA256 caching)."""
        # 1. Check SHA256 Cache (RÉACTIVÉ !)
        cached_extraction = self.cache_manager.get(image_data)
        if cached_extraction:
            self.quota_manager.record_cache_hit()
            return cached_extraction

        # 2. Cache Miss -> Make single Gemini API call with exponential backoff
        start_time = time.time()
        img_bytes, pil_img = self._load_image(image_data)

        extraction_result = self._execute_single_extraction_api(pil_img, img_bytes)
        latency = time.time() - start_time

        # Record metrics & cache
        self.quota_manager.record_call(input_tokens=600, output_tokens=400, latency_sec=latency)
        self.cache_manager.put(image_data, extraction_result)

        return extraction_result

    @exponential_backoff_retry(max_retries=2, initial_delay=1.0)
    def _execute_single_extraction_api(self, pil_img: Image.Image, img_bytes: bytes) -> FullChartExtraction:
        """Executes API extraction request to Gemini."""
        if self.client is None:
            self._init_client()

        if self.client is not None and HAVE_GENAI_SDK:
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[CHAR_EXTRACTION_SYSTEM_PROMPT, pil_img],
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        response_mime_type="application/json",
                    ) if types else None,
                )
                if response and response.text:
                    cleaned_json = self._clean_json(response.text)
                    try:
                        parsed = json.loads(cleaned_json)
                        return self._map_to_full_extraction(parsed)
                    except json.JSONDecodeError as e:
                        # On imprime le JSON cassé dans le terminal pour l'inspecter !
                        print("\n=== 🚨 JSON CRASH REPORT 🚨 ===")
                        print(cleaned_json)
                        print("===============================\n")
                        raise ValueError(f"Erreur de syntaxe de l'IA : {str(e)}")
            except Exception as e:
                logger.error(f"ERREUR CRITIQUE Gemini API : {e}")
                # Au lieu d'utiliser le fallback, on lève l'erreur pour que le frontend l'affiche !
                raise ValueError(f"Échec de l'analyse IA : {str(e)}")
        else:
            raise ValueError("Le SDK Google GenAI n'est pas installé ou la clé API GEMINI_API_KEY est manquante.")

    def detect_chart_type(self, image_data: bytes | Path | str) -> str:
        """Detects the category or type of the given chart image."""
        extraction = self.extract_chart(image_data)
        return extraction.type_graphique

    def generate_interpretation(self, extraction: FullChartExtraction, target_language: str = "fr") -> str:
        """Generates structured executive interpretation from extracted chart data.

        If interpretation_initiale was generated during single-pass extraction, reuses it!
        """
        if extraction.interpretation_initiale and len(extraction.interpretation_initiale) > 30:
            logger.info("GeminiService: Reusing saved initial interpretation (0 Gemini API calls).")
            self.quota_manager.record_local_routing()
            return extraction.interpretation_initiale

        # Otherwise generate concise interpretation
        start_t = time.time()
        prompt = INTERPRETATION_PROMPT_TEMPLATE.format(
            extracted_json=json.dumps(extraction.model_dump(), ensure_ascii=False),
            target_language="Français" if target_language == "fr" else "English",
        )
        
        # AJOUT : Directive anti-répétition absolue
        prompt += f""" Agis en tant qu'Analyste Stratégique. Analyse les données extraites de ce graphique : {json.dumps(extraction.model_dump(), ensure_ascii=False)}

        CONTRAINTES STRICTES ET ABSOLUES :
        1. AUCUNE RECOMMANDATION : Ne propose aucune action, solution, ou conseil (cela est géré par un autre système).
        2. AUCUNE RECOPIE DE DONNÉES : Ne fais aucune décomposition quantitative et ne liste pas les valeurs du tableau. Va directement aux insights.
        3. FORMAT STRICT : Ta réponse DOIT contenir UNIQUEMENT les 4 sections exactes ci-dessous, formatées en Markdown avec '###'. Ne rajoute ni introduction ni conclusion en dehors de ces titres :

        ### Résumé Exécutif et Cadrage Stratégique
        (Ton analyse ici)

        ### Tendances et Statistiques Clés
        (Ton analyse ici)

        ### Risques et Anomalies Identifiés
        (Ton analyse ici)

        ### Opportunités de Croissance et de Rentabilité
        (Ton analyse ici)
        """
        res_text = self._call_text_api(prompt, temp=0.2)
        latency = time.time() - start_t
        self.quota_manager.record_call(input_tokens=300, output_tokens=250, latency_sec=latency)
        return res_text

    def answer_question(
        self,
        extraction: FullChartExtraction,
        question: str,
        ast_context: dict[str, Any] | None = None,
        rag_context: list[str] | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """Answers user analytical question. Checks QuestionRouter first to avoid Gemini call if possible!"""
        # 1. Check QuestionRouter
        route = self.question_router.route_question(question)
        if route == RouteTarget.AST_CALCULATOR:
            ast_response = self.question_router.execute_ast_query(question, extraction)
            if ast_response:
                self.quota_manager.record_local_routing()
                return ast_response

        # 2. Text-only Gemini Call (No image re-sent)
        start_t = time.time()
        ast_str = json.dumps(ast_context or {}, ensure_ascii=False)
        rag_str = "\n".join(rag_context or [])

        prompt = QA_PROMPT_TEMPLATE.format(
            extracted_json=json.dumps(extraction.model_dump(), ensure_ascii=False),
            ast_context=ast_str,
            rag_context=rag_str,
            question=question,
        )

        res_text = self._call_text_api(prompt, temp=0.2)
        latency = time.time() - start_t
        self.quota_manager.record_call(input_tokens=400, output_tokens=200, latency_sec=latency)
        return res_text

    # AJOUT : paramètre user_context
    def generate_recommendation(self, extraction: FullChartExtraction, target_language: str = "fr", user_context: str = "") -> list[dict[str, Any]]:
        """Generate strategic recommendations based on extracted charts trends and user context."""
        start_t = time.time()
        
        prompt = RECOMMENDATION_PROMPT_TEMPLATE.format(
            extracted_json=json.dumps(extraction.model_dump(), ensure_ascii=False)
        )
        
        # AJOUT : Injection du contexte utilisateur pour des recos sur-mesure
        if user_context:
            prompt += f"\n\nCONTRAINTE DE PERSONNALISATION : L'utilisateur est un(e) {user_context}. Toutes tes recommandations doivent être ultra-spécifiques à son secteur d'activité et à son niveau d'expertise, et non génériques."

        res_text = self._call_text_api(prompt, temp=0.1)
        # ...
        latency = time.time() - start_t
        self.quota_manager.record_call(input_tokens=350, output_tokens=200, latency_sec=latency)

        try:
            cleaned = self._clean_json(res_text)
            return json.loads(cleaned)
        except Exception:
            return [
                {
                    "titre": "Consolider les segments performants",
                    "priorite": "HAUTE",
                    "description": f"Allouer les ressources prioritaires aux séries principales du graphique ({extraction.titre}).",
                    "impact_attendu": "Maximisation du ROI et stabilité des données.",
                }
            ]

    def vision_chat(
        self,
        extraction: FullChartExtraction,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """Handles conversational dialogue based on extracted chart data (Text-only, no image re-sent)."""
        return self.answer_question(extraction=extraction, question=message, history=history)

    def summarize(self, text_or_data: Any) -> str:
        """Summarizes complex text or data into concise key points."""
        if isinstance(text_or_data, str) and len(text_or_data) < 200:
            return text_or_data
        data_str = json.dumps(text_or_data, ensure_ascii=False) if not isinstance(text_or_data, str) else text_or_data
        prompt = f"Résume de manière synthétique en 2 phrases max : {data_str}"
        return self._call_text_api(prompt, temp=0.1)

    @exponential_backoff_retry(max_retries=5, initial_delay=1.0)
    def _call_text_api(self, prompt: str, temp: float = 0.2) -> str:
        """Executes text-only Gemini API call."""
        if self.client is None:
            self._init_client()

        if self.client is not None and HAVE_GENAI_SDK:
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=temp) if types else None,
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini text API call exception: {e}")

        return "Analyse analytique générée à partir des données extraites."

    @staticmethod
    def _load_image(image_input: bytes | Path | str) -> tuple[bytes, Image.Image]:
        """Helper to load image bytes and PIL Image object."""
        import io
        if isinstance(image_input, bytes):
            img_bytes = image_input
        else:
            p = Path(image_input)
            img_bytes = p.read_bytes() if p.exists() and p.is_file() else str(image_input).encode("utf-8")

        try:
            pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        except Exception:
            pil_img = Image.new("RGB", (100, 100), color=(240, 240, 240))

        return img_bytes, pil_img

    @staticmethod
    def _clean_json(raw_text: str) -> str:
        """Cleans markdown wrappers, auto-heals commas, and fixes truncated JSON braces."""
        if not raw_text:
            return "{}"
        
        clean_text = raw_text.strip()
        
        # 1. Nettoyage des balises Markdown (au début et à la fin)
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        clean_text = clean_text.strip()
        
        # 2. Sécurisation du début du JSON
        start_idx = clean_text.find('{')
        if start_idx != -1:
            clean_text = clean_text[start_idx:]

        # 3. AUTO-HEALER V2 : Correction chirurgicale des virgules
        clean_text = re.sub(r'\}\s+\{', '}, {', clean_text)
        clean_text = re.sub(r'\]\s+\{', '], {', clean_text)
        clean_text = re.sub(r'\]\s+"', '], "', clean_text)
        clean_text = re.sub(r'\}\s+"', '}, "', clean_text)
        clean_text = re.sub(r'"\s+"', '", "', clean_text)
        clean_text = re.sub(r',\s*\}', '}', clean_text)
        clean_text = re.sub(r',\s*\]', ']', clean_text)
        
        # 4. AUTO-HEALER V3 : Le correcteur de flemme (Accolades manquantes)
        open_braces = clean_text.count('{')
        close_braces = clean_text.count('}')
        
        if open_braces > close_braces:
            # S'il manque des accolades fermantes, on les ajoute à la fin !
            clean_text += '}' * (open_braces - close_braces)
            
        return clean_text.strip()

    @staticmethod
    def _map_to_full_extraction(parsed: dict[str, Any]) -> FullChartExtraction:
        """Maps dict JSON output to FullChartExtraction Pydantic model."""
        series_objs = []
        for s in parsed.get("series", []):
            series_objs.append(
                SeriesData(
                    series_name=s.get("series_name", "Série"),
                    categories=s.get("categories", []),
                    values=[float(v) for v in s.get("values", [])],
                    unit=s.get("unit", ""),
                )
            )
        return FullChartExtraction(
            type_graphique=parsed.get("type_graphique", "BAR"),
            titre=parsed.get("titre", "Graphique Extrait"),
            sous_titre=parsed.get("sous_titre", ""),
            axe_x_label=parsed.get("axe_x_label", ""),
            axe_y_label=parsed.get("axe_y_label", ""),
            unites=parsed.get("unites", ""),
            legendes=parsed.get("legendes", []),
            series=series_objs,
            donnees_tabulaires=parsed.get("donnees_tabulaires", []),
            metadonnees=parsed.get("metadonnees", {}),
            confiance_extraction=parsed.get("confiance_extraction", 95.0),
            resume_executif=parsed.get("resume_executif", ""),
            interpretation_initiale=parsed.get("interpretation_initiale", ""),
        )

    @staticmethod
    def _generate_fallback_extraction(pil_img: Image.Image) -> FullChartExtraction:
        """Fallback extraction when Gemini SDK is unavailable or unconfigured."""
        width, height = pil_img.size
        return FullChartExtraction(
            type_graphique="BAR",
            titre="Ventes Trimestrielles & Performance",
            sous_titre="Analyse de la distribution des résultats",
            axe_x_label="Trimestre",
            axe_y_label="Chiffre d'Affaires (k€)",
            unites="k€",
            legendes=["Ventes 2026"],
            series=[
                SeriesData(
                    series_name="Ventes 2026",
                    categories=["T1", "T2", "T3", "T4"],
                    values=[68.0, 88.0, 78.0, 92.0],
                    unit="k€",
                )
            ],
            donnees_tabulaires=[
                {"categorie": "T1", "valeur": 68.0},
                {"categorie": "T2", "valeur": 88.0},
                {"categorie": "T3", "valeur": 78.0},
                {"categorie": "T4", "valeur": 92.0},
            ],
            metadonnees={"dimensions": f"{width}x{height}", "source": "Extraction Fallback CV"},
            confiance_extraction=95.0,
            resume_executif="La performance globale affiche une moyenne de 81.5k€ avec un pic au T4 à 92.0k€.",
            interpretation_initiale="### RAPPORT DE PERFORMANCE EXÉCUTIF\n- **Moyenne globale :** 81.50 k€\n- **Peak T4 :** 92.00 k€\n- **Croissance :** Évolution positive observée sur l'exercice.",
        )

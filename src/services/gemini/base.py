"""BaseAIService abstract interface for multimodal and conversational AI providers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field


class SeriesData(BaseModel):
    """Represents a data series extracted from a chart."""
    series_name: str = Field(default="Série principale", description="Nom de la série de données")
    categories: list[str] = Field(default_factory=list, description="Catégories ou étiquettes de l'axe X")
    values: list[float] = Field(default_factory=list, description="Valeurs numériques associées")
    unit: str = Field(default="", description="Unité de mesure (ex: %, €, M$)")


class FullChartExtraction(BaseModel):
    """Complete, single-pass structured extraction of a chart image."""
    type_graphique: str = Field(default="BAR", description="Type de graphique (BAR, LINE, PIE, SCATTER, HISTOGRAM, AREA, OTHER)")
    titre: str = Field(default="Graphique Extrait", description="Titre principal du graphique")
    sous_titre: str = Field(default="", description="Sous-titre ou précision contextuelle")
    axe_x_label: str = Field(default="", description="Nom ou étiquette de l'axe X")
    axe_y_label: str = Field(default="", description="Nom ou étiquette de l'axe Y")
    unites: str = Field(default="", description="Unité globale des valeurs")
    legendes: list[str] = Field(default_factory=list, description="Légendes ou éléments de clé")
    series: list[SeriesData] = Field(default_factory=list, description="Liste des séries de données extraites")
    donnees_tabulaires: list[dict[str, Any]] = Field(default_factory=list, description="Tableau sous forme de dictionnaire ligne par ligne")
    metadonnees: dict[str, Any] = Field(default_factory=dict, description="Métadonnées supplémentaires (dimensions, échelle, anomalies)")
    confiance_extraction: float = Field(default=95.0, description="Score de confiance d'extraction (0-100%)")
    resume_executif: str = Field(default="", description="Résumé synthétique en 2-3 phrases des observations clés")
    interpretation_initiale: str = Field(default="", description="Interprétation analytique initiale structurée")
    image_hash: str = Field(default="", description="Empreinte SHA256 de l'image source")


class BaseAIService(ABC):
    """Abstract Base Class for Multimodal AI Services (Gemini, OpenAI, Claude, etc.)."""

    @abstractmethod
    def extract_chart(self, image_data: bytes | Path | str) -> FullChartExtraction:
        """Extracts complete structured data from a chart image in a single pass."""
        pass

    @abstractmethod
    def detect_chart_type(self, image_data: bytes | Path | str) -> str:
        """Detects the category or type of the given chart image."""
        pass

    @abstractmethod
    def generate_interpretation(self, extraction: FullChartExtraction, target_language: str = "fr") -> str:
        """Generates structured executive interpretation from extracted chart data."""
        pass

    @abstractmethod
    def answer_question(
        self,
        extraction: FullChartExtraction,
        question: str,
        ast_context: dict[str, Any] | None = None,
        rag_context: list[str] | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """Answers user analytical question based on structured chart data (text-only, no image re-sent)."""
        pass

    @abstractmethod
    def generate_recommendation(self, extraction: FullChartExtraction, target_language: str = "fr") -> list[dict[str, Any]]:
        """Generates strategic recommendations based on extracted chart trends."""
        pass

    @abstractmethod
    def vision_chat(
        self,
        extraction: FullChartExtraction,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """Handles conversational dialogue based on extracted chart data."""
        pass

    @abstractmethod
    def summarize(self, text_or_data: Any) -> str:
        """Summarizes complex text or data into concise key points."""
        pass

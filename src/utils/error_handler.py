"""Enterprise Error Handler categorizing system errors into 9 standardized domain classes with actionable solutions."""

import logging
from typing import Any
from pydantic import BaseModel, Field

logger = logging.getLogger("EnterpriseErrorHandler")


class EnterpriseErrorResponse(BaseModel):
    """Structured error object containing error code, user message, technical details, and proposed solution."""

    code: str = Field(..., description="Standardized error code (ex: ERR_OCR_001)")
    category: str = Field(..., description="Category: VALIDATION, VISION, OCR, GEMINI, FAISS, AST, PDF, API, AUTH")
    user_message: str = Field(..., description="User-facing friendly French error message")
    technical_message: str = Field(..., description="Technical exception detail")
    proposed_solution: str = Field(..., description="Recommended user or developer resolution action")


class EnterpriseErrorHandler:
    """Centralized handler mapping exceptions to categorized EnterpriseErrorResponse models."""

    ERROR_CATALOG = {
        "VALIDATION": ("ERR_VAL_400", "Erreur de Validation de Données", "Vérifier le format du fichier ou la validité des champs saisies."),
        "VISION": ("ERR_VIS_500", "Erreur du Moteur d'Analyse Visuelle", "Ressoumettre une image plus nette avec des axes bien contrastés."),
        "OCR": ("ERR_OCR_501", "Échec d'Extraction du Texte (OCR)", "S'assurer que la résolution du texte sur l'image est supérieure à 300 DPI."),
        "GEMINI": ("ERR_GEM_502", "Erreur de Communication avec l'IA Multimodale", "Vérifier la clé d'API GEMINI_API_KEY et les limites de débit."),
        "FAISS": ("ERR_FAS_503", "Erreur de Recherche Vectorielle FAISS", "Ré-indexer le corpus de connaissances ou vérifier les vecteurs RAG."),
        "AST": ("ERR_AST_504", "Erreur d'Évaluation Arithmétique AST", "Vérifier l'expression mathématique et l'absence de division par zéro."),
        "PDF": ("ERR_PDF_505", "Échec de Génération du Rapport PDF", "Vérifier la taille des polices et la présence des dépendances ReportLab."),
        "API": ("ERR_API_500", "Erreur Interne du Serveur API", "Consulter les logs système ou réessayer l'opération."),
        "AUTH": ("ERR_ATH_401", "Erreur d'Authentification / Accès Refusé", "Vérifier vos identifiants ou vous ré-authentifier."),
    }

    def __init__(self) -> None:
        pass

    def handle_exception(self, exc: Exception, category: str = "API") -> EnterpriseErrorResponse:
        """Classifies an exception and returns a standardized EnterpriseErrorResponse payload.

        Args:
            exc: Python exception instance.
            category: Error domain category.

        Returns:
            EnterpriseErrorResponse model.
        """
        cat_key = category.upper() if category.upper() in self.ERROR_CATALOG else "API"
        code, default_user_msg, default_solution = self.ERROR_CATALOG[cat_key]

        tech_msg = str(exc) or exc.__class__.__name__

        logger.error(f"[{code}] EnterpriseErrorHandler caught {cat_key} exception: {tech_msg}")

        return EnterpriseErrorResponse(
            code=code,
            category=cat_key,
            user_message=default_user_msg,
            technical_message=tech_msg,
            proposed_solution=default_solution,
        )

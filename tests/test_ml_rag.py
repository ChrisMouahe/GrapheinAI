"""Comprehensive pytest test suite for ML Classifier, Feature Engineering, EmbeddingGenerator, and FAISS RAG Pipeline."""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

from src.agents.classifier_agent import ClassifierAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.models.chart import ClassificationResult, RAGRetrievalResult
from src.models.exceptions import (
    EmbeddingGenerationError,
    FeatureEngineeringError,
    MLModelError,
    ModelNotFoundError,
    RAGPipelineError,
)
from src.utils.embedding_generator import EmbeddingGenerator
from src.utils.feature_engineering import ChartQAFeatureEngineer
from src.utils.ml_classifier import ChartQAClassifierTrainer
from src.utils.rag_pipeline import FAISSRAGPipeline


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"chart_id": "img1.png", "question": "What is the value of item A?", "chart_type": "bar"},
            {"chart_id": "img2.png", "question": "What is the average growth rate across 2020?", "chart_type": "line"},
            {"chart_id": "img3.png", "question": "What is the total sum divided by count?", "chart_type": "bar"},
            {"chart_id": "img4.png", "question": "Which slice is largest?", "chart_type": "pie"},
            {"chart_id": "img5.png", "question": "Calculate the difference between X and Y.", "chart_type": "line"},
            {"chart_id": "img6.png", "question": "What is the percentage of slice B?", "chart_type": "pie"},
        ]
    )


@pytest.fixture
def sample_rag_items() -> list[dict]:
    return [
        {
            "question": "What is the average growth rate?",
            "chart_type": "line",
            "resolution_formula": "(v1 + v2 + v3) / 3",
            "answer": "14.5%",
        },
        {
            "question": "What is the total sum of sales?",
            "chart_type": "bar",
            "resolution_formula": "sum(sales)",
            "answer": "350",
        },
        {
            "question": "Which category has the highest value?",
            "chart_type": "bar",
            "resolution_formula": "max(category_values)",
            "answer": "Category C",
        },
    ]


class TestFeatureEngineering:
    def test_extract_question_features(self) -> None:
        fe = ChartQAFeatureEngineer()
        feats = fe.extract_question_features("What is the average difference in 2024?")
        assert feats["has_math_keyword"] == 1
        assert feats["keyword_count"] >= 2
        assert feats["question_len"] > 0
        assert feats["is_question_mark"] == 1

    def test_fit_transform_and_binary_target(self, sample_dataframe: pd.DataFrame) -> None:
        fe = ChartQAFeatureEngineer()
        X, y = fe.fit_transform(sample_dataframe)

        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)
        assert len(X) == len(sample_dataframe)
        assert set(y.unique()).issubset({0, 1})

    def test_transform_missing_question_raises(self) -> None:
        fe = ChartQAFeatureEngineer()
        with pytest.raises(FeatureEngineeringError):
            fe.transform(pd.DataFrame([{"invalid_col": "val"}]))


class TestMLClassifier:
    def test_train_and_evaluate(self, sample_dataframe: pd.DataFrame, tmp_path: Path) -> None:
        trainer = ChartQAClassifierTrainer(output_dir=tmp_path)
        results = trainer.train_and_evaluate(sample_dataframe)

        assert "RandomForest" in results
        assert "XGBoost" in results
        assert "winner" in results
        assert (tmp_path / "best_classifier.joblib").exists()
        assert (tmp_path / "classifier_metadata.json").exists()

    def test_classifier_agent_predict(self, sample_dataframe: pd.DataFrame, tmp_path: Path) -> None:
        trainer = ChartQAClassifierTrainer(output_dir=tmp_path)
        trainer.train_and_evaluate(sample_dataframe)

        agent = ClassifierAgent(
            model_path=tmp_path / "best_classifier.joblib",
            metadata_path=tmp_path / "classifier_metadata.json",
        )

        res = agent.predict("What is the average percentage increase?", chart_type="line")
        assert isinstance(res, ClassificationResult)
        assert res.complexity in ("SIMPLE", "COMPLEX")
        assert 0.0 <= res.confidence <= 1.0

    def test_classifier_agent_missing_model_raises(self, tmp_path: Path) -> None:
        missing_model = tmp_path / "nonexistent.joblib"
        agent = ClassifierAgent(model_path=missing_model)

        with pytest.raises(ModelNotFoundError):
            agent.predict("Question?")


class TestEmbeddingGenerator:
    def test_encode_single_and_list(self) -> None:
        generator = EmbeddingGenerator()
        vec_single = generator.encode("What is the sales total?")
        assert isinstance(vec_single, np.ndarray)
        assert len(vec_single.shape) == 1
        assert vec_single.shape[0] == generator.get_embedding_dimension()

        vec_list = generator.encode(["Question 1", "Question 2"])
        assert isinstance(vec_list, np.ndarray)
        assert vec_list.shape == (2, generator.get_embedding_dimension())

    def test_empty_input_raises(self) -> None:
        generator = EmbeddingGenerator()
        with pytest.raises(EmbeddingGenerationError):
            generator.encode("")


class TestFAISSAndRetrievalAgent:
    def test_build_search_save_load_index(self, sample_rag_items: list[dict], tmp_path: Path) -> None:
        pipeline = FAISSRAGPipeline(index_dir=tmp_path)
        idx_p, meta_p = pipeline.build_index(sample_rag_items)

        assert idx_p.exists()
        assert meta_p.exists()

        search_res = pipeline.search("average growth rate", top_k=2)
        assert len(search_res) == 2
        assert "resolution_formula" in search_res[0]

        # Test reload
        new_pipeline = FAISSRAGPipeline(index_dir=tmp_path)
        new_pipeline.load_index(idx_p, meta_p)
        reloaded_res = new_pipeline.search("total sum", top_k=1)
        assert len(reloaded_res) == 1

    def test_retrieval_agent(self, sample_rag_items: list[dict], tmp_path: Path) -> None:
        pipeline = FAISSRAGPipeline(index_dir=tmp_path)
        idx_p, meta_p = pipeline.build_index(sample_rag_items)

        agent = RetrievalAgent(index_path=idx_p, metadata_path=meta_p)
        res_list = agent.retrieve("highest category value", top_k=3)

        assert len(res_list) == 3
        schema_res = agent.retrieve_schema("highest category value", top_k=3)
        assert isinstance(schema_res, RAGRetrievalResult)
        assert len(schema_res.results) == 3

    def test_empty_build_raises(self, tmp_path: Path) -> None:
        pipeline = FAISSRAGPipeline(index_dir=tmp_path)
        with pytest.raises(RAGPipelineError):
            pipeline.build_index([])

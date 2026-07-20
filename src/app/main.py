"""Main application entry point for ChartQA Multimodal Assistant Sprint 1 & Sprint 2 demonstration."""

from pathlib import Path
from src.agents.classifier_agent import ClassifierAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.safe_calculator import SafeCalculator
from src.models.chart import ChartExtraction, ChartImage, ExtractedDataPoint
from src.utils.data_engineering import ChartQADataEngineer
from src.utils.embedding_generator import EmbeddingGenerator
from src.utils.feature_engineering import ChartQAFeatureEngineer
from src.utils.ml_classifier import ChartQAClassifierTrainer
from src.utils.rag_pipeline import FAISSRAGPipeline


def run_demo() -> None:
    print("==================================================")
    print(" ChartQA Multimodal Assistant - Sprint 1 & 2 Demo")
    print("==================================================\n")

    # 1. Sprint 1 Foundations
    print("--- 1. Testing SafeCalculator (AST Only) ---")
    calculator = SafeCalculator()
    expr = "(125.4 + 180.2) / 2"
    res = calculator.evaluate(expr)
    print(f"SafeCalculator expression: {expr}  =>  Result: {res}\n")

    # 2. Data Engineering & ML Training
    print("--- 2. Machine Learning Classifier (XGBoost vs. RandomForest) ---")
    sample_csv = Path("data/raw/sample_chartqa.csv")
    if sample_csv.exists():
        engineer = ChartQADataEngineer(sample_csv)
        df_raw = engineer.load_data()
        df_cleaned = engineer.clean_missing_values()

        trainer = ChartQAClassifierTrainer(output_dir="models")
        eval_metrics = trainer.train_and_evaluate(df_cleaned)

        print(f"Winning Model: {eval_metrics['winner']}")
        print(f"XGBoost Metrics: {eval_metrics['XGBoost']}")
        print(f"RandomForest Metrics: {eval_metrics['RandomForest']}\n")

        # Predict with ClassifierAgent
        classifier_agent = ClassifierAgent(
            model_path="models/best_classifier.joblib",
            metadata_path="models/classifier_metadata.json",
        )
        sample_q = "What is the average growth percentage across categories?"
        pred_res = classifier_agent.predict(sample_q, chart_type="bar")
        print(f"Question: '{sample_q}'")
        print(f"Predicted Complexity: {pred_res.complexity} (Confidence: {pred_res.confidence:.2%})\n")

    # 3. RAG & FAISS Vector Search
    print("--- 3. RAG Pipeline & RetrievalAgent (FAISS + MiniLM Embeddings) ---")
    rag_sample_items = [
        {
            "question": "What is the value of item A?",
            "chart_type": "bar",
            "resolution_formula": "value(item_A)",
            "answer": "25.5",
        },
        {
            "question": "What is the average growth rate?",
            "chart_type": "line",
            "resolution_formula": "(v2022 - v2020) / 2",
            "answer": "7.8%",
        },
        {
            "question": "What is the total count in 2023?",
            "chart_type": "bar",
            "resolution_formula": "sum(count_2023)",
            "answer": "150",
        },
        {
            "question": "What is the percentage of slice B?",
            "chart_type": "pie",
            "resolution_formula": "(val_B / total) * 100",
            "answer": "18.2%",
        },
    ]

    embedder = EmbeddingGenerator()
    pipeline = FAISSRAGPipeline(index_dir="models", embedding_generator=embedder)
    pipeline.build_index(rag_sample_items)

    retrieval_agent = RetrievalAgent(
        index_path="models/index.faiss",
        metadata_path="models/metadata.pkl",
        embedding_generator=embedder,
    )

    user_query = "Calculate average growth speed"
    retrieved = retrieval_agent.retrieve(user_query, top_k=3)

    print(f"User Search Query: '{user_query}'")
    print("Top-3 Retrieved Examples:")
    for idx, item in enumerate(retrieved, 1):
        print(f"  [{idx}] Question: '{item['question']}'")
        print(f"      Formula: {item['resolution_formula']} | Answer: {item['answer']} | Distance: {item['distance']:.4f}")

    print("\n==================================================")
    print(" Sprint 2 ML & RAG execution completed successfully!")
    print("==================================================")


if __name__ == "__main__":
    run_demo()

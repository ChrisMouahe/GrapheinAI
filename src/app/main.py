"""Main application entry point for ChartQA Multimodal Assistant Sprint 1, 2 & 3 demonstration."""

from pathlib import Path

from src.agents.classifier_agent import ClassifierAgent
from src.agents.pipeline_agent import PipelineAgent
from src.agents.reasoning_agent import ReasoningAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.safe_calculator import SafeCalculator
from src.models.chart import ChartImage
from src.utils.data_engineering import ChartQADataEngineer
from src.utils.embedding_generator import EmbeddingGenerator
from src.utils.feature_engineering import ChartQAFeatureEngineer
from src.utils.ml_classifier import ChartQAClassifierTrainer
from src.utils.rag_pipeline import FAISSRAGPipeline


def run_demo() -> None:
    print("==================================================")
    print(" ChartQA Multimodal Assistant - Full Pipeline Demo")
    print(" Sprints 1, 2 & 3 Architecture Demonstration")
    print("==================================================\n")

    # 1. Sprint 1 Foundations: SafeCalculator
    print("--- 1. SafeCalculator (AST-Only Security Engine) ---")
    calc = SafeCalculator()
    expr_test = "(125.4 + 180.2) / 2"
    calc_res = calc.evaluate(expr_test)
    print(f"Expression: {expr_test}  =>  Calculated Result: {calc_res}\n")

    # 2. Sprint 2 ML & RAG Indexing
    print("--- 2. Machine Learning Classifier & FAISS RAG Setup ---")
    sample_csv = Path("data/raw/sample_chartqa.csv")
    if sample_csv.exists():
        engineer = ChartQADataEngineer(sample_csv)
        df_raw = engineer.load_data()
        df_cleaned = engineer.clean_missing_values()

        trainer = ChartQAClassifierTrainer(output_dir="models")
        trainer.train_and_evaluate(df_cleaned)

    # Build RAG index
    rag_items = [
        {
            "question": "What is the average growth rate?",
            "chart_type": "line",
            "resolution_formula": "(v2022 - v2020) / 2",
            "answer": "7.8%",
        },
        {
            "question": "What is the total sales revenue?",
            "chart_type": "bar",
            "resolution_formula": "sum(quarterly_revenue)",
            "answer": "656.1",
        },
    ]
    embedder = EmbeddingGenerator()
    rag_pipe = FAISSRAGPipeline(index_dir="models", embedding_generator=embedder)
    rag_pipe.build_index(rag_items)
    print("Trained ML model and built FAISS RAG vector index successfully.\n")

    # 3. Sprint 3 Master Orchestration (PipelineAgent)
    print("--- 3. Master PipelineAgent Orchestration (End-to-End) ---")
    sample_img_path = Path("data/raw/sample_chart.png")
    if not sample_img_path.exists():
        print("Sample chart image not found. Creating fallback chart image...")
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        sample_img_path.parent.mkdir(parents=True, exist_ok=True)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["Q1 Sales", "Q2 Sales"], [125.4, 180.2], color=["#4C72B0", "#55A868"])
        ax.set_title("Quarterly Sales 2024")
        plt.tight_layout()
        plt.savefig(sample_img_path, dpi=100)
        plt.close(fig)

    pipeline = PipelineAgent()
    target_question = "What is the average growth rate between Q1 and Q2 sales?"

    print(f"Target Image: {sample_img_path}")
    print(f"User Question: '{target_question}'\n")
    print("Executing Orchestration Pipeline:")
    print("  [Step 1] ChartImage -> Input Image Loaded")
    print("  [Step 2] ClassifierAgent -> Predicting Complexity & Chart Type")
    print("  [Step 3] RetrievalAgent -> Searching Top-3 FAISS RAG Context")
    print("  [Step 4] ReasoningAgent -> Prompting Gemini Flash Vision VLM")
    print("  [Step 5] SafeCalculator -> Evaluating Arithmetic AST Formula\n")

    result = pipeline.answer(image=sample_img_path, question=target_question)

    print("==================================================")
    print(" FINAL MULTIMODAL REASONING RESULT")
    print("==================================================")
    print(f"Final Answer: {result.final_answer}")
    print(f"Calculation Expression: {result.calculation_expression}")
    print(f"ML Complexity Level: {result.complexity.complexity} (Confidence: {result.complexity.confidence:.2%})")
    print(f"Extracted Chart Title: {result.extracted_data.title}")
    print(f"Extracted Data Points ({len(result.extracted_data.data_points)}):")
    for dp in result.extracted_data.data_points:
        print(f"  - {dp.label}: {dp.value} (confidence: {dp.confidence:.2f})")
    print("\nStep-by-Step Reasoning:")
    print(f"  {result.reasoning}")
    print("\nRetrieved RAG Few-Shot Context Examples:")
    for idx, ex in enumerate(result.retrieved_examples, 1):
        print(f"  [{idx}] '{ex.get('question')}' => Formula: {ex.get('resolution_formula')}")
    print("==================================================")


if __name__ == "__main__":
    run_demo()

"""Main application entry point for ChartQA Multimodal Assistant Sprint 1 demonstration."""

from pathlib import Path
from src.agents.safe_calculator import SafeCalculator
from src.models.chart import ChartExtraction, ChartImage, ExtractedDataPoint
from src.utils.data_engineering import ChartQADataEngineer


def run_demo() -> None:
    print("==================================================")
    print(" ChartQA Multimodal Assistant - Sprint 1 Demo")
    print("==================================================\n")

    # 1. Models Demonstration
    print("--- 1. Testing Domain Models ---")
    data_point_a = ExtractedDataPoint(label="Q1 Sales", value=125.4, confidence=0.98)
    data_point_b = ExtractedDataPoint(label="Q2 Sales", value=180.2, confidence=0.95)

    extraction = ChartExtraction(
        chart_type="bar",
        title="Quarterly Sales 2024",
        x_label="Quarter",
        y_label="Revenue ($k)",
        data_points=[data_point_a, data_point_b],
    )
    print(f"Chart Title: {extraction.title}")
    print(f"Extracted Data Points: {[dp.label for dp in extraction.data_points]}")
    print(f"Numerical values: {extraction.get_numerical_values()}\n")

    # 2. SafeCalculator Demonstration
    print("--- 2. Testing SafeCalculator (AST Only) ---")
    calculator = SafeCalculator()
    expressions = [
        "10 + 15 * 2",
        "(125.4 + 180.2) / 2",
        "-50 + (3 * 4)",
        "2 ** 4",
    ]
    for expr in expressions:
        res = calculator.evaluate(expr)
        print(f"Expression: {expr}  =>  Result: {res}")

    # Injection test demo
    print("\nSecurity Injection Test:")
    injection_expr = "__import__('os').system('echo Hacked')"
    try:
        calculator.evaluate(injection_expr)
    except Exception as e:
        print(f"Blocked expression '{injection_expr}' successfully!")
        print(f"Caught expected security error: {type(e).__name__} - {e}\n")

    # 3. Data Engineering Demonstration
    print("--- 3. Testing Data Engineering Pipeline ---")
    sample_csv = Path("data/raw/sample_chartqa.csv")
    if sample_csv.exists():
        engineer = ChartQADataEngineer(sample_csv)
        df_raw = engineer.load_data()
        print(f"Loaded raw dataset with {len(df_raw)} rows.")

        df_cleaned = engineer.clean_missing_values()
        df_transformed = engineer.convert_types(df_cleaned)

        stats = engineer.get_descriptive_stats(df_transformed)
        print(f"Dataset columns: {stats['columns']}")
        print(f"Missing values summary: {stats['missing_values']}")

        plots = engineer.generate_exploratory_plots(df_transformed)
        print(f"Generated {len(plots)} exploratory plots in data/processed/plots/\n")

    print("==================================================")
    print(" Sprint 1 Foundations execution completed successfully!")
    print("==================================================")


if __name__ == "__main__":
    run_demo()

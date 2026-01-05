# TinyTest: SLM Unit Test Evaluation Framework

**TinyTest** is a research framework designed to evaluate the true capabilities of Small Language Models (SLMs) in generating unit tests. 

We go beyond simple **Pass Rates** or **Line Coverage**. This framework uses **Mutation Testing** as the gold standard to verify if the generated tests actually detect bugs ("kill mutants") or just mechanically execute code ("hollow tests").

---

## Key Features

*   **Automated Pipeline**: End-to-end generation, execution, and repair of unit tests (`scripts/run_pipeline.py`).
*   **Mutation Intelligence**: Integration with `mutmut` to measure the semantic adequacy of tests.
*   **Auto-Repair**: Attempt to fix syntax and assertion errors iteratively.
*   **Research-Grade Artifacts**: Generation of publication-ready Tables, Heatmaps, and Efficiency Frontiers.

---

## How to Use

### Prerequisites
Ensure you have Python 3.10+ installed.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the Full Pipeline
The framework operates in stages. Here are the commands to reproduce our experiments:

**Step 1: Generate & Repair Tests**
Runs the LLM agent to generate tests, attempting auto-repair on failures.
```bash
python -m scripts.run_pipeline --model llama3.2 --template few_shot --range 1-164 --max_retries 2 --temperature 0.3 --provider ollama --strip-docstrings
```

**Step 2: Parse & Analyze Results**
Extracts pass/fail metrics from the raw logs.
```bash
python scripts/analyze_results.py --runs-dir old_runs/run_id_XX --output run_id_XX_results_summary.json
```

**Step 3: Consolidate Passing Tests**
Extracts valid test cases from the runs into a clean test suite.
```bash
python -m scripts.consolidate_tests --summary-file run_id_XX_results_summary.json --run-id run_id_XX
```

**Step 4: Measure Line Coverage**
Runs the consolidated tests against the source code to calculate coverage.
```bash
python -m scripts.run_coverage --test-dir consolidated_tests/run_id_XX --source data/modules --output coverage_summary_run_id_XX.txt
```

**Step 5: Prepare Mutation Testing Workspace**
Sets up the environment for `mutmut` execution.
```bash
python build_mutation_workspace.py --tests consolidated_tests/run_id_XX --source-modules data/modules
```


## Understanding the Metrics

We use specialized metrics to tell the real story of testing quality:

*   **Mutation Score (The Truth)**: The percentage of artificial bugs (mutants) your tests detected. A high score means the tests are robust.
*   **Verification Gap**: The difference between *Line Coverage* (lines touched) and *Mutation Score* (lines verified). Large gaps indicate "Hollow Tests."
*   **Cost of Assurance (Tokens/Killed Mutant)**: An economic metric. How many tokens does the model burn to find one actual bug? (Lower is better).

---

*Verified for Research Validity | TinyTest Framework*
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
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Also, ensure, that your have Ollama in your system. You can download it from [here](https://ollama.com/).

### Running the Full Pipeline
The framework operates in stages. Here are the commands to reproduce our experiments:

**Step 1: Generate & Repair Tests**
Runs the LLM agent to generate tests, attempting auto-repair on failures.
```bash
python -m scripts.run_pipeline \
--model llama3.2 \
--template few_shot \
--range 1-164 \
--max_retries 2 \
--temperature 0.3 \
--provider ollama \
--strip-docstrings \
--output-dir all_runs/run_id_XX
```

To run the pipeline in different configuration, use the following options:

* zero-shot prompt + 3 auto repair iterations + keeping docstrings (ZS+R+D);
* few-shot prompt + 3 auto repair iterations + keeping docstrings (FS+R+D);
* few-shot prompt + 0 auto repair iterations + keeping docstrings (FS+NR+D);
* few-shot prompt + 3 auto repair iterations + removing docstrings (FS+R+ND);
* few-shot prompt + 0 auto repair iterations + removing docstrings (FS+NR+ND).

------------ 


1. To run with doscting removed, use the `--strip-docstrings` flag / else remove it from the command.
2. To run with 0 auto repair iterations, use the `--max_retries 0` flag.
3. To run with zero-shot prompt, use the `--template zero_shot` flag.
4. To run with different range of modules, use the `--range` flag.
5. To run with different temperature, use the `--temperature` flag.
6. To run with different provider, use the `--provider` flag. Currently we have support for Ollama, OpenAI, Gemini.
7. To run with different model, use the `--model` flag.    
8. To run with different output directory, use the `--output-dir` flag. If you don't provide any directory, the framework will create a new directory with a fixed number - all_runs/run_id_00. To make the trancking simple, we used the format like this: all_runs/run_id_XY , where XY is a fixed number, here X if from Model_MAP and Y is from CONFIG_SHORT. So, for example, run_id_12 means that the model is llama3.2 and the configuration is FS+R+D.

```bash
MODEL_MAP = {
    1: "llama3.2",
    2: "gemma3:4b",
    3: "qwen2.5-coder",
    4: "phi3:3.8b",
    5: "mistral:7b",
    6: "gpt-4o-mini",
    7: "gemini-flash-2.5-lite"
}

CONFIG_SHORT = {
    1: "ZS+R+D",
    2: "FS+R+D",
    3: "FS+NR+D",
    4: "FS+R+ND",
    5: "FS+NR+ND"
}
```


**Step 2: Parse & Analyze Results**
Extracts pass/fail metrics from the raw logs.
```bash
python scripts/analyze_results.py \
--runs-dir all_runs/run_id_XY\
--output run_id_XY_results_summary.json
```

**Step 3: Consolidate Passing Tests**
Extracts valid test cases from the runs into a clean test suite.
```bash
python -m scripts.consolidate_tests \
--summary-file run_id_XY_results_summary.json \
--run-id run_id_XY
```

**Step 4: Measure Line Coverage**
Runs the consolidated tests against the source code to calculate coverage.
```bash
python -m scripts.run_coverage \
--test-dir consolidated_tests/run_id_XY \
--source data/modules \
--output coverage_summary_run_id_XY.txt
```

**Step 5: Prepare Mutation Testing Workspace**
Sets up the environment for `mutmut` execution.
```bash
python build_mutation_workspace.py \
--tests consolidated_tests/run_id_XY \
--source-modules data/modules
```

After creating the workspace, you can run mutation testing inside this workspace:
```bash
cd mut_workspace/run_id_XY
mutmut run
```


## Understanding the Metrics

We use specialized metrics to tell the real story of testing quality:

*   **Mutation Score (The Truth)**: The percentage of artificial bugs (mutants) your tests detected. A high score means the tests are robust.
*   **Verification Gap**: The difference between *Line Coverage* (lines touched) and *Mutation Score* (lines verified). Large gaps indicate "Hollow Tests."
*   **Cost of Assurance (Tokens/Killed Mutant)**: An economic metric. How many tokens does the model burn to find one actual bug? (Lower is better).

---

*Verified for Research Validity | TinyTest Framework*
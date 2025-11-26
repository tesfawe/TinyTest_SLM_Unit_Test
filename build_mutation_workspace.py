import os
import shutil
import re
import argparse
import configparser

## Usage: python build_mutation_workspace.py --tests path/to/tests/run_id_X --source-modules path/to/source/modules [--workspace mut_workspace]

def main():
    parser = argparse.ArgumentParser(description="Prepare mutation testing workspace.")
    parser.add_argument(
        "--tests",
        required=True,
        help="Path to test directory (must contain folder name like run_id_X)"
    )
    parser.add_argument(
        "--source-modules",
        required=True,
        help="Path to source modules directory"
    )
    parser.add_argument(
        "--workspace",
        default="mut_workspace",
        help="Parent workspace directory (default: mut_workspace)"
    )

    args = parser.parse_args()

    TEST_DIR = args.tests
    SOURCE_MODULES = args.source_modules
    WORKSPACE = args.workspace

    # Extract run_id from the last folder name
    RUN_ID = os.path.basename(os.path.normpath(TEST_DIR))

    # Create a run-specific workspace
    RUN_WORKSPACE = os.path.join(WORKSPACE, RUN_ID)
    WS_DATA = os.path.join(RUN_WORKSPACE, "data")
    WS_MODULES = os.path.join(WS_DATA, "modules")
    WS_TESTS = os.path.join(RUN_WORKSPACE, "tests", RUN_ID)

    # Create directories
    os.makedirs(WS_MODULES, exist_ok=True)
    os.makedirs(WS_TESTS, exist_ok=True)

    pattern = re.compile(r"module_(\d+)_test\.py$")
    copied_modules = set()

    # Copy modules and tests
    for filename in os.listdir(TEST_DIR):
        match = pattern.match(filename)
        if not match:
            continue

        test_number = match.group(1)
        module_filename = f"module_{test_number}.py"

        src_module_path = os.path.join(SOURCE_MODULES, module_filename)
        dst_module_path = os.path.join(WS_MODULES, module_filename)

        if os.path.isfile(src_module_path):
            print(f"Copying module → {dst_module_path}")
            shutil.copy2(src_module_path, dst_module_path)
            copied_modules.add(module_filename)
        else:
            print(f"Module not found: {module_filename}")

        # Copy test file
        src_test_path = os.path.join(TEST_DIR, filename)
        dst_test_path = os.path.join(WS_TESTS, filename)
        print(f"Copying test → {dst_test_path}")
        shutil.copy2(src_test_path, dst_test_path)

    # Create __init__.py files
    for path in [RUN_WORKSPACE, WS_DATA, WS_MODULES, WS_TESTS]:
        init_file = os.path.join(path, "__init__.py")
        os.makedirs(path, exist_ok=True)
        open(init_file, "w").close()

    print("\nWorkspace created successfully!")
    print(f"Run-specific workspace: {RUN_WORKSPACE}")
    print("Mutate these modules:")
    for m in sorted(copied_modules):
        print("   -", m)

    print("\nRun mutation testing inside this workspace:")
    print(f"    cd {RUN_WORKSPACE}")
    print("    mutmut run")

    # Generate run-specific setup.cfg
    setup_cfg_path = os.path.join(RUN_WORKSPACE, "setup.cfg")
    config = configparser.ConfigParser()
    config["mutmut"] = {
        "paths_to_mutate": f"{SOURCE_MODULES}/",
        "runner": f"python -m pytest tests/{RUN_ID}/ --tb=short"
    }
    with open(setup_cfg_path, "w") as f:
        config.write(f)

    print(f"\nCreated {setup_cfg_path} with:")
    print(f"  paths_to_mutate = {SOURCE_MODULES}/")
    print(f"  runner = python -m pytest tests/{RUN_ID}/ --tb=short")


if __name__ == "__main__":
    main()

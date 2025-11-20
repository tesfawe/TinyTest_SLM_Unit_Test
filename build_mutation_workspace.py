import os
import shutil
import re

TEST_DIR = "consolidated_tests/run_id_4"
SOURCE_MODULES = "data/modules"

# The directory where mutation testing will be done
WORKSPACE = "mut_workspace"
WS_DATA = os.path.join(WORKSPACE, "data")
WS_MODULES = os.path.join(WORKSPACE, "data", "modules")
WS_TESTS = os.path.join(WORKSPACE, "tests", "run_id_4")

# Create workspace directory structure
os.makedirs(WS_MODULES, exist_ok=True)
os.makedirs(WS_TESTS, exist_ok=True)

pattern = re.compile(r"module_(\d+)_test\.py$")

copied_modules = set()

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

    # Copy test file too
    src_test_path = os.path.join(TEST_DIR, filename)
    dst_test_path = os.path.join(WS_TESTS, filename)

    print(f"Copying test → {dst_test_path}")
    shutil.copy2(src_test_path, dst_test_path)

# Create __init__.py files so imports work
open(os.path.join(WORKSPACE, "__init__.py"), "w").close()
open(os.path.join(WS_DATA, "__init__.py"), "w").close()
open(os.path.join(WS_MODULES, "__init__.py"), "w").close()
os.makedirs(os.path.join(WORKSPACE, "tests"), exist_ok=True)
open(os.path.join(WORKSPACE, "tests", "__init__.py"), "w").close()
open(os.path.join(WS_TESTS, "__init__.py"), "w").close()

print("\n Workspace created successfully!")
print("Mutate these modules:")
for m in sorted(copied_modules):
    print("   -", m)

print("\n Run mutation testing inside mut_workspace/")
print("Example:")
print("    cd mut_workspace")
print("    mutmut run --paths-to-mutate data/modules")

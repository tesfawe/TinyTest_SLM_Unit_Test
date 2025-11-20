import subprocess
import json
import re
from collections import defaultdict

OUTPUT_JSON_FILE = "mutmut_results.json"


# Run mutation testing
print("Running mutation testing with Mutmut...")
try:
    subprocess.run(["mutmut", "run"], check=True)
except subprocess.CalledProcessError as e:
    print("Error running mutmut:", e)
    exit(1)

# Capture results
print("Fetching mutation results...")
try:
    result = subprocess.run(
        ["mutmut", "results"], capture_output=True, text=True, check=True
    )
    lines = result.stdout.splitlines()
except subprocess.CalledProcessError as e:
    print("Error fetching mutmut results:", e)
    exit(1)

# Parse results
mutants = []
pattern = re.compile(
    r"(?P<module>[\w\.]+)\.(?P<function>\w+)__mutmut_(?P<id>\d+): (?P<status>\w+)"
)

for line in lines:
    match = pattern.match(line.strip())
    if match:
        m = match.groupdict()
        m["id"] = int(m["id"])
        m["status"] = m["status"].lower()  # killed / survived / timeout
        mutants.append(m)

# Save full mutant details to JSON
with open(OUTPUT_JSON_FILE, "w") as f:
    json.dump(mutants, f, indent=2)
print(f"Saved detailed mutants to {OUTPUT_JSON_FILE}")


print("Mutation testing and JSON export complete!")

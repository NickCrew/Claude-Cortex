import re

def parse_workstream_sections(text: str) -> list:
    # The regex from tui_textual.py
    workstream_pattern = re.compile(
        r"###\s+\d+\.\s+\**(.*?)\**\s*\(([^)]+)\)", re.IGNORECASE
    )
    matches = list(workstream_pattern.finditer(text))
    
    print(f"Found {len(matches)} matches.")
    for idx, match in enumerate(matches):
        print(f"Match {idx}: Group 1='{match.group(1)}', Group 2='{match.group(2)}'")
        
    return matches

test_cases = []

# 1. Expected format
test_cases.append("### 1. **Setup Environment** (DevOps)\n- Install dependencies")

# 2. Missing bold
test_cases.append("### 1. Setup Environment (DevOps)\n- Install dependencies")

# 3. Missing parens
test_cases.append("### 1. **Setup Environment**\n- Install dependencies")

# 4. Different header level
test_cases.append("## 1. **Setup Environment** (DevOps)\n- Install dependencies")

# 5. Case sensitivity
test_cases.append("### 1. **setup environment** (devops)")

for i, text in enumerate(test_cases):
    print(f"\n--- Test Case {i+1} ---")
    parse_workstream_sections(text)

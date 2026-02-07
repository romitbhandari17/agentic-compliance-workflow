import os
import sys
import json

# ensure project root is on sys.path so imports work
# script_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(script_dir)
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

from main import handler  # type: ignore

event = {
    "contract_id": "",
    "s3": {"bucket": "agentic-compliance-workflow-dev-s3-artifacts", "key": "contracts/contract.pdf"},
    # add optional metadata here if needed
}

if __name__ == "__main__":
    result = handler(event, None)
    print(json.dumps(result, indent=2, ensure_ascii=False))

"""Simple local runner to invoke the compliance.lambda handler with a sample
ingestion output. Usage:

  python3 scripts/trigger_compliance_local.py [--payload payload.json]

Set USE_BEDROCK=1 and BEDROCK_MODEL_ID=<model-id> in your environment to enable Bedrock calls.
"""
import os
import sys
import json
from typing import Any, Dict

# Ensure repo root is on sys.path so imports like src.agents.compliance.main work
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, "../.."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from src.agents.compliance.main import handler  # type: ignore


def load_payload(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


if __name__ == "__main__":

    # event: Dict[str, Any] = {
    #     "status": "ok",
    #     "contract_id": "abc-123",
    #     "s3": {"bucket": "agentic-compliance-workflow-dev-s3-artifacts", "key": "contracts/contract.pdf"},
    #     "extracted_text": "This contract includes revenue information. Contact: alice@example.com. Audit required.",
    #     "extracted_lines": [
    #         "This contract includes revenue information.",
    #         "Contact: alice@example.com.",
    #         "Audit required."
    #     ],
    #     "metadata": {"n_lines": 3, "n_chars": 123},
    # }

    event = {
        "status": "ok",
        "contract_id": "6d3f61e1-82a2-4c69-9feb-b2ee05996c75",
        "s3": {
            "bucket": "agentic-compliance-workflow-dev-s3-artifacts",
            "key": "contracts/contract.pdf"
        },
        "extracted_text": "MASTER SERVICES AGREEMENT (MSA)\nThis Master Services Agreement (\"Agreement\") is entered into as of March 1, 2026 (\"Effective\nDate\") by and between:\n(1) Acme Analytics, Inc., a Delaware corporation with offices at 100 Market Street, San Francisco,\nCA 94105 (\"Customer\"); and\n(2) BrightVendor LLC, a New York limited liability company with offices at 200 Madison Avenue,\nNew York, NY 10016 (\"Vendor\").\n1. Services\nVendor will provide data processing and analytics services (\"Services\") as described in Statements\nof Work (\"SOWs\") executed by the parties.\n2. Term and Renewal\n2.1 Initial Term. The initial term begins on the Effective Date and continues for twelve (12) months\n(\"Initial Term\").\n2.2 Renewal. After the Initial Term, this Agreement will automatically renew for successive one (1)\nyear periods unless either party provides written notice of non-renewal at least thirty (30) days\nbefore the end of the then-current term.\n3. Fees and Payment Terms\n3.1 Fees. Customer will pay Vendor the fees set forth in the applicable SOW.\n3.2 Invoicing. Vendor will invoice monthly in arrears.\n3.3 Payment Terms. Customer will pay undisputed invoices within thirty (30) days of receipt (\"Net\n30\").\n3.4 Late Fees. Overdue amounts may accrue interest at 1.5% per month or the maximum allowed\nby law, whichever is lower.\n4. Termination\n4.1 Termination for Convenience. Customer may terminate this Agreement or any SOW for\nconvenience upon sixty (60) days' prior written notice.\n4.2 Termination for Cause. Either party may terminate this Agreement upon written notice if the\nother party materially breaches and fails to cure such breach within thirty (30) days after receiving\nwritten notice.\n4.3 Effect of Termination. Upon termination, Customer will pay Vendor for Services performed up\nto the effective date of termination.\n5. Data Protection and Confidentiality\n5.1 Confidential Information. Each party may receive confidential information from the other and\nwill protect it using at least reasonable care.\n5.2 Data Protection. Vendor will implement and maintain appropriate technical and organizational\nsecurity measures to protect Customer Data against unauthorized access, use, alteration, or\ndisclosure.\n5.3 Security Incident Notification. Vendor will notify Customer without undue delay and in any\nevent within seventy-two (72) hours after becoming aware of a confirmed security incident involving\nCustomer Data.\n5.4 Data Processing. Vendor will process Customer Data only to provide the Services and in\naccordance with Customer's documented instructions.\n6. Limitation of Liability\n6.1 Cap. Except for Excluded Claims, each party's total aggregate liability will not exceed the fees\npaid or payable in the twelve (12) months preceding the claim.\n6.2 Exclusion of Damages. Except for Excluded Claims, neither party will be liable for indirect or\nconsequential damages.\n6.3 Excluded Claims. Excluded Claims include breach of confidentiality, IP infringement, or gross\nnegligence or willful misconduct.\n7. Indemnification\n7.1 Vendor Indemnity. Vendor will indemnify Customer for third-party claims arising from IP\ninfringement or misconduct.\n7.2 Customer Indemnity. Customer will indemnify Vendor for claims arising from misuse of\nServices.\n8. Governing Law\nThis Agreement is governed by the laws of the State of New York.\n9. Miscellaneous\n9.1 Entire Agreement. This Agreement constitutes the entire agreement.\n9.2 Order of Precedence. SOWs control in case of conflict.\n9.3 Notices. Notices must be in writing by email and certified mail.\nIN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.\nCustomer: Acme Analytics, Inc.\nBy:\nName: Jordan Lee\nTitle: VP Procurement\nVendor: BrightVendor LLC\nBy:\nName: Taylor Morgan\nTitle: Managing Member",
        "extracted_lines": [
            "MASTER SERVICES AGREEMENT (MSA)",
            "This Master Services Agreement (\"Agreement\") is entered into as of March 1, 2026 (\"Effective",
            "Date\") by and between:",
            "(1) Acme Analytics, Inc., a Delaware corporation with offices at 100 Market Street, San Francisco,",
            "CA 94105 (\"Customer\"); and",
            "(2) BrightVendor LLC, a New York limited liability company with offices at 200 Madison Avenue,",
            "New York, NY 10016 (\"Vendor\").",
            "1. Services",
            "Vendor will provide data processing and analytics services (\"Services\") as described in Statements",
            "of Work (\"SOWs\") executed by the parties.",
            "2. Term and Renewal",
            "2.1 Initial Term. The initial term begins on the Effective Date and continues for twelve (12) months",
            "(\"Initial Term\").",
            "2.2 Renewal. After the Initial Term, this Agreement will automatically renew for successive one (1)",
            "year periods unless either party provides written notice of non-renewal at least thirty (30) days",
            "before the end of the then-current term.",
            "3. Fees and Payment Terms",
            "3.1 Fees. Customer will pay Vendor the fees set forth in the applicable SOW.",
            "3.2 Invoicing. Vendor will invoice monthly in arrears.",
            "3.3 Payment Terms. Customer will pay undisputed invoices within thirty (30) days of receipt (\"Net",
            "30\").",
            "3.4 Late Fees. Overdue amounts may accrue interest at 1.5% per month or the maximum allowed",
            "by law, whichever is lower.",
            "4. Termination",
            "4.1 Termination for Convenience. Customer may terminate this Agreement or any SOW for",
            "convenience upon sixty (60) days' prior written notice.",
            "4.2 Termination for Cause. Either party may terminate this Agreement upon written notice if the",
            "other party materially breaches and fails to cure such breach within thirty (30) days after receiving",
            "written notice.",
            "4.3 Effect of Termination. Upon termination, Customer will pay Vendor for Services performed up",
            "to the effective date of termination.",
            "5. Data Protection and Confidentiality",
            "5.1 Confidential Information. Each party may receive confidential information from the other and",
            "will protect it using at least reasonable care.",
            "5.2 Data Protection. Vendor will implement and maintain appropriate technical and organizational",
            "security measures to protect Customer Data against unauthorized access, use, alteration, or",
            "disclosure.",
            "5.3 Security Incident Notification. Vendor will notify Customer without undue delay and in any",
            "event within seventy-two (72) hours after becoming aware of a confirmed security incident involving",
            "Customer Data.",
            "5.4 Data Processing. Vendor will process Customer Data only to provide the Services and in",
            "accordance with Customer's documented instructions.",
            "6. Limitation of Liability",
            "6.1 Cap. Except for Excluded Claims, each party's total aggregate liability will not exceed the fees",
            "paid or payable in the twelve (12) months preceding the claim.",
            "6.2 Exclusion of Damages. Except for Excluded Claims, neither party will be liable for indirect or",
            "consequential damages.",
            "6.3 Excluded Claims. Excluded Claims include breach of confidentiality, IP infringement, or gross",
            "negligence or willful misconduct.",
            "7. Indemnification",
            "7.1 Vendor Indemnity. Vendor will indemnify Customer for third-party claims arising from IP",
            "infringement or misconduct.",
            "7.2 Customer Indemnity. Customer will indemnify Vendor for claims arising from misuse of",
            "Services.",
            "8. Governing Law",
            "This Agreement is governed by the laws of the State of New York.",
            "9. Miscellaneous",
            "9.1 Entire Agreement. This Agreement constitutes the entire agreement.",
            "9.2 Order of Precedence. SOWs control in case of conflict.",
            "9.3 Notices. Notices must be in writing by email and certified mail.",
            "IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.",
            "Customer: Acme Analytics, Inc.",
            "By:",
            "Name: Jordan Lee",
            "Title: VP Procurement",
            "Vendor: BrightVendor LLC",
            "By:",
            "Name: Taylor Morgan",
            "Title: Managing Member"
        ],
        "metadata": {
            "n_lines": 69,
            "n_chars": 3769
        }
    };

    print("Invoking compliance.handler with event:\n", json.dumps(event, indent=2))
    try:
        result = handler(event, None)
    except Exception as e:
        print("Handler raised:", e)
        raise

    print("Result:\n", json.dumps(result, indent=2))

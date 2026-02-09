# Implemented compliance lambda handler that accepts the ingestion output and applies
# simple GDPR and SOX rules. It will try to call AWS Bedrock (if available) for
# advanced ML-based checks, and fall back to local rule-based checks otherwise.
# The handler returns a structured `findings` list and a summary.

import os
import re
import json
import logging
from typing import Any, Dict, List, Optional
import boto3

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

_region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-west-2"
# Set default session so boto3.client() picks this region when created without explicit region
boto3.setup_default_session(region_name=_region)
logger.info("Using AWS region for boto3: %s", _region)
print(f"Using AWS region for boto3: {_region}")

# Regexes for simple PII detection (GDPR-related)
PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "phone": re.compile(r"(?:\+\d{1,3}[\s-]?)?(?:\(\d+\)|\d+)[\s.-]?\d+[\s.-]?\d+"),
    # US SSN-ish pattern (very approximate)
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    # Simple date pattern (may indicate DOB or deadlines)
    "date": re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
}

# Keywords for SOX-ish checks (financial controls / audit related)
SOX_KEYWORDS = [
    "revenue",
    "net income",
    "financial statements",
    "internal control",
    "material weakness",
    "fraud",
    "audit",
    "compliance",
    "whistleblow",
]

# Severity mapping for local rules
RULE_SEVERITY = {
    "gdpr_pii": "high",
    "gdpr_sensitive": "high",
    "sox_keyword": "medium",
}


def _safe_bedrock_client():
    """Try to create a Bedrock (or bedrock-runtime) boto3 client.
    Returns client or None if unavailable.
    """
    print("Entering _safe_bedrock_client")
    for name in ("bedrock-runtime", "bedrock"):
        try:
            return boto3.client(name)
        except Exception:
            continue
    return None


def _call_bedrock_for_checks(text: str, model: Optional[str] = None) -> Dict[str, Any]:
    """Attempt to call Bedrock to perform advanced checks.

    This simplified function constructs a single, well-formed messages-style
    payload that is compatible with Amazon Nova-style models and many other
    chat-style models hosted on Bedrock. It will attempt a short list of
    candidate models (environment override -> Nova -> Anthropic) and return
    the parsed JSON response on success or a structured failure dict.
    """
    print("Entering _call_bedrock_for_checks")
    client = _safe_bedrock_client()
    if not client:
        msg = "Bedrock client is unavailable in this environment"
        logger.info(msg)
        return {"bedrock_ok": False, "error": msg}

    # Candidate model ordering: explicit argument, env var, common Nova id, Anthropic fallback
    model_id = os.environ.get("BEDROCK_MODEL_ID") or "arn:aws:bedrock:us-west-2:968239734180:inference-profile/global.amazon.nova-2-lite-v1:0" #"anthropic.claude-v1" "amazon.nova-lite-v1:0"

    # Build a single messages-style payload that uses an array for content items
    prompt = (
        "You are a compliance assistant. Given the following document text, "
        "return a JSON object with two keys: 'pii' (list of detected PII types and examples) "
        "and 'issues' (list of compliance issues with short explanations).\n\n"
        f"Document:\n{(text[:2000] + '...') if len(text) > 2000 else text}\n\n"
        "Respond ONLY with valid JSON."
    )

    # if "anthropic" in model:
    #     payload = {
    #         "anthropic_version": "bedrock-2023-05-31",
    #         "max_tokens": 500,
    #         "temperature": 0,
    #         "messages": [
    #             {"role": "user", "content": [{"type": "text", "text": prompt}]},
    #         ],
    #     }
    # elif "amazon" in model:
    payload = {
            "inferenceConfig": {
                "maxTokens": 500,
                "temperature": 0,
            },
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
        }

    last_err: Optional[Exception] = None
    try:
        print(f"Trying Bedrock model: {model_id}")
        body = json.dumps(payload)
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=body,
        )

        resp_body = response.get("body") or response.get("Body")
        if not resp_body:
            raise RuntimeError("Empty response from Bedrock")

        if hasattr(resp_body, "read"):
            raw = resp_body.read()
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", errors="ignore")
        else:
            raw = resp_body

        parsed = json.loads(raw)
        print(f"Bedrock model {model_id} returned a response")
        return {"bedrock_ok": True, "result": parsed, "used_model": model_id}

    except Exception as e:
        last_err = e
        msg = str(e)
        # If validation-type errors occur, try next candidate model
        if any(k in msg for k in ("messages", "JSONArray", "Malformed", "required key")):
            print(f"Bedrock model {model_id} rejected the payload: {msg}")
            logger.info("Bedrock model %s rejected payload: %s", model_id, msg)
            return {"bedrock_ok": False, "error": str(last_err) if last_err else "no models tried"}


def _local_pii_checks(text: str) -> List[Dict[str, Any]]:
    print("Entering _local_pii_checks")
    findings: List[Dict[str, Any]] = []
    # Check each PII pattern and capture small examples
    for kind, pattern in PII_PATTERNS.items():
        for match in pattern.finditer(text):
            snippet = match.group(0)
            findings.append(
                {
                    "rule_id": "gdpr_pii",
                    "type": kind,
                    "match": snippet,
                    "severity": RULE_SEVERITY.get("gdpr_pii", "high"),
                }
            )
            # Do not flood: capture up to a few
            if len([f for f in findings if f.get("type") == kind]) >= 10:
                break
    return findings


def _local_sox_checks(text: str) -> List[Dict[str, Any]]:
    print("Entering _local_sox_checks")
    findings: List[Dict[str, Any]] = []
    lowtext = text.lower()
    for kw in SOX_KEYWORDS:
        if kw in lowtext:
            # capture short context near first occurrence
            idx = lowtext.find(kw)
            start = max(0, idx - 40)
            end = min(len(text), idx + len(kw) + 40)
            snippet = text[start:end].strip()
            findings.append(
                {
                    "rule_id": "sox_keyword",
                    "keyword": kw,
                    "match": snippet,
                    "severity": RULE_SEVERITY.get("sox_keyword", "medium"),
                }
            )
    return findings


def _summarize_findings(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    print("Entering _summarize_findings")
    counts = {"high": 0, "medium": 0, "low": 0}
    for f in findings:
        sev = f.get("severity", "low")
        if sev in counts:
            counts[sev] += 1
        else:
            counts["low"] += 1
    return {"n_findings": len(findings), "by_severity": counts}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    print("Entering lambda_handler")
    """Lambda handler for compliance checks.

    Expected input (from ingestion):
    {
      "status": "ok",
      "contract_id": "...",
      "s3": {"bucket": "...", "key": "..."},
      "extracted_text": "...",
      "extracted_lines": ["..."],
      "metadata": {"n_lines": X, "n_chars": Y}
    }

    Returns structured findings and an optional bedrock result.
    """
    logger.info("Compliance handler received event")

    # Basic validation
    if not isinstance(event, dict):
        return {"status": "error", "message": "Event must be a JSON object"}

    contract_id = event.get("contract_id") or ""
    s3_info = event.get("s3") or {}
    bucket = s3_info.get("bucket")
    key = s3_info.get("key")
    text = event.get("extracted_text") or ""

    missing = []
    if not contract_id:
        missing.append("contract_id")
    if not bucket:
        missing.append("s3.bucket")
    if not key:
        missing.append("s3.key")
    if not text:
        missing.append("extracted_text")
    if missing:
        msg = "Missing required fields: " + ", ".join(missing)
        logger.error(msg)
        return {"status": "error", "message": msg}

    findings: List[Dict[str, Any]] = []
    bedrock_used = False
    bedrock_resp: Optional[Dict[str, Any]] = None

    # If configured to use Bedrock, try it first for advanced parsing
    # Default to off for local development
    use_bedrock = os.environ.get("USE_BEDROCK", "true").lower() in ("1", "true", "yes")
    if use_bedrock:
        try:
            bedrock_resp = _call_bedrock_for_checks(text)
            # If bedrock returned structured fields, try to merge them into findings
            if bedrock_resp and bedrock_resp.get("result"):
                parsed = bedrock_resp["result"]
                # Expect parsed to contain 'pii' and 'issues' lists; adapt if different
                for p in parsed.get("pii", []) if isinstance(parsed.get("pii"), list) else []:
                    findings.append({"rule_id": "gdpr_pii_bedrock", "detail": p, "severity": "high"})
                for it in parsed.get("issues", []) if isinstance(parsed.get("issues"), list) else []:
                    findings.append({"rule_id": "sox_or_other_bedrock", "detail": it, "severity": it.get("severity", "medium") if isinstance(it, dict) else "medium"})
                bedrock_used = True
        except Exception as e:
            logger.warning("Bedrock check failed, falling back to local rules: %s", e)

    # Always run local rules (they can complement or serve as fallback)
    try:
        findings.extend(_local_pii_checks(text))
        findings.extend(_local_sox_checks(text))
    except Exception:
        logger.exception("Local checks failed")

    summary = _summarize_findings(findings)

    result = {
        "status": "ok",
        "contract_id": contract_id,
        "s3": {"bucket": bucket, "key": key},
        "findings": findings,
        "summary": summary,
        "bedrock_used": bedrock_used,
        "bedrock_response": bedrock_resp,
    }

    logger.info("Compliance check complete for %s: %s", contract_id, json.dumps(summary))
    return result


# Export a simple alias expected by other scripts
handler = lambda_handler

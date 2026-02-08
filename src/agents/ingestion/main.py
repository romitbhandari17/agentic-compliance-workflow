import os
import time
import logging
import uuid
from typing import Dict, Any, List
import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

# Set default session so subsequent boto3.client() calls inherit the region
boto3.setup_default_session(region_name="us-west-2")
s3_client = boto3.client("s3")
textract_client = boto3.client("textract")


def _get_extension(key: str) -> str:
    _, ext = os.path.splitext(key or "")
    return ext.lower()


def _extract_lines_from_blocks(blocks: List[Dict[str, Any]]) -> List[str]:
    lines = []
    for b in blocks:
        if b.get("BlockType") == "LINE" and "Text" in b:
            lines.append(b["Text"])
    return lines


def _detect_text_sync(bucket: str, key: str) -> List[str]:
    # Download object bytes
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read()
    # Call Textract synchronous API (suitable for images)
    resp = textract_client.detect_document_text(Document={"Bytes": body})
    blocks = resp.get("Blocks", [])
    return _extract_lines_from_blocks(blocks)


def _start_text_detection_async(bucket: str, key: str) -> str:
    resp = textract_client.start_document_text_detection(
        DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}}
    )
    return resp["JobId"]


def _get_text_detection_results(job_id: str, wait_seconds: int = 60, poll_interval: float = 2.0) -> List[str]:
    started = time.time()
    next_token = None
    all_lines: List[str] = []

    # Poll for job completion
    while True:
        try:
            if next_token:
                resp = textract_client.get_document_text_detection(JobId=job_id, NextToken=next_token)
            else:
                resp = textract_client.get_document_text_detection(JobId=job_id)
        except (BotoCoreError, ClientError) as e:
            logger.exception("Error getting Textract job result")
            raise

        status = resp.get("JobStatus")
        logger.debug("Textract job %s status: %s", job_id, status)

        if status == "SUCCEEDED":
            blocks = resp.get("Blocks", [])
            all_lines.extend(_extract_lines_from_blocks(blocks))
            next_token = resp.get("NextToken")
            # Continue pagination if NextToken present
            if next_token:
                continue
            break
        elif status == "FAILED":
            raise RuntimeError(f"Textract job {job_id} failed")
        else:
            # IN_PROGRESS or unknown: check timeout
            if time.time() - started > wait_seconds:
                raise TimeoutError(f"Textract job {job_id} did not complete within {wait_seconds} seconds")
            time.sleep(poll_interval)

    return all_lines


def extract_text_from_s3(bucket: str, key: str) -> Dict[str, Any]:
    ext = _get_extension(key)
    logger.info("Extracting text from s3://%s/%s (ext=%s)", bucket, key, ext)

    # Treat PDFs as async jobs; images as synchronous.
    try:
        if ext == ".pdf":
            job_id = _start_text_detection_async(bucket, key)
            logger.info("Started Textract job %s for %s/%s", job_id, bucket, key)
            lines = _get_text_detection_results(job_id)
        else:
            lines = _detect_text_sync(bucket, key)
    except Exception as e:
        logger.exception("Text extraction failed")
        raise

    text = "\n".join(lines)
    return {
        "n_lines": len(lines),
        "n_chars": len(text),
        "lines": lines,
        "text": text,
    }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Expected event:
    {
      "contract_id": "abc-123",
      "s3": { "bucket": "my-bucket", "key": "contracts/abc.pdf" },
      ... optional metadata ...
    }
    """
    logger.info("Received event: %s", event)
    contract_id = event.get("contract_id")
    s3_info = event.get("s3") or {}
    bucket = s3_info.get("bucket")
    key = s3_info.get("key")

    if not contract_id:
            contract_id = str(uuid.uuid4())
    elif not bucket or not key:
        msg = "Missing required fields: s3.bucket, s3.key"
        logger.error(msg)
        return {"status": "error", "message": msg}

    try:
        extraction = extract_text_from_s3(bucket, key)
    except Exception as e:
        return {"status": "error", "message": str(e), "contract_id": contract_id, "s3": s3_info}

    # Return payload consumable by compliance lambda
    result = {
        "status": "ok",
        "contract_id": contract_id,
        "s3": {"bucket": bucket, "key": key},
        "extracted_text": extraction["text"],
        "extracted_lines": extraction["lines"],
        "metadata": {
            "n_lines": extraction["n_lines"],
            "n_chars": extraction["n_chars"],
        },
    }
    logger.info("Extraction complete for %s: %d lines, %d chars", contract_id, extraction["n_lines"], extraction["n_chars"])
    return result

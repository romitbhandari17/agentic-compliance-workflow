#!/usr/bin/env python3
"""Trigger script: start the Step Functions state machine which triggers ingestion.

By default this script will call AWS Step Functions StartExecution. To run
locally (skip SFN and call ingestion handler directly) set LOCAL=1.

Environment variables:
  ENV (default: dev)
  PROJECT (default: repo folder name)
  S3_KEY (default: contracts/contract.pdf)
  CONTRACT_ID (optional)
  STATE_MACHINE_ARN (required unless LOCAL=1)
  AWS_REGION or AWS_DEFAULT_REGION (optional)
  LOCAL=1 to bypass SFN and call the handler directly

Usage:
  STATE_MACHINE_ARN=arn:... python src/scripts/trigger_ingestion_local.py
  LOCAL=1 python src/scripts/trigger_ingestion_local.py
"""

import sys
import os
import json
from pathlib import Path
from typing import Any, Dict

# Make repo root importable so `src` package can be resolved
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Configuration
event = {
    "contract_id": "",
    "s3": {"bucket": "agentic-compliance-workflow-dev-s3-artifacts", "key": "contracts/contract.pdf"},
    # add optional metadata here if needed
}

STATE_MACHINE_ARN = "arn:aws:states:us-west-2:968239734180:stateMachine:agentic-compliance-workflow-dev-state-machine"
LOCAL = ""

def main():
    print("Triggering Step Functions state machine with event:\n", json.dumps(event, indent=2))

    if LOCAL:
        print("LOCAL=1 set: calling ingestion handler directly (no Step Functions)")
        try:
            from src.agents.ingestion.main import handler as ingestion_handler
        except Exception as e:
            print("Failed to import ingestion handler:\n", e, file=sys.stderr)
            raise

        try:
            result = ingestion_handler(event, None)
        except Exception as e:
            print("Handler raised an exception:\n", e, file=sys.stderr)
            raise

        print("Handler result:\n", json.dumps(result, indent=2))
        return

    # Default: require STATE_MACHINE_ARN and start a Step Functions execution
    if not STATE_MACHINE_ARN:
        msg = (
            "STATE_MACHINE_ARN is required when not running in LOCAL mode. "
            "Set the environment variable STATE_MACHINE_ARN to the state machine ARN."
        )
        print(msg, file=sys.stderr)
        raise SystemExit(2)

    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except Exception as e:  # pragma: no cover - boto3 runtime availability
        print("boto3 is required to trigger Step Functions.\n", e, file=sys.stderr)
        raise

    # Create session and client
    session = boto3.Session()
    sfn = session.client("stepfunctions")

    # Start execution
    try:
        resp = sfn.start_execution(stateMachineArn=STATE_MACHINE_ARN, input=json.dumps(event))
        print("Started execution:", json.dumps(resp, indent=2, default=str))
    except ClientError as e:
        print("Failed to start Step Functions execution:\n", e, file=sys.stderr)
        raise
    except BotoCoreError as e:
        print("BotoCore error starting execution:\n", e, file=sys.stderr)
        raise


if __name__ == "__main__":
    main()


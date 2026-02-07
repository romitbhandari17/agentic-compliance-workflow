from agentic_risk_automation import __version__
from agentic_risk_automation.workflows.risk_workflow import RiskWorkflow


def test_version():
    assert __version__ == "0.1.0"


def test_workflow_run():
    wf = RiskWorkflow()
    report = wf.run()
    assert "agent_result" in report
    assert report["summary"]["n_items"] == 3

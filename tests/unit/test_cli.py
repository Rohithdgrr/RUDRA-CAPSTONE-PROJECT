from typer.testing import CliRunner
from src.cli import app
from pathlib import Path

runner = CliRunner()

def test_faults():
    r = runner.invoke(app, ["faults"])
    assert r.exit_code == 0
    assert "SF-01" in r.output

def test_platforms():
    r = runner.invoke(app, ["platforms"])
    assert r.exit_code == 0
    assert "stm32f4" in r.output

def test_campaign_cli(tmp_path):
    r = runner.invoke(app, ["campaign", "--config", "campaigns/sensor_suite.yaml", "--parallel", "1", "--output", str(tmp_path)])
    assert r.exit_code == 0
    assert "Grade" in r.output
    assert list(tmp_path.glob("*.json"))

def test_validator():
    from src.config.validator import validate_file
    cfg = validate_file("campaigns/sensor_suite.yaml")
    assert cfg.name == "Sensor Suite Validation"

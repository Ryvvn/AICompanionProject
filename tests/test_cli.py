import pytest
from typer.testing import CliRunner
from bananalyzer.cli import app

runner = CliRunner()

def test_help_displays_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout
    assert "status" in result.stdout
    assert "dashboard" in result.stdout
    assert "diagnose" in result.stdout
    assert "config" in result.stdout

def test_config_command(mocker):
    # Mock Settings and ModelProfiles to avoid reading real files
    mocker.patch("bananalyzer.cli.Settings")
    mocker.patch("bananalyzer.cli.ModelProfiles")
    mocker.patch("bananalyzer.cli.Thresholds")
    
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert "Active Configuration" in result.stdout

def test_status_command(mocker):
    # Mock pathlib paths
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("json.load", side_effect=[
        {"state": "coding"},
        {"service": {"status": "ok"}}
    ])
    
    mocker.patch("bananalyzer.cli.ModelProfiles", return_value=mocker.Mock(default_model="test-model"))
    
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "Current State" in result.stdout
    assert "Integration Health" in result.stdout

def test_diagnose_command(mocker):
    # Mock pathlib paths
    mocker.patch("pathlib.Path.exists", return_value=True)
    
    result = runner.invoke(app, ["diagnose"])
    assert result.exit_code == 0
    assert "Diagnostic Report" in result.stdout
    assert "Data Dir exists" in result.stdout

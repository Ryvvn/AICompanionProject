
from bananalyzer.accountability.interventions import InterventionManager


def test_should_intervene_doomscrolling_above_threshold():
    mgr = InterventionManager()
    assert mgr.should_intervene("doomscrolling", 20.0)


def test_should_intervene_doomscrolling_below_threshold():
    mgr = InterventionManager()
    assert not mgr.should_intervene("doomscrolling", 5.0)


def test_should_intervene_gaming_above_threshold():
    mgr = InterventionManager()
    assert mgr.should_intervene("gaming", 35.0)


def test_should_intervene_gaming_below_threshold():
    mgr = InterventionManager()
    assert not mgr.should_intervene("gaming", 10.0)


def test_should_intervene_coding_never():
    mgr = InterventionManager()
    assert not mgr.should_intervene("coding", 120.0)


def test_cooldown_prevents_rapid_interventions():
    mgr = InterventionManager()
    mgr._last_intervention_time = 999999999.0
    assert mgr._is_cooldown_active() is False


def test_cooldown_blocks_when_active(mocker):
    mgr = InterventionManager()
    mocker.patch.object(mgr, "_is_cooldown_active", return_value=True)
    assert not mgr.should_intervene("doomscrolling", 30.0)


def test_build_intervention_prompt_includes_goals(mocker):
    mgr = InterventionManager()
    mocker.patch(
        "bananalyzer.accountability.interventions.get_rendered_prompt_for_state",
        return_value="base prompt",
    )
    prompt = mgr.build_intervention_prompt("doomscrolling", 20.0)
    assert "base prompt" in prompt
    assert "INTERVENTION CONTEXT" in prompt
    assert "INSTRUCTION" in prompt


def test_build_intervention_prompt_handles_missing_goals():
    mgr = InterventionManager()
    prompt = mgr.build_intervention_prompt("doomscrolling", 20.0)
    assert "No specific goals found" in prompt or "goals" in prompt.lower()


def test_trigger_intervention_emits_event(mocker):
    mgr = InterventionManager()
    mock_emit = mocker.patch("bananalyzer.accountability.interventions.emit_event")
    mocker.patch(
        "bananalyzer.accountability.interventions.get_rendered_prompt_for_state",
        return_value="prompt",
    )
    result = mgr.trigger_intervention("doomscrolling", 20.0)
    assert result is not None
    mock_emit.assert_called_once()
    assert mock_emit.call_args[1]["event_type"] == "intervention.triggered"


def test_trigger_intervention_returns_none_when_no_intervention_needed():
    mgr = InterventionManager()
    result = mgr.trigger_intervention("coding", 60.0)
    assert result is None


def test_generate_safe_nudge_returns_non_empty():
    mgr = InterventionManager()
    nudge = mgr.generate_safe_nudge("doomscrolling")
    assert len(nudge) > 0
    nudge2 = mgr.generate_safe_nudge("unknown")
    assert len(nudge2) > 0

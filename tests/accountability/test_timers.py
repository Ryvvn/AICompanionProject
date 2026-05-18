from pathlib import Path

from bananalyzer.accountability.timers import StateTimeTracker


def test_tracker_initializes_with_zero_totals(tmp_path: Path):
    state_dir = tmp_path / "state"
    tracker = StateTimeTracker(state_dir=state_dir)
    totals = tracker.get_totals()
    assert totals["coding"] == 0.0
    assert totals["gaming"] == 0.0
    assert totals["doomscrolling"] == 0.0
    assert totals["companion"] == 0.0
    assert totals["fallback"] == 0.0


def test_tracker_records_state_change_and_accumulates(tmp_path: Path, mocker):
    state_dir = tmp_path / "state"
    tracker = StateTimeTracker(state_dir=state_dir)

    tracker.record_state_change("coding", "2026-05-10T10:00:00")
    mocker.patch.object(tracker, "resolve_elapsed", return_value=60.0)
    tracker.record_state_change("gaming", "2026-05-10T10:01:00")

    totals = tracker.get_totals()
    assert totals["coding"] == 60.0


def test_tracker_persists_across_instances(tmp_path: Path, mocker):
    state_dir = tmp_path / "state"
    tracker1 = StateTimeTracker(state_dir=state_dir)
    tracker1.record_state_change("coding", "2026-05-10T10:00:00")
    mocker.patch.object(tracker1, "resolve_elapsed", return_value=120.0)
    tracker1.record_state_change("doomscrolling", "2026-05-10T10:02:00")
    tracker1.record_state_change("coding", "2026-05-10T10:04:00")

    tracker2 = StateTimeTracker(state_dir=state_dir)
    totals = tracker2.get_totals()
    assert totals["coding"] > 0
    assert totals["doomscrolling"] > 0


def test_tracker_get_totals_display_formats(tmp_path: Path):
    state_dir = tmp_path / "state"
    tracker = StateTimeTracker(state_dir=state_dir)
    tracker.record_state_change("coding")
    display = tracker.get_totals_display()
    assert "coding" in display
    assert "gaming" in display


def test_tracker_handles_corrupted_state_file(tmp_path: Path):
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "activity_time.json").write_text("not valid json", encoding="utf-8")

    tracker = StateTimeTracker(state_dir=state_dir)
    totals = tracker.get_totals()
    assert totals["coding"] == 0.0


def test_tracker_handles_missing_state_file(tmp_path: Path):
    state_dir = tmp_path / "nonexistent_d3f4"
    tracker = StateTimeTracker(state_dir=state_dir)
    totals = tracker.get_totals()
    assert totals["coding"] == 0.0


def test_tracker_reset_clears_all(tmp_path: Path):
    state_dir = tmp_path / "state"
    tracker = StateTimeTracker(state_dir=state_dir)
    tracker.record_state_change("coding", "2026-05-10T10:00:00")
    tracker.record_state_change("gaming", "2026-05-10T10:01:00")
    tracker.reset()
    totals = tracker.get_totals()
    assert totals["coding"] == 0.0
    assert totals["gaming"] == 0.0

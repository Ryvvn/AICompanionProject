from pathlib import Path

from bananalyzer.accountability.banana_debt import BananaDebtCalculator


def test_calculate_debt_formula():
    calc = BananaDebtCalculator()
    debt = calc.calculate(coding_minutes=30, gaming_minutes=10, doomscrolling_minutes=5)
    assert debt >= 0.0
    assert debt <= 30.0


def test_calculate_debt_only_coding_gives_zero():
    calc = BananaDebtCalculator()
    debt = calc.calculate(coding_minutes=60, gaming_minutes=0, doomscrolling_minutes=0)
    assert debt == 0.0


def test_calculate_debt_never_negative():
    calc = BananaDebtCalculator()
    debt = calc.calculate(coding_minutes=0, gaming_minutes=0, doomscrolling_minutes=0)
    assert debt >= 0.0


def test_update_debt_writes_and_returns_data(tmp_path: Path):
    calc = BananaDebtCalculator(memory_dir=tmp_path)
    result = calc.update_debt(coding_minutes=20, gaming_minutes=15, doomscrolling_minutes=10)
    assert "current_debt" in result
    assert "breakdown" in result
    assert result["breakdown"]["coding_minutes"] == 20
    assert (tmp_path / "banana_debt.json").exists()


def test_get_current_debt_returns_empty_for_no_file():
    calc = BananaDebtCalculator(memory_dir=Path("/nonexistent_xyz_banana_test"))
    result = calc.get_current_debt()
    assert result == {}


def test_degraded_mode_when_write_fails(tmp_path: Path, mocker):
    calc = BananaDebtCalculator(memory_dir=tmp_path)
    mocker.patch.object(calc, "_write_debt", return_value=False)
    result = calc.update_debt(coding_minutes=10, gaming_minutes=5, doomscrolling_minutes=2)
    assert "current_debt" in result


def test_debt_persists_across_instances(tmp_path: Path):
    calc1 = BananaDebtCalculator(memory_dir=tmp_path)
    calc1.update_debt(coding_minutes=0, gaming_minutes=10, doomscrolling_minutes=5)

    calc2 = BananaDebtCalculator(memory_dir=tmp_path)
    data = calc2.get_current_debt()
    assert data["current_debt"] > 0

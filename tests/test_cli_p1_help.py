import pytest

from skillloop.cli import main


def test_p1_help_exposes_coordinate_contract_without_fixed_workbook_answers(capsys):
    with pytest.raises(SystemExit) as result:
        main(['run-p1', '--help'])
    assert result.value.code == 0
    output = capsys.readouterr().out
    for term in ('sheet', 'month_col', 'total_col', 'first_row', '1-based',
                 'integer', '절대 좌표', 'month_col != total_col', 'chart_ref'):
        assert term in output
    assert 'NEEDS_AGENT_DISCOVERY' in output and 'NEEDS_TASK_MAPPING' in output
    assert 'AAAAA01' not in output and '1650' not in output

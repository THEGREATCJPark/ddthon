"""CLI operational errors fail clearly without rewriting data or hiding bugs."""
import subprocess

import pytest

from skillloop import cli


def test_malformed_store_reports_error_without_rewriting(tmp_path, capsys):
    store = tmp_path / 'store.json'
    store.write_text('{', encoding='utf-8')
    assert cli.main(['match', '--signature', 'test-failure', '--store', str(store)]) == 2
    output = capsys.readouterr()
    assert 'JSONDecodeError' in output.err
    assert 'Traceback' not in output.err
    assert store.read_bytes() == b'{'
    assert list(tmp_path.iterdir()) == [store]


@pytest.mark.parametrize('error', [
    PermissionError('store not readable'),
    subprocess.TimeoutExpired(['pip', '--version'], 1),
    RuntimeError('clean environment required'),
])
def test_operational_failure_is_nonzero(monkeypatch, capsys, error):
    def fail():
        raise error
    monkeypatch.setattr(cli, 'run_p0', fail)
    assert cli.main(['run-p0']) == 2
    assert type(error).__name__ in capsys.readouterr().err


@pytest.mark.parametrize('error', [TypeError('programming defect'), AssertionError('invariant'), KeyboardInterrupt()])
def test_unexpected_errors_and_interrupts_propagate(monkeypatch, error):
    def fail():
        raise error
    monkeypatch.setattr(cli, 'run_p0', fail)
    with pytest.raises(type(error)):
        cli.main(['run-p0'])


def test_command_result_and_argparse_help_preserved(monkeypatch):
    monkeypatch.setattr(cli, 'run_p0', lambda: 7)
    assert cli.main(['run-p0']) == 7
    with pytest.raises(SystemExit) as exc:
        cli.main(['--help'])
    assert exc.value.code == 0

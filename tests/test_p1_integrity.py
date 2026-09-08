from types import SimpleNamespace

from skillloop import envharness_p1 as h, replay
from skillloop.descriptor import make_descriptor


def candidate():
    return make_descriptor({'id': 'access', 'version': '1', 'origin': {'author': 'test'},
                            'applicability': {'signals': ['file-access-fail:xlsx']},
                            'procedure': {'action': 'file-access', 'method': 'excel-com-attach'}})


def test_digest_mismatch_blocks_before_any_read(monkeypatch):
    c = candidate()
    c.procedure['sheet'] = 2
    monkeypatch.setattr(replay, 'run_file_access_procedure', lambda *a: (_ for _ in ()).throw(AssertionError('must not read')))
    result = replay.replay(c, h.EnvContext('unused', True))
    assert result.verdict == 'FAIL'
    assert result.evidence['ran'] is False


def test_missing_file_hash_cannot_claim_unchanged(tmp_path, monkeypatch):
    monkeypatch.setattr(h, '_read_via_excel_attach', lambda *a: [('2026-01', 1), ('2026-02', 2), ('2026-03', 3)])
    result = h.run_file_access_procedure(candidate().procedure, h.EnvContext(str(tmp_path / 'missing'), True))
    assert not result.ok
    assert result.evidence['original_unchanged'] is False


def test_cleanup_closes_only_owned_workbook_and_keeps_other_open():
    calls = []
    class Book:
        def Close(self, **kw): calls.append(('owned-close', kw))
    class Excel:
        Workbooks = SimpleNamespace(Count=1)
        def Quit(self): calls.append('quit')
    h._excel_app, h._excel_book, h._active = Excel(), Book(), None
    h.teardown()
    assert calls == [('owned-close', {'SaveChanges': False})]
    assert h._excel_app is None and h._excel_book is None


def test_invalid_action_never_reads(monkeypatch):
    monkeypatch.setattr(h, '_read_via_excel_attach', lambda *a: (_ for _ in ()).throw(AssertionError('must not read')))
    assert not h.run_file_access_procedure({'action': 'execute-script'}, h.EnvContext('unused', True)).ok


def test_no_excel_placeholder_is_not_office_encryption(monkeypatch):
    monkeypatch.setattr(h, '_try_com_create_encrypted', lambda *a: False)
    e = h.setup_encrypted_open_xlsx_env([], 'synthetic-only')
    try:
        assert e.present_facts['file_state'] == 'non-office-placeholder'
        assert not e.app_running
    finally:
        h.teardown()

"""Operator preparation contracts using a COM double; not real Excel evidence."""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

import pytest


def load_prepare():
    spec = importlib.util.spec_from_file_location('operator_prepare',
        Path(__file__).resolve().parents[1] / 'scripts/prepare-p1.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('custom_password', [None, 'operator-demo1'])
def test_operator_password_is_only_used_for_save_not_exposed(tmp_path, monkeypatch, capsys, custom_password):
    prep = load_prepare()
    books = []
    password = custom_password or prep.DEMO_PASSWORD
    class Book:
        def __init__(self):
            self.closed = self.activated = False
            self.sheet = SimpleNamespace(Cells=lambda *a: SimpleNamespace(),
                                         Range=lambda *a: SimpleNamespace())
        def Worksheets(self, index): return self.sheet
        def SaveAs(self, path, **kwargs): self.saved_password = kwargs['Password']
        def Activate(self): self.activated = True
        def Close(self, **kwargs): self.closed = True
    class Collection:
        def Add(self):
            book = Book(); books.append(book); return book
        @property
        def Count(self): return sum(not b.closed for b in books)
    app = SimpleNamespace(Workbooks=Collection(), Hwnd=1, Quit=lambda: None)
    client = ModuleType('win32com.client'); client.DispatchEx = lambda _: app
    package = ModuleType('win32com'); package.client = client
    process = ModuleType('win32process'); process.GetWindowThreadProcessId = lambda _: (1, 42)
    monkeypatch.setitem(sys.modules, 'win32com', package)
    monkeypatch.setitem(sys.modules, 'win32com.client', client)
    monkeypatch.setitem(sys.modules, 'win32process', process)
    dest = tmp_path / 'new-work'
    monkeypatch.setattr(prep.time, 'sleep', lambda _: (dest / 'STOP').touch())
    prep.prepare(dest, operator_password=custom_password)
    assert len(books) == 2 and all(b.saved_password == password for b in books)
    assert books[0].activated and app.Visible
    assert all(b.closed for b in books)
    output = capsys.readouterr().out
    if custom_password:
        assert password not in output
    else:
        assert password == 'nowhere' and 'nowhere' in output
    for path in dest.rglob('*'):
        if path.is_file(): assert password.encode() not in path.read_bytes()
    import json
    context = json.loads((dest / 'cold/.skillloop/context.json').read_text(encoding='utf-8'))
    assert context['display_label'] == 'NASCA 보안 프로그램'
    assert context['virtual'] is True
    assert context['diagnosis_source'] == 'demo-scenario-configuration'
    assert 'method' not in context and 'password' not in context
    # The test double does not write an XLSX. Do not claim encryption/Excel PASS.


@pytest.mark.parametrize('answers', [('',), ('first-private', 'different'), ('a' * 16,)])
def test_invalid_hidden_password_not_echoed(answers, monkeypatch, capsys):
    prep = load_prepare()
    monkeypatch.setattr(prep.sys, 'stdin', SimpleNamespace(isatty=lambda: True))
    responses = iter(answers)
    monkeypatch.setattr(prep.getpass, 'getpass', lambda _: next(responses))
    with pytest.raises(ValueError) as error:
        prep.read_operator_password()
    for value in answers:
        if value: assert value not in str(error.value) + capsys.readouterr().out


def test_empty_password_rejected_before_environment_creation(tmp_path):
    prep = load_prepare()
    dest = tmp_path / 'untouched'
    with pytest.raises(ValueError, match='Empty password'):
        prep.prepare(dest, operator_password='')
    assert not dest.exists()


def test_noninteractive_password_input_rejected_before_prompt(monkeypatch):
    prep = load_prepare()
    monkeypatch.setattr(prep.sys, 'stdin', SimpleNamespace(isatty=lambda: False))
    def forbidden(*args): raise AssertionError('Must not fall back to echoed input')
    monkeypatch.setattr(prep.getpass, 'getpass', forbidden)
    with pytest.raises(RuntimeError, match='interactive terminal'):
        prep.read_operator_password()

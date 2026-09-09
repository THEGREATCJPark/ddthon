"""Real offline installation: same environment Skill, two different task packages."""
import json
import subprocess
import sys
import zipfile
from pathlib import Path

from skillloop.cli import apply_requirements
from skillloop.descriptor import make_descriptor
from skillloop.store import SkillStore


def wheel(destination, name, version):
    module = name.replace('-', '_')
    dist = f'{module}-{version}.dist-info'
    files = {
        f'{module}/__init__.py': f'VALUE = {version!r}\n',
        f'{dist}/METADATA': f'Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n',
        f'{dist}/WHEEL': 'Wheel-Version: 1.0\nGenerator: SkillLoop test\nRoot-Is-Purelib: true\nTag: py3-none-any\n',
    }
    files[f'{dist}/RECORD'] = ''.join(f'{path},,\n' for path in files) + f'{dist}/RECORD,,\n'
    with zipfile.ZipFile(destination / f'{module}-{version}-py3-none-any.whl', 'w') as archive:
        for path, content in files.items(): archive.writestr(path, content)


def test_two_task_packages_reuse_same_environment_skill(tmp_path, capsys):
    source = tmp_path / 'approved-source'; source.mkdir()
    failing = tmp_path / 'empty-source'; failing.mkdir()
    packages = [('example-alpha', '1.2.0'), ('example-beta', '2.3.0')]
    for name, version in packages: wheel(source, name, version)
    descriptor = make_descriptor({'id': 'internal-python-source', 'version': '1',
        'origin': {'author': 'test-operator'}, 'applicability': {'signals': ['pip-install-fail']},
        'procedure': {'action': 'pip-install', 'source': 'internal'}})
    for index, (name, version) in enumerate(packages):
        folder = tmp_path / f'work-{index}'; folder.mkdir()
        subprocess.run([sys.executable, '-m', 'venv', str(folder / '.venv')], check=True, capture_output=True)
        python = folder / '.venv' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
        config = folder / '.venv' / ('pip.ini' if sys.platform == 'win32' else 'pip.conf')
        config.write_text(f'[global]\nno-index=true\nfind-links={failing.resolve().as_uri()}\ndisable-pip-version-check=true\n', encoding='utf-8')
        req = folder / 'requirements.txt'; req.write_text(f'{name}=={version}\n', encoding='utf-8')
        store = folder / 'store.json'; SkillStore(str(store)).put(descriptor)
        usage = folder / 'usage.json'; policy = folder / 'policy.json'
        policy.write_text(json.dumps({'approved_skills': [{k: getattr(descriptor, k) for k in ('id', 'version', 'digest')}],
            'sources': {'internal': str(source)}, 'imports': {name: name.replace('-', '_')}}), encoding='utf-8')
        assert apply_requirements(str(req), str(python), str(store), str(usage), f'run-{index}', str(policy)) == 0
        output = capsys.readouterr().out
        assert 'install exit=1' in output and 'counted=True' in output
        probe = subprocess.run([str(python), '-c', 'import importlib,sys;print(importlib.import_module(sys.argv[1]).VALUE)', name.replace('-', '_')], capture_output=True, text=True)
        assert probe.returncode == 0 and probe.stdout.strip() == version
        data = json.loads(usage.read_text())
        assert sum(data['counts'].values()) == 1
        assert SkillStore(str(store)).list()[0].digest == descriptor.digest
        # Already installed: regular pip success must not manufacture a second reuse.
        assert apply_requirements(str(req), str(python), str(store), str(usage), f'again-{index}', str(policy)) == 0
        assert sum(json.loads(usage.read_text())['counts'].values()) == 1

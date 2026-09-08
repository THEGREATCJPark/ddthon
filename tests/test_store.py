"""V3, V4 — CONFLICT 판정·DEDUP 카운트 무변경. 소유: CJ. 구현: S3."""

from skillloop import descriptor as D
from skillloop.store import SkillStore


def _mk(idv="pkg-fix", ver="1.0.0", proc=None, reuse=0, seed=False):
    content = {
        "id": idv,
        "version": ver,
        "origin": {"author": "test"},
        "applicability": {"signals": ["pip-install-fail"]},
        "procedure": proc if proc is not None else {"index": "allow"},
    }
    return D.make_descriptor(content, actual_reuse=reuse, demo_seed=seed)


def test_store_and_get_roundtrip(tmp_path):
    s = SkillStore(str(tmp_path / "store.json"))
    d = _mk()
    assert s.put(d).result == "STORED"
    got = s.get("pkg-fix", "1.0.0")
    assert got == d


def test_dedup_same_id_version_same_digest(tmp_path):
    s = SkillStore(str(tmp_path / "store.json"))
    d = _mk()
    assert s.put(d).result == "STORED"
    assert s.put(_mk()).result == "DEDUP"
    assert len(s.list()) == 1


def test_conflict_same_id_version_different_digest(tmp_path):
    # V3: 동일 (id,version) + 다른 digest = CONFLICT. 덮어쓰지 않음.
    s = SkillStore(str(tmp_path / "store.json"))
    first = _mk(proc={"index": "allow"})
    second = _mk(proc={"index": "other"})  # 다른 절차 → 다른 digest
    assert first.digest != second.digest
    assert s.put(first).result == "STORED"
    r = s.put(second)
    assert r.result == "CONFLICT"
    # 기존 레코드는 그대로(덮어쓰기 없음)
    assert s.get("pkg-fix", "1.0.0") == first


def test_different_version_is_not_conflict(tmp_path):
    # V3: 다른 version은 CONFLICT 아님 — 독립 저장.
    s = SkillStore(str(tmp_path / "store.json"))
    assert s.put(_mk(ver="1.0.0")).result == "STORED"
    assert s.put(_mk(ver="2.0.0")).result == "STORED"
    assert len(s.list()) == 2


def test_dedup_does_not_change_usage_or_count(tmp_path):
    # V4: DEDUP은 usage 병합·actual_reuse 변경 없음(기존 레코드 유지).
    s = SkillStore(str(tmp_path / "store.json"))
    s.put(_mk(reuse=5, seed=False))
    # 같은 content, 다른 usage로 재put → DEDUP, 기존 usage 유지
    r = s.put(_mk(reuse=999, seed=True))
    assert r.result == "DEDUP"
    kept = s.get("pkg-fix", "1.0.0")
    assert kept.actual_reuse == 5
    assert kept.demo_seed is False

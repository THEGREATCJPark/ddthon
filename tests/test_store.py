"""V3, V4 — CONFLICT 판정·DEDUP 카운트 무변경 + C-a/C-b 공유 계약. 소유: CJ."""

import json

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


# --- C-b: descriptor 공유 export/import ---

def _ref(d):
    return {"id": d.id, "version": d.version, "digest": d.digest}


def test_export_bundle_only_judged_refs_not_all(tmp_path):
    # C-b: export는 전달받은 정확한 refs만(전체 항목 아님). content만·usage 제외.
    s = SkillStore(str(tmp_path / "store.json"))
    a = _mk(idv="a", proc={"index": "allow"}, reuse=3)
    b = _mk(idv="b", proc={"index": "allow"})
    s.put(a)
    s.put(b)
    blob = s.export_bundle([_ref(a)])  # a만 허용목록
    data = json.loads(blob.decode("utf-8"))
    assert len(data["skills"]) == 1
    item = data["skills"][0]
    assert item["content"]["id"] == "a"
    # content만 — usage(actual_reuse/demo_seed) 미포함
    assert "actual_reuse" not in item["content"]
    assert "demo_seed" not in item["content"]


def test_export_bundle_excludes_digest_mismatch(tmp_path):
    # C-b: 판정 대상과 로컬 저장본의 digest 불일치는 export에서 제외(무결성).
    s = SkillStore(str(tmp_path / "store.json"))
    a = _mk(idv="a")
    s.put(a)
    bad = {"id": "a", "version": "1.0.0", "digest": "deadbeef"}  # 위조 digest
    assert json.loads(s.export_bundle([bad]).decode("utf-8"))["skills"] == []
    # 미존재 참조도 제외
    assert json.loads(
        s.export_bundle([{"id": "z", "version": "9.9", "digest": a.digest}]).decode("utf-8")
    )["skills"] == []


def test_import_bundle_roundtrip_content_only(tmp_path):
    # C-b: export→import 왕복이 content 기준으로 동일 descriptor를 저장(STORED).
    src = SkillStore(str(tmp_path / "src.json"))
    a = _mk(idv="a", reuse=9)  # 원본은 usage 보유
    src.put(a)
    blob = src.export_bundle([_ref(a)])

    dst = SkillStore(str(tmp_path / "dst.json"))
    results = dst.import_bundle(blob)
    assert [r.result for r in results] == ["STORED"]
    got = dst.get("a", "1.0.0")
    assert got.digest == a.digest
    # 원격 usage는 전달되지 않음 — content만 반영
    assert got.actual_reuse == 0 and got.demo_seed is False


def test_import_bundle_dedup_and_conflict(tmp_path):
    # C-b: 동일 id/version+동일 digest=DEDUP, 다른 digest=CONFLICT.
    dst = SkillStore(str(tmp_path / "dst.json"))
    a = _mk(idv="a", proc={"index": "allow"})
    dst.put(a)
    src = SkillStore(str(tmp_path / "src.json"))
    src.put(a)
    assert dst.import_bundle(src.export_bundle([_ref(a)]))[0].result == "DEDUP"

    conflicting = _mk(idv="a", proc={"index": "other"})  # 같은 id/ver, 다른 digest
    src2 = SkillStore(str(tmp_path / "src2.json"))
    src2.put(conflicting)
    r = dst.import_bundle(src2.export_bundle([_ref(conflicting)]))
    assert r[0].result == "CONFLICT"
    # 기존 저장본 불변(덮어쓰기 없음)
    assert dst.get("a", "1.0.0").digest == a.digest


def test_import_bundle_rejects_forged_digest(tmp_path):
    # C-b: 선언 digest와 content 재계산이 다르면 거부(위조 방지).
    dst = SkillStore(str(tmp_path / "dst.json"))
    a = _mk(idv="a")
    forged = json.dumps({
        "skills": [{
            "content": {k: getattr(a, k) for k in
                        ("id", "version", "origin", "applicability", "procedure")},
            "declared_digest": "0" * 64,  # content와 불일치
        }]
    }).encode("utf-8")
    r = dst.import_bundle(forged)
    assert r[0].result == "CONFLICT" and "mismatch" in r[0].reason
    assert dst.get("a", "1.0.0") is None  # 반영 안 됨


# --- C-a: lifecycle 상태 저장·로드(저장만) ---

def test_lifecycle_save_load_by_exact_digest(tmp_path):
    # C-a: 상태·근거는 정확한 candidate(id/version/digest)에 연결. C2는 저장만.
    s = SkillStore(str(tmp_path / "store.json"))
    a = _mk(idv="a")
    ref = _ref(a)
    s.save_lifecycle_state(ref, "APPROVED", {"reviewer": "s3"})
    rec = s.load_lifecycle_state(ref)
    assert rec["state"] == "APPROVED" and rec["digest"] == a.digest
    # 다른 digest(같은 id/version)는 별개 candidate — 상태 미연결
    other = {"id": "a", "version": "1.0.0", "digest": "beef" * 16}
    assert s.load_lifecycle_state(other) is None


def test_lifecycle_persists_across_instances(tmp_path):
    p = str(tmp_path / "store.json")
    a = _mk(idv="a")
    ref = _ref(a)
    SkillStore(p).save_lifecycle_state(ref, "PUBLISHED", {})
    assert SkillStore(p).load_lifecycle_state(ref)["state"] == "PUBLISHED"

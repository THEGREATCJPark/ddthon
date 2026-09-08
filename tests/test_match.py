"""V5, V6 — 검색 결정성·다중후보 안정선택·오류 구분. 소유: A. 구현: S7."""

import time

from skillloop import descriptor as D
from skillloop import match as M


def _mk(idv, ver, signals):
    content = {
        "id": idv,
        "version": ver,
        "origin": {"author": "test"},
        "applicability": {"signals": list(signals)},
        "procedure": {"action": "pip-install", "index": "allow", "target": "skillloop-demo-pkg"},
    }
    return D.make_descriptor(content)


def _obs(signature="pip-install-fail:skillloop-demo-pkg", exit_code=1):
    return M.FailureObservation(
        command="pip install skillloop-demo-pkg",
        target_pkg="skillloop-demo-pkg",
        error_signature=signature,
        exit_code=exit_code,
    )


class _FakeStore:
    def __init__(self, descriptors):
        self._descriptors = list(descriptors)

    def list(self):
        return list(self._descriptors)


class _RaisingStore:
    def list(self):
        raise RuntimeError("store list failure")


class _SlowStore:
    def __init__(self, descriptors, delay):
        self._descriptors = list(descriptors)
        self._delay = delay

    def list(self):
        time.sleep(self._delay)
        return list(self._descriptors)


_EXACT = "pip-install-fail:skillloop-demo-pkg"
_GENERIC = "pip-install-fail"


def test_multiple_valid_candidates_select_single_match():
    # 다중 유효 후보 → NO_MATCH 아님. 결정적 단일 선택(적합도↓, version↓, id↑).

    # (1) 적합도 우선: 정확 일치(fit=2)가 상위 네임스페이스 일치(fit=1)를 이긴다.
    #     — generic 후보의 version이 더 높아도 적합도가 우선.
    out = M.search(_obs(), _FakeStore([
        _mk("generic-fix", "9.0.0", [_GENERIC]),
        _mk("exact-fix", "1.0.0", [_EXACT]),
    ]))
    assert out.status == "MATCH"
    assert out.descriptor.id == "exact-fix"
    assert out.candidates_considered == 2

    # (2) 동일 적합도 → version 내림차순으로 결정.
    out = M.search(_obs(), _FakeStore([
        _mk("aaa", "1.0.0", [_EXACT]),
        _mk("zzz", "2.0.0", [_EXACT]),
    ]))
    assert out.status == "MATCH"
    assert out.descriptor.id == "zzz"
    assert out.descriptor.version == "2.0.0"

    # (3) 동일 적합도·동일 version → id 오름차순으로 결정.
    out = M.search(_obs(), _FakeStore([
        _mk("bbb", "1.0.0", [_EXACT]),
        _mk("aaa", "1.0.0", [_EXACT]),
    ]))
    assert out.status == "MATCH"
    assert out.descriptor.id == "aaa"

    # (4) 결정성: 동일 입력 → 동일 출력.
    store = _FakeStore([
        _mk("generic-fix", "9.0.0", [_GENERIC]),
        _mk("exact-fix", "1.0.0", [_EXACT]),
    ])
    first = M.search(_obs(), store)
    second = M.search(_obs(), store)
    assert first.status == second.status == "MATCH"
    assert first.descriptor == second.descriptor


def test_no_match_only_when_zero_valid_candidates():
    # 유효 후보 0건일 때만 NO_MATCH(빈 스토어 / 불일치 신호).
    out = M.search(_obs(), _FakeStore([]))
    assert out.status == "NO_MATCH"
    assert out.descriptor is None
    assert out.candidates_considered == 0

    out = M.search(_obs(), _FakeStore([
        _mk("other", "1.0.0", ["file-access-fail"]),
        _mk("wrong-pkg", "1.0.0", ["pip-install-fail:other-pkg"]),
    ]))
    assert out.status == "NO_MATCH"
    assert out.candidates_considered == 0

    # 유효 후보가 하나라도 있으면 NO_MATCH가 아니다.
    out = M.search(_obs(), _FakeStore([
        _mk("other", "1.0.0", ["file-access-fail"]),
        _mk("hit", "1.0.0", [_EXACT]),
    ]))
    assert out.status == "MATCH"
    assert out.descriptor.id == "hit"


def test_error_timeout_not_invoked_distinct_from_no_match():
    # 오류/시간초과/미호출은 각각 별도 상태이며 NO_MATCH와 혼동되지 않는다.

    # ERROR: 검색 중 예외 → NO_MATCH로 위장하지 않음.
    err = M.search(_obs(), _RaisingStore())
    assert err.status == "ERROR"

    # TIMEOUT: 검색 예산 초과. 유효 후보가 있어도 예산 초과면 MATCH가 아니라 TIMEOUT.
    to = M.search(
        _obs(),
        _SlowStore([_mk("hit", "1.0.0", [_EXACT])], delay=0.05),
        budget_s=0.001,
    )
    assert to.status == "TIMEOUT"

    # NOT_INVOKED: 관찰 신호 없음 → 검색 미수행.
    ni = M.search(_obs(signature="   "), _FakeStore([_mk("hit", "1.0.0", [_EXACT])]))
    assert ni.status == "NOT_INVOKED"

    # NO_MATCH(실검색·유효 0건)와 위 세 상태는 모두 구별된다.
    nm = M.search(_obs(), _FakeStore([]))
    assert nm.status == "NO_MATCH"
    assert len({err.status, to.status, ni.status, nm.status}) == 4

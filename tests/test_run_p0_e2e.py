"""V12 — run-p0 e2e 실제 샘플(실패→적용→검증→reuse+1).

소유: CJ 단일 수정자(A는 검증·수정 의견). 구현: S9.

상태: **SKIPPED — A의 S7/S8(match.py/reuse_service.py) 인계 후 아래 skip 해제.**
본문은 실행 준비 완료 상태이며, A 코드 수신 시 `pytestmark`만 제거하면 실제 통합 검증이 돈다.
파일 존재만으로 완료 처리하지 않는다 — 실제 설치·검증·카운트 결과를 assert한다.
"""

import shutil

import pytest

from skillloop import cli
from skillloop import usage as U
from skillloop.usage import UsageTracker

# A(S7/S8) 인계 전까지 e2e는 실행 불가 → 현재 부분 검증 상태 유지(19 PASS / 8 SKIP).
pytestmark = pytest.mark.skip(reason="A의 S7/S8(match/reuse_service) 인계 대기 — 수신 후 unskip")

DEMO_ID = "fix-skillloop-demo-pkg-install"
DEMO_VER = "1.0.0"


@pytest.fixture()
def paths(tmp_path):
    store_p = str(tmp_path / "store.json")
    usage_p = str(tmp_path / "usage.json")
    yield store_p, usage_p
    shutil.rmtree(tmp_path, ignore_errors=True)


def test_run_p0_reuse_increments_to_one(paths):
    # 실패 재현 → MATCH → 실제 설치·검증 성공 → reuse=1.
    store_p, usage_p = paths
    rc = cli.run_p0(store_path=store_p, usage_path=usage_p)
    assert rc == 0
    assert UsageTracker(usage_p).current_count(DEMO_ID, DEMO_VER) == 1


def test_same_execution_reverify_keeps_count(paths):
    # 동일 run_id(같은 논리 실행)의 재시작·재검증은 중복 +1 하지 않는다.
    store_p, usage_p = paths
    rid = U.new_execution_id()
    assert cli.run_p0(store_path=store_p, usage_path=usage_p, run_id=rid) == 0
    assert UsageTracker(usage_p).current_count(DEMO_ID, DEMO_VER) == 1
    # 같은 run_id로 재실행(재시작 시뮬레이션)
    assert cli.run_p0(store_path=store_p, usage_path=usage_p, run_id=rid) == 0
    assert UsageTracker(usage_p).current_count(DEMO_ID, DEMO_VER) == 1


def test_new_execution_increments_to_two(paths):
    # 새 논리 실행(새 run_id)은 각각 +1 → 두 번째 실행에서 reuse=2.
    store_p, usage_p = paths
    assert cli.run_p0(store_path=store_p, usage_path=usage_p) == 0
    assert cli.run_p0(store_path=store_p, usage_path=usage_p) == 0
    assert UsageTracker(usage_p).current_count(DEMO_ID, DEMO_VER) == 2

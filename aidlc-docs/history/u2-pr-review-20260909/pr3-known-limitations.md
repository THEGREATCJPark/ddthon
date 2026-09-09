# U2 알려진 한계 — 빈 Excel 인스턴스가 GetActiveObject를 가로채는 문제

> **성격**: 알려진 한계 기록. 코드는 변경하지 않았습니다.
> **QA §9 준수** — 신규 기능 없음, 코드 무변경, 문서만 추가.

## 요약

실행 중 Excel 인스턴스에 attach하는 P1 파일접근 경로는 `GetActiveObject("Excel.Application")`
**단일 경로**로 인스턴스를 하나만 잡습니다. 대상 workbook을 보유하지 않은 **빈(또는 다른) Excel
인스턴스**가 ROT(Running Object Table)에 먼저 등록돼 있으면 그 인스턴스가 반환되고, 대상 workbook을
찾지 못해 `NOT_RUN`으로 끝납니다. 여러 실행 중 Excel 인스턴스를 열거해 대상 workbook 보유 인스턴스를
찾는 로직은 현재 없습니다.

## 2026-09-09 B PC 시연 실제 재현

- **PID 8888** — 창 제목 없는 전날 잔여 Excel 인스턴스(대상 workbook 미보유).
- **PID 7916** — `scripts/prepare-p1.py`가 열어둔 대상 workbook 보유 인스턴스.
- `GetActiveObject`가 ROT에서 PID 8888(빈 인스턴스)을 반환 → 대상 workbook 부재 →
  attach 매칭 실패 → `NOT_RUN`.

## 코드 근거

- **단일 GetActiveObject 경로**: `skillloop/envharness_p1.py:200`
  ```python
  excel = _excel_app if _excel_app is not None else win32com.client.GetActiveObject('Excel.Application')
  ```
- **매칭 루프는 attach된 단 하나의 인스턴스 내부만 탐색**: `skillloop/envharness_p1.py:204-208`
  - workbook `FullName`을 대상 경로와 대조하되, **그 하나의 인스턴스의 `Workbooks`만** 순회.
  - 대상이 없으면 `AccessUnavailable('workbook: target is not open in attached Excel')` → 상위에서 `NOT_RUN`.
- `GetActiveObject`는 코드 전체에서 이 한 곳뿐이며, ROT 열거·`GetObject(path)` 등 대안 경로는 없습니다.

## 크로스-프로세스 구조상 `_excel_app` 우회가 무효인 이유

- `skillloop/envharness_p1.py:200`의 `_excel_app`(모듈 전역)은 **같은 프로세스에서**
  `_try_com_create_encrypted`(`DispatchEx`)로 인스턴스를 만든 경우에만 채워집니다.
- 그러나 실제 시연은 크로스-프로세스입니다:
  - `scripts/prepare-p1.py`가 **운영자 별도 프로세스**에서 `DispatchEx('Excel.Application')`로
    Excel을 띄우고 대상 workbook을 열어둡니다(스크립트 상단 docstring: *"Keeps two owned workbooks open"*).
  - Agent 복구 흐름(cli/서비스)은 **다른 프로세스**라 그 프로세스의 `_excel_app`은 `None`.
- 따라서 Agent 프로세스에서는 항상 `GetActiveObject` fallback으로 떨어지고,
  `_excel_app` 보관은 우회 효과가 없습니다. `_excel_app` 우회는 **동일 프로세스 단위테스트**
  (`tests/test_envharness_p1.py::test_real_excel_attach_end_to_end`)에서만 유효합니다.

## 빈 인스턴스 존재 시 `NOT_RUN`은 정직한 결과

- 대상 workbook을 못 찾았을 때 강제 통과·연출 없이 `NOT_RUN`으로 끝나는 것은
  U2 정직성 원칙(환경 미준비/미가용 → `NOT_RUN`, 게시 금지)에 부합합니다.
- 즉 현재 동작은 **결과를 왜곡하지 않는다**는 점에서 정직하며, 문제는 "정답 인스턴스를
  자동으로 고르지 못한다"는 편의/견고성 측면입니다.

## 미구현 사유 (판단은 CJ)

- 여러 실행 중 Excel 인스턴스를 열거(ROT 열거, 인스턴스별 `Workbooks` 스캔 등)해
  대상 workbook 보유 인스턴스를 선택하는 로직은 **신규 기능**에 해당하여 QA §9(신규 기능 금지)에
  저촉될 수 있습니다.
- 따라서 즉시 구현하지 않고 한계로 기록합니다. 다중 인스턴스 탐색 도입 여부·범위는 CJ 판단.
- 당장의 회피책: 시연 전 대상 workbook 보유 인스턴스 외의 잔여 Excel 인스턴스를 종료하고,
  대상 workbook만 열어둔 상태로 실행.

## 자동 테스트로 잡히지 않는 점

- 실 Excel attach 통합 테스트는 opt-in입니다:
  `tests/test_envharness_p1.py:155`는 `SKILLLOOP_RUN_EXCEL_TESTS=1`일 때만 실행되고
  그 외에는 skip(`NOT_RUN`).
- 이 테스트는 opt-in으로 켜더라도 **동일 프로세스**에서 `_try_com_create_encrypted`가 만든
  인스턴스를 대상으로 하므로, **크로스-프로세스 + 빈 인스턴스 간섭** 상황은 재현하지 않습니다.
- 따라서 본 한계는 현재 자동 테스트 스위트로는 검출되지 않으며, 실 시연에서만 드러납니다.

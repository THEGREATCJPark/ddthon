export const drafts = [
  {
    title: "Requirements 최종 검토와 범위 합의",
    track: "공통",
    detail:
      "P0/P1 성공 조건과 공개 저장소 사용 범위를 검토하고 실제 사람 승인 기록에 연결합니다.",
    acceptance: "요구사항 문서와 실제 결정 기록 링크",
  },
  {
    title: "P0 · 기존 Skill 재사용 시연",
    track: "P0",
    detail:
      "합성 내부 패키지 설치 실패 → 기존 팀 Skill 적용 → 실제 설치 및 출처 검증 → 실제 적용 +1을 확인합니다.",
    acceptance:
      "설치 결과 및 출처 확인\n- [ ] 검색만으로 사용 횟수가 증가하지 않음\n- [ ] 합성 초기값과 실제 사용 이력 구분",
  },
  {
    title: "P1 · 업무 결과와 접근 방법 검증",
    track: "P1",
    detail:
      "합성 XLSX 접근 문제를 진단하고 허용된 경로로 데이터를 읽어 실적과 예상치를 구분한 그래프를 완성합니다.",
    acceptance:
      "TASK 결과와 CAPABILITY 접근 결과를 각각 검증\n- [ ] 실적 / 예상 구분\n- [ ] 원본 데이터가 Skill에 포함되지 않음",
  },
  {
    title: "Core / Store 최소 통합 규약 합의",
    track: "공통",
    detail:
      "Unit 설계 후 identity, lifecycle, export/import, reuse event, 충돌 규칙, 파일 소유 범위를 합의합니다.",
    acceptance: "승인된 설계 및 인터페이스 링크",
  },
  {
    title: "다른 PC에서 Published Skill 수신 확인",
    track: "공유",
    detail:
      "통합 규약 확정 후 Published descriptor 전송과 수신·검증·검색을 확인합니다. 새 업무 재사용은 별도 검증합니다.",
    acceptance:
      "수신 및 검색 증거\n- [ ] 동일 이벤트 중복 집계 방지\n- [ ] Warm 실행 결과는 별도로 기록",
  },
  {
    title: "독립 검증 · 제출 증거 정리",
    track: "QA",
    detail:
      "새 환경 재실행, 실제 P0/P1 화면, AI-DLC 결정과 구현의 연결을 확인하고 NOT_RUN을 구분합니다.",
    acceptance: "대상 커밋·명령·입력·결과·증거 링크",
  },
];
export const goals = [
  {
    id: "P0",
    title: "이미 아는 문제는, 팀의 경험으로.",
    subtitle: "기존 Skill 재사용",
    text: "프로젝트 라이브러리 설치가 막혀도, 팀이 검증한 방법으로 업무를 이어갑니다.",
    checks: [
      "기존 팀 Skill 검색과 현재 환경 적합성 확인",
      "실제 설치 결과 · 패키지 출처 검증",
      "검증된 적용에만 +1, 중복 집계 방지",
    ],
    color: "green",
  },
  {
    id: "P1",
    title: "처음 푼 문제는, 다음 동료의 경험으로.",
    subtitle: "새로운 경험 축적",
    text: "데이터 접근 문제를 해결하고 요청한 그래프까지 완성한 뒤, 재사용할 환경 절차만 남깁니다.",
    checks: [
      "TASK와 CAPABILITY 각각 검증",
      "정확한 후보 내용에 대한 사람 검토",
      "다른 입력 Replay 통과 후 Published",
    ],
    color: "purple",
  },
];
export const diagrams = [
  {
    id: "loop",
    name: "SkillLoop 한눈에",
    tag: "전체 흐름",
    description:
      "업무 요청에서 시작해 팀의 경험이 다음 Agent에게 전달되기까지. 아래 흐름은 목표 구조이며 실제 완료 상태가 아닙니다.",
    steps: [
      "업무 요청",
      "팀 경험 검색",
      "적용 또는 환경 탐색",
      "업무와 접근 검증",
      "사람 검토와 Replay",
      "다음 Agent 재사용",
    ],
    code: `flowchart TB\n  A["현업 엔지니어의 업무 요청"] --> B["팀 Skill 검색 · 현재 환경 확인"]\n  B --> C["기존 경험 적용"]\n  B --> D["새 환경 조사 · 허용된 방법 탐색"]\n  C --> E["TASK 결과 + CAPABILITY 접근 각각 검증"]\n  D --> E\n  E --> F["기존 경험 · 실제 재사용 기록"]\n  E --> G["새 경험 · 정확한 내용 사람 검토"]\n  G --> H["독립 Replay PASS → Published"]\n  H -.-> B`,
  },
  {
    id: "p0",
    name: "P0 · 기존 경험 재사용",
    tag: "데모 시나리오",
    description:
      "기존 팀 Skill로 합성 패키지 설치 문제를 해결합니다. 초기 20회는 합성 데모 값이며 실제 과거 실적으로 보지 않습니다.",
    steps: [
      "설치 요청",
      "일반 설치 경로 실패",
      "기존 Skill 적용",
      "설치와 출처 검증",
      "실제 적용 +1",
    ],
    code: `flowchart LR\n  A["requirements 설치 요청"] --> B["일반 공급 경로의 실제 실패"]\n  B --> C["기존 팀 Skill 검색"]\n  C --> D["현재 환경 적합성 확인"]\n  D --> E["허용된 공급 경로 적용"]\n  E --> F{"설치 · 출처 검증 PASS?"}\n  F -->|예| G["실제 적용 +1"]\n  F -->|아니오| H["실패 기록 · 카운트 유지"]`,
  },
  {
    id: "p1",
    name: "P1 · 새로운 경험 축적",
    tag: "데모 시나리오",
    description:
      "업무 데이터는 현재 작업에 남기고, 재사용 가능한 환경 접근 절차만 공유합니다. 자원 접근 승인과 후보 공개 동의는 각각 확인합니다.",
    steps: [
      "합성 XLSX 분석 요청",
      "환경 사실과 지식 확인",
      "허용된 접근으로 그래프 완성",
      "업무 / 접근 독립 검증",
      "후보 검토",
      "다른 입력 Replay",
      "게시 및 Warm 검증",
    ],
    code: `flowchart TD\n  A["합성 XLSX 분석 · 추세선 요청"] --> B["직접 읽기 실패 · 환경 사실 확인"]\n  B --> C["팀 Skill · 사내 지식 검색"]\n  C --> D["적용 가능한 방법 부재 확인 · 환경 탐색"]\n  D --> E["필요한 자원 접근 승인"]\n  E --> F["데이터 읽기 · 실제 그래프 생성"]\n  F --> G["TASK 결과 검증"]\n  G --> H["CAPABILITY 접근 검증"]\n  H --> I["재사용할 환경 절차만 Candidate로 제안"]\n  I --> J["정확한 내용 · 공개 의사 사람 검토"]\n  J --> K["독립 Replay"]\n  K -->|PASS| L["Published"]\n  K -->|FAIL| M["공개 보류 · 원인 확인"]\n  L --> N["새 업무 Warm 검증"]`,
  },
  {
    id: "team",
    name: "팀 공유 구조",
    tag: "설계 후보",
    description:
      "main은 제품 소스, team-skill-store는 합성 공유 데이터 전송 브랜치로 제안된 상태입니다. 실제 구현은 통합 규약 확정 후 진행합니다.",
    steps: [
      "PC A 로컬 Registry",
      "Published descriptor 내보내기",
      "Git 전송",
      "PC B 검증 및 가져오기",
      "새 업무 재사용 별도 검증",
    ],
    code: `flowchart LR\n  A["PC A · Local Registry"] --> B["Published descriptor export"]\n  B --> C["ddthon · team-skill-store"]\n  C --> D["PC B · pull"]\n  D --> E["schema · digest · Published 검증"]\n  E --> F["Local Registry import"]\n  F --> G["검색 · 새 업무 Warm 검증"]\n  G --> H["고유 reuse event"]\n  H --> C`,
  },
];

import test from "node:test";
import assert from "node:assert/strict";
import {
  STAGES,
  SAMPLE,
  messageInput,
  encodeProgress,
  decodeProgress,
  emptyProgress,
} from "./workspace.ts";
test("scenario names explain Python and Excel without requiring P0/P1 knowledge", () => {
  assert.equal(STAGES.length, 6);
  assert.match(STAGES[1].name, /Python 설치/);
  assert.match(STAGES[2].name, /Excel 설치/);
});
test("progress links preserve independent parallel stages", () => {
  const p = emptyProgress();
  p.python = 1;
  p.excel = 2;
  p.plan = 3;
  assert.deepEqual(decodeProgress(encodeProgress(p)), p);
  assert.equal(p.verify, 0);
});
test("unrecognized link versions and invalid statuses never invent progress", () => {
  for (const v of [
    null,
    "",
    "v1.01230123",
    "v2.01230",
    "v2.012304",
    "v2.0123012",
    "v2.<script>",
  ])
    assert.equal(decodeProgress(v), null);
});
test("challenge forcibly removes submitted identity; team needs a name", () => {
  assert.deepEqual(messageInput("challenge", "  날카로운 의견  ", "실명"), {
    body: "날카로운 의견",
    name: "익명의 다른 팀",
  });
  assert.throws(() => messageInput("team", "내용", " "));
  assert.deepEqual(messageInput("team", "내용", "민수"), {
    body: "내용",
    name: "민수",
  });
});
test("comments reject blank and oversized text; sample remains visibly synthetic", () => {
  assert.throws(() => messageInput("team", " ", "민수"));
  assert.throws(() => messageInput("challenge", "가".repeat(1001), ""));
  assert.equal(SAMPLE.sample, true);
  assert.equal(SAMPLE.board, "challenge");
  assert.equal(SAMPLE.parentId, "");
});

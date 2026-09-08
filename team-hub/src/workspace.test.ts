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
test("progress links preserve independent parallel stages", () => {
  const p = emptyProgress();
  p.u1 = 1;
  p.u2 = 2;
  p.u3 = 3;
  assert.deepEqual(decodeProgress(encodeProgress(p)), p);
  assert.equal(p.q1, 0);
});
test("unrecognized link versions and invalid statuses never invent progress", () => {
  for (const v of [
    null,
    "",
    "v1.01230123",
    "v2.012301",
    "v3.012301",
    "v4.01230",
    "v4.01230400",
    "v3.0123012",
    "v3.<script>",
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

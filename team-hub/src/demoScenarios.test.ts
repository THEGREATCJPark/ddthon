import test from "node:test";
import assert from "node:assert/strict";
import { SCENARIOS, demoCounts } from "./demoScenarios.ts";

test("ordinary P0 request does not require repeated recovery instructions", () => {
  assert.equal(SCENARIOS.p0.filter(s => s.prompt).length, 1);
  assert.equal(demoCounts("p0", 3).reused, 0);
  assert.equal(demoCounts("p0", 4).reused, 1);
});

test("candidate and human approval do not increment publication or reuse", () => {
  for (const n of [4, 5, 6]) {
    assert.equal(demoCounts("p1", n).published, 0);
    assert.equal(demoCounts("p1", n).reused, 0);
    assert.equal(demoCounts("p1", n).candidates, 1);
  }
  assert.equal(demoCounts("p1", 7).published, 1);
  assert.equal(demoCounts("p1", 8).reused, 0);
  assert.deepEqual(demoCounts("p1", 9), { published: 1, available: 2, reused: 1, candidates: 0, warm: true });
  assert.deepEqual(demoCounts("p1", 0), { published: 0, available: 1, reused: 0, candidates: 0, warm: false });
});

test("environment fact turn precedes discovery without supplying an API answer", () => {
  assert.ok(SCENARIOS.p1[0].answer.some(line => line.includes("열어 볼 수 있나요")));
  assert.match(SCENARIOS.p1[1].prompt, /엑셀을 열어서/);
  assert.doesNotMatch(SCENARIOS.p1[1].prompt, /COM|pywin32|xlwings/);
  assert.equal(SCENARIOS.p1[2].prompt, "");
  assert.equal(demoCounts("p0", 0).available, 1);
  assert.equal(demoCounts("p0", 4).published, 0);
});

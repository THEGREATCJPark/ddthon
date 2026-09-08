import test from "node:test";
import assert from "node:assert/strict";
import { SCENARIOS, demoCounts } from "./demoScenarios.ts";

test("ordinary P0 request does not require repeated recovery instructions", () => {
  assert.equal(SCENARIOS.p0.filter(s => s.prompt).length, 1);
  assert.equal(demoCounts("p0", 3).reused, 0);
  assert.equal(demoCounts("p0", 4).reused, 1);
});

test("candidate and human approval do not increment publication or reuse", () => {
  for (const n of [3, 4, 5]) {
    assert.equal(demoCounts("p1", n).published, 0);
    assert.equal(demoCounts("p1", n).reused, 0);
    assert.equal(demoCounts("p1", n).candidates, 1);
  }
  assert.equal(demoCounts("p1", 6).published, 1);
  assert.equal(demoCounts("p1", 7).reused, 0);
  assert.deepEqual(demoCounts("p1", 8), { published: 1, reused: 1, candidates: 0, warm: true });
  assert.deepEqual(demoCounts("p1", 0), { published: 0, reused: 0, candidates: 0, warm: false });
});

import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { validateExample } from "./exampleSkillData.ts";

// Fixed seed for reproducibility; fast-check's default shrinking remains enabled.
const options = { seed: 20260909, numRuns: 200 };
const text = (max: number) => fc.array(
  fc.constantFrom("A", "z", "0", "한", "글", "é", "😀", "<", ">", "\"", "\n", " "),
  { maxLength: Math.floor((max - 2) / 2) },
).map(chars => "가" + chars.join("") + "끝");
const whitespace = fc.array(fc.constantFrom(" ", "\t", "\n", "\r", "\u00a0"),
  { maxLength: 20 }).map(chars => chars.join(""));

test("generated valid drafts preserve content, normalize boundaries, and are idempotent", () => {
  fc.assert(fc.property(text(100), text(60000), text(30), whitespace,
    (title, body, author, pad) => {
      const input = { title: pad + title + pad, body: pad + body + pad, author: pad + author + pad };
      const before = { ...input };
      const normalized = validateExample(input);
      assert.deepEqual(normalized, { title, body, author });
      assert.deepEqual(validateExample(normalized), normalized);
      assert.deepEqual(input, before);
    }), options);
});

test("generated whitespace-only required fields are rejected; blank author gets the default", () => {
  fc.assert(fc.property(whitespace, text(100), text(60000), (blank, title, body) => {
    assert.throws(() => validateExample({ title: blank, body, author: "CJ" }));
    assert.throws(() => validateExample({ title, body: blank, author: "CJ" }));
    assert.equal(validateExample({ title, body, author: blank }).author, "팀원");
  }), options);
});

test("generated over-limit fields are rejected while exact boundaries remain valid", () => {
  const limits = { title: 100, body: 60000, author: 30 } as const;
  fc.assert(fc.property(fc.constantFrom("title", "body", "author"),
    fc.integer({ min: 1, max: 100 }), (field, excess) => {
      const draft = { title: "제목", body: "내용", author: "CJ", [field]: "가".repeat(limits[field]) };
      assert.equal(validateExample(draft)[field].length, limits[field]);
      draft[field] += "나".repeat(excess);
      assert.throws(() => validateExample(draft));
    }), options);
});

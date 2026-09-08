import { readFileSync } from "node:fs";
import { before, after, test } from "node:test";
import {
  initializeTestEnvironment,
  assertSucceeds,
  assertFails,
} from "@firebase/rules-unit-testing";
import {
  doc,
  collection,
  writeBatch,
  serverTimestamp,
  getDoc,
  getDocs,
  query,
  limit,
  setDoc,
  deleteDoc,
  updateDoc,
} from "firebase/firestore";
let env;
before(async () => {
  env = await initializeTestEnvironment({
    projectId: "demo-nowhere",
    firestore: {
      host: "127.0.0.1",
      port: 9098,
      rules: readFileSync("firestore.rules", "utf8"),
    },
  });
  await env.clearFirestore();
});
after(async () => {
  await env?.cleanup();
});
function post(db, uid, id, patch = {}) {
  const batch = writeBatch(db);
  batch.set(doc(db, "messages", id), {
    board: "team",
    body: "검증",
    name: "작성자",
    parentId: "",
    createdAt: serverTimestamp(),
    ...patch,
  });
  batch.set(doc(db, "messageOwners", id), {
    uid,
    createdAt: serverTimestamp(),
  });
  batch.set(doc(db, "postLimits", uid), {
    last: serverTimestamp(),
    messageId: id,
  });
  return batch.commit();
}
test("anonymous writes require Auth; reads require bounded queries", async () => {
  const db = env.unauthenticatedContext().firestore();
  await assertFails(post(db, "none", "no-auth"));
  await assertSucceeds(getDocs(query(collection(db, "messages"), limit(200))));
  await assertFails(getDocs(collection(db, "messages")));
});
test("author can post/delete; another browser cannot impersonate/edit/delete/read owner", async () => {
  const a = env.authenticatedContext("alice").firestore(),
    b = env.authenticatedContext("bob").firestore();
  await assertSucceeds(post(a, "alice", "owned"));
  await assertFails(deleteDoc(doc(b, "messages", "owned")));
  await assertFails(
    updateDoc(doc(b, "messages", "owned"), { body: "덮어쓰기" }),
  );
  await assertFails(getDoc(doc(b, "messageOwners", "owned")));
  await assertFails(post(b, "alice", "forged"));
  await assertSucceeds(deleteDoc(doc(a, "messages", "owned")));
});
test("server validates lengths, identity, extra fields and real timestamp", async () => {
  for (const [i, patch] of [
    { body: "" },
    { body: "가".repeat(1001) },
    { board: "private" },
    { board: "challenge", name: "실명" },
    { sample: true },
    { createdAt: 0 },
  ].entries()) {
    const uid = `bad${i}`;
    await assertFails(
      post(env.authenticatedContext(uid).firestore(), uid, uid, patch),
    );
  }
});
test("replies stay on their own board and only one level; sample accepts anonymous replies", async () => {
  await assertSucceeds(
    post(env.authenticatedContext("root").firestore(), "root", "root"),
  );
  await assertSucceeds(
    post(env.authenticatedContext("reply").firestore(), "reply", "reply", {
      parentId: "root",
    }),
  );
  await assertFails(
    post(env.authenticatedContext("nested").firestore(), "nested", "nested", {
      parentId: "reply",
    }),
  );
  await assertFails(
    post(env.authenticatedContext("cross").firestore(), "cross", "cross", {
      board: "challenge",
      name: "익명의 다른 팀",
      parentId: "root",
    }),
  );
  await assertSucceeds(
    post(env.authenticatedContext("sample").firestore(), "sample", "sample", {
      board: "challenge",
      name: "익명의 다른 팀",
      parentId: "sample-challenge",
    }),
  );
});
test("rules enforce cooldown and reject writes without ownership/rate batch", async () => {
  const db = env.authenticatedContext("rate").firestore();
  await assertSucceeds(post(db, "rate", "first"));
  await assertFails(post(db, "rate", "second"));
  await assertFails(
    setDoc(doc(db, "messages", "direct"), {
      board: "team",
      body: "우회",
      name: "익명",
      parentId: "",
      createdAt: serverTimestamp(),
    }),
  );
});

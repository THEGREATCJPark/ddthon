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

function capture(db, uid, id, patch = {}) {
  const batch = writeBatch(db);
  batch.set(doc(db, 'captures', id), { scenario: 'p0', title: '실행 캡처 검증', uid, mime: 'image/gif', chunks: 1, hasText: true, createdAt: serverTimestamp(), ...patch });
  batch.set(doc(db, 'captures', id, 'content', 'image-00'), { data: 'R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==' });
  batch.set(doc(db, 'captures', id, 'content', 'transcript'), { text: '질문과 실제 실행 답변' });
  return batch.commit();
}
test('capture image/text are shared; only original author can remove or write content', async () => {
  const a = env.authenticatedContext('capture-author').firestore();
  const b = env.authenticatedContext('capture-other').firestore();
  const publicDb = env.unauthenticatedContext().firestore();
  await assertFails(capture(publicDb, 'nobody', 'capture-no-auth'));
  await assertFails(capture(b, 'capture-author', 'capture-forged'));
  await assertFails(capture(a, 'capture-author', 'capture-html', { mime: 'text/html' }));
  await assertSucceeds(capture(a, 'capture-author', 'capture-good'));
  await assertSucceeds(getDocs(query(collection(publicDb, 'captures'), limit(50))));
  await assertFails(getDocs(collection(publicDb, 'captures')));
  await assertSucceeds(getDoc(doc(publicDb, 'captures', 'capture-good', 'content', 'transcript')));
  await assertSucceeds(getDocs(query(collection(publicDb, 'captures', 'capture-good', 'content'), limit(29))));
  await assertFails(updateDoc(doc(a, 'captures', 'capture-good'), { title: '변조' }));
  await assertFails(setDoc(doc(b, 'captures', 'capture-good', 'content', 'image-01'), { data: 'tamper' }));
  await assertFails(deleteDoc(doc(b, 'captures', 'capture-good')));
  await assertFails(deleteDoc(doc(b, 'captures', 'capture-good', 'content', 'transcript')));
  const batch = writeBatch(a);
  batch.delete(doc(a, 'captures', 'capture-good', 'content', 'image-00'));
  batch.delete(doc(a, 'captures', 'capture-good', 'content', 'transcript'));
  batch.delete(doc(a, 'captures', 'capture-good'));
  await assertSucceeds(batch.commit());
});

test("skill examples are public, bounded and deletable only by their author", async () => {
  const author = env.authenticatedContext("example-author").firestore();
  const other = env.authenticatedContext("example-other").firestore();
  const publicDb = env.unauthenticatedContext().firestore();
  const data = {title:"Example",author:"Team",problem:"403",cause:"Clock",applicability:"Confirmed skew",procedure:"Adjust signing time",verification:"List bucket",uid:"example-author",createdAt:serverTimestamp()};
  await assertFails(setDoc(doc(publicDb,"skillExamples","anon"),data));
  await assertFails(setDoc(doc(other,"skillExamples","spoof"),data));
  await assertFails(setDoc(doc(author,"skillExamples","large"),{...data,procedure:"x".repeat(6001)}));
  await assertFails(setDoc(doc(author,"skillExamples","oversize-benefit"),{...data,benefit:"x".repeat(241)}));
  await assertFails(setDoc(doc(author,"skillExamples","invalid-effect"),{...data,effect:123}));
  await assertSucceeds(setDoc(doc(author,"skillExamples","with-value"),{...data,benefit:"Shared troubleshooting",effect:"Less repeated diagnosis"}));
  await assertSucceeds(setDoc(doc(author,"skillExamples","valid"),data));
  await assertSucceeds(getDocs(query(collection(publicDb,"skillExamples"),limit(100))));
  await assertFails(getDocs(collection(publicDb,"skillExamples")));
  await assertFails(updateDoc(doc(author,"skillExamples","valid"),{title:"changed"}));
  await assertFails(deleteDoc(doc(other,"skillExamples","valid")));
  await assertSucceeds(deleteDoc(doc(author,"skillExamples","valid")));
});

test("free-text skill ideas accept a body without structured fields", async () => {
  const db = env.authenticatedContext("free-author").firestore();
  const other = env.authenticatedContext("free-other").firestore();
  const data = {title:"Free idea",body:"A freely written experience",author:"Team",uid:"free-author",createdAt:serverTimestamp()};
  await assertSucceeds(setDoc(doc(db,"skillExamples","free-valid"),data));
  await assertFails(setDoc(doc(db,"skillExamples","free-empty"),{...data,body:""}));
  await assertFails(setDoc(doc(db,"skillExamples","free-large"),{...data,body:"x".repeat(60001)}));
  await assertFails(setDoc(doc(other,"skillExamples","free-spoof"),data));
  await assertFails(deleteDoc(doc(other,"skillExamples","free-valid")));
  await assertSucceeds(deleteDoc(doc(db,"skillExamples","free-valid")));
});

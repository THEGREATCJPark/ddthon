import { initializeApp } from "firebase/app";
import { getAuth, signInAnonymously } from "firebase/auth";
import {
  collection,
  doc,
  getFirestore,
  limit,
  onSnapshot,
  orderBy,
  query,
  serverTimestamp,
  where,
  writeBatch,
} from "firebase/firestore";
import { messageInput, type Board, type Message } from "./workspace";

// Public web-app identifier. Access is enforced by Firebase Auth and firestore.rules.
const app = initializeApp({
  apiKey: "AIzaSyBqEPYnchiLvAVqgWTO5eN9c-goclV1tk4",
  authDomain: "nowhere-skillloop-ddthon.firebaseapp.com",
  projectId: "nowhere-skillloop-ddthon",
  appId: "1:803885490930:web:a37b06a7719fedd5bfe66b",
});
export const db = getFirestore(app);
const auth = getAuth(app);
let signingIn: ReturnType<typeof signInAnonymously> | undefined;
export async function session() {
  await auth.authStateReady();
  if (auth.currentUser) return auth.currentUser;
  try {
    return (await (signingIn ||= signInAnonymously(auth))).user;
  } finally {
    signingIn = undefined;
  }
}
export function watchMessages(
  board: Board,
  next: (data: Message[]) => void,
  error: () => void,
) {
  return onSnapshot(
    query(
      collection(db, "messages"),
      where("board", "==", board),
      orderBy("createdAt", "desc"),
      limit(200),
    ),
    (snapshot) => {
      next(
        snapshot.docs.map(
          (d) =>
            ({
              ...d.data(),
              id: d.id,
              createdAt: d.data().createdAt?.toMillis() || Date.now(),
            }) as Message,
        ),
      );
    },
    error,
  );
}
export async function sendMessage(
  board: Board,
  body: string,
  name: string,
  parentId = "",
) {
  const input = messageInput(board, body, name);
  const user = await session();
  const message = doc(collection(db, "messages"));
  const batch = writeBatch(db);
  batch.set(message, {
    board,
    ...input,
    parentId,
    createdAt: serverTimestamp(),
  });
  batch.set(doc(db, "messageOwners", message.id), {
    uid: user.uid,
    createdAt: serverTimestamp(),
  });
  batch.set(doc(db, "postLimits", user.uid), {
    last: serverTimestamp(),
    messageId: message.id,
  });
  await batch.commit();
  return message.id;
}
export async function removeMessage(id: string) {
  const batch = writeBatch(db);
  batch.delete(doc(db, "messages", id));
  batch.delete(doc(db, "messageOwners", id));
  await batch.commit();
}
export function watchOwned(uid: string, next: (ids: Set<string>) => void) {
  return onSnapshot(
    query(collection(db, "messageOwners"), where("uid", "==", uid), limit(200)),
    (s) => next(new Set(s.docs.map((d) => d.id))),
    () => {},
  );
}

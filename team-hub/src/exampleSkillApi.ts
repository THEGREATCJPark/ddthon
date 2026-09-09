import {addDoc, collection, deleteDoc, doc, limit, onSnapshot, orderBy, query, serverTimestamp} from "firebase/firestore";
import {db, session} from "./communityApi";
import {validateExample, type ExampleSkill, type FreeSkillDraft} from "./exampleSkillData";
export function watchExamples(next: (items: ExampleSkill[]) => void, error: () => void) {
  return onSnapshot(query(collection(db, "skillExamples"), orderBy("createdAt", "desc"), limit(100)), snapshot => next(snapshot.docs.map(d => ({...d.data(), id:d.id, createdAt:d.data().createdAt?.toMillis() || Date.now()}) as ExampleSkill)), error);
}
export async function saveExample(draft: FreeSkillDraft) {
  const input = validateExample(draft);
  const user = await session();
  await addDoc(collection(db, "skillExamples"), {...input, uid:user.uid, createdAt:serverTimestamp()});
}
export async function removeExample(id: string) {
  await deleteDoc(doc(db, "skillExamples", id));
}

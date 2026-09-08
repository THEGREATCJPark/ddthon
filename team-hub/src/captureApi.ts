import {
  collection,
  doc,
  documentId,
  getDoc,
  getDocs,
  limit,
  onSnapshot,
  orderBy,
  query,
  serverTimestamp,
  writeBatch,
} from "firebase/firestore";
import { db, session } from "./communityApi";

export type Capture = {
  id: string;
  scenario: "p0" | "p1";
  title: string;
  uid: string;
  mime: string;
  chunks: number;
  hasText: boolean;
  createdAt: number;
};
export const MAX_FILE = 4 * 1024 * 1024;
const CHUNK_SIZE = 200000;
export function watchCaptures(
  next: (items: Capture[]) => void,
  error: () => void,
) {
  return onSnapshot(
    query(collection(db, "captures"), orderBy("createdAt", "desc"), limit(50)),
    { includeMetadataChanges: true },
    (snapshot) =>
      next(
        snapshot.docs
          .filter((d) => !d.metadata.hasPendingWrites)
          .map(
            (d) =>
              ({
                ...d.data(),
                id: d.id,
                createdAt: d.data().createdAt?.toMillis() || Date.now(),
              }) as Capture,
          ),
      ),
    error,
  );
}
export async function saveCapture(
  scenario: "p0" | "p1",
  title: string,
  transcript: string,
  file: File | null,
) {
  if (!title.trim() || title.trim().length > 80)
    throw new Error("제목은 1~80자로 입력해 주세요.");
  if (!file && !transcript.trim())
    throw new Error("이미지/GIF 또는 실행 전문을 넣어 주세요.");
  if (transcript.length > 60000)
    throw new Error("실행 전문은 60,000자까지 등록할 수 있습니다.");
  if (
    file &&
    (file.size > MAX_FILE ||
      !["image/png", "image/jpeg", "image/gif", "image/webp"].includes(
        file.type,
      ))
  )
    throw new Error("PNG·JPG·GIF·WebP, 파일당 4MB까지 등록할 수 있습니다.");
  const user = await session();
  const capture = doc(collection(db, "captures"));
  const batch = writeBatch(db);
  const encoded = file
    ? await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result).split(",")[1]);
        reader.onerror = () => reject(new Error("파일을 읽지 못했습니다."));
        reader.readAsDataURL(file);
      })
    : "";
  const chunks = Math.ceil(encoded.length / CHUNK_SIZE);
  batch.set(capture, {
    scenario,
    title: title.trim(),
    uid: user.uid,
    mime: file?.type || "",
    chunks,
    hasText: !!transcript.trim(),
    createdAt: serverTimestamp(),
  });
  if (transcript.trim())
    batch.set(doc(capture, "content", "transcript"), { text: transcript });
  for (let i = 0; i < chunks; i++)
    batch.set(doc(capture, "content", `image-${String(i).padStart(2, "0")}`), {
      data: encoded.slice(i * CHUNK_SIZE, (i + 1) * CHUNK_SIZE),
    });
  await batch.commit();
}
export async function loadMedia(item: Capture) {
  const docs = await getDocs(
    query(
      collection(db, "captures", item.id, "content"),
      orderBy(documentId()),
      limit(29),
    ),
  );
  const encoded = docs.docs
    .filter((d) => d.id.startsWith("image-"))
    .map((d) => d.data().data as string)
    .join("");
  if (!encoded) throw new Error("이미지를 불러오지 못했습니다.");
  const bytes = Uint8Array.from(atob(encoded), (char) => char.charCodeAt(0));
  return URL.createObjectURL(new Blob([bytes], { type: item.mime }));
}
export async function loadTranscript(id: string) {
  const snapshot = await getDoc(
    doc(db, "captures", id, "content", "transcript"),
  );
  if (!snapshot.exists()) throw new Error("실행 전문을 불러오지 못했습니다.");
  return snapshot.data().text as string;
}
export async function removeCapture(item: Capture) {
  const batch = writeBatch(db);
  for (let i = 0; i < item.chunks; i++)
    batch.delete(
      doc(
        db,
        "captures",
        item.id,
        "content",
        `image-${String(i).padStart(2, "0")}`,
      ),
    );
  if (item.hasText)
    batch.delete(doc(db, "captures", item.id, "content", "transcript"));
  batch.delete(doc(db, "captures", item.id));
  await batch.commit();
}

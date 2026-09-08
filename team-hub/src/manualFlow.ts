import { STAGES, type StageId } from "./stages.ts";
import type { Status } from "./domain.ts";

export const FLOW_STATUSES: Status[] = ["todo", "doing", "blocked", "done"];
export type FlowState = {
  mode: "github" | "manual";
  stages: Record<StageId, Status>;
};
export function emptyFlow(): FlowState {
  return {
    mode: "github",
    stages: Object.fromEntries(STAGES.map((s) => [s.id, "todo"])) as Record<
      StageId,
      Status
    >,
  };
}
// Fixed version and exact-length alphabet keep shared URLs small and unambiguous.
export function decodeFlow(value: string | null): FlowState | null {
  if (!value || !/^v1\.[0-3]{8}$/.test(value)) return null;
  return {
    mode: "manual",
    stages: Object.fromEntries(
      STAGES.map((s, i) => [s.id, FLOW_STATUSES[Number(value[i + 3])]]),
    ) as Record<StageId, Status>,
  };
}
export function encodeFlow(state: FlowState): string {
  return `v1.${STAGES.map((s) => FLOW_STATUSES.indexOf(state.stages[s.id])).join("")}`;
}
export function restoreFlow(value: string | null): FlowState {
  try {
    const parsed = JSON.parse(value || "null");
    const state = decodeFlow(parsed?.value);
    if (state && ["github", "manual"].includes(parsed.mode))
      return { ...state, mode: parsed.mode };
  } catch {
    /* Corrupt or unavailable storage must not prevent startup. */
  }
  return emptyFlow();
}

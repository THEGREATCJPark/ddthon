import { useEffect, useState } from "react";
import {
  decodeFlow,
  encodeFlow,
  emptyFlow,
  restoreFlow,
  type FlowState,
} from "./manualFlow";
const KEY = "ddthon.flow.v1";
export function useFlowState() {
  const [state, setState] = useState<FlowState>(() => {
    const shared = decodeFlow(new URL(location.href).searchParams.get("flow"));
    if (shared) return shared;
    try {
      return restoreFlow(localStorage.getItem(KEY));
    } catch {
      return emptyFlow();
    }
  });
  const [storageError, setStorageError] = useState(false);
  useEffect(() => {
    try {
      localStorage.setItem(
        KEY,
        JSON.stringify({ mode: state.mode, value: encodeFlow(state) }),
      );
      setStorageError(false);
    } catch {
      setStorageError(true);
    }
    // A received link remains reload-safe after editing or switching sources.
    const url = new URL(location.href);
    if (url.searchParams.has("flow")) {
      if (state.mode === "manual")
        url.searchParams.set("flow", encodeFlow(state));
      else url.searchParams.delete("flow");
      history.replaceState(null, "", url);
    }
  }, [state]);
  return { state, setState, storageError };
}

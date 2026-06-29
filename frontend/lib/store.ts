import { create } from "zustand";

interface AppState {
  currentModel: string;
  currentProvider: string;
  setModel: (model: string, provider: string) => void;
}

export const useAppStore = create<AppState>()((set) => ({
  currentModel: "qwen-vl-max",
  currentProvider: "cloud",
  setModel: (model, provider) =>
    set({ currentModel: model, currentProvider: provider }),
}));

import { create } from 'zustand';
import { localKey } from "../lib/api"

export interface NavStack {
  title: string;
  path: string;
}

interface UserStore {
  token: string | null;
  setToken: (token: string) => void;
}

export const userStore = create<UserStore>((set) => ({
  token: localStorage.getItem(localKey.token) || null,
  setToken: (token) => {
    localStorage.setItem(localKey.token, token);
    set({ token });
  }
}));
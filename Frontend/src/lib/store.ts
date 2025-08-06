"use client";

import { create } from 'zustand';

export type View = 'overview' | 'sql' | 'llm' | 'charts' | 'logs' | 'connections';

type DashboardState = {
  activeView: View;
  setActiveView: (view: View) => void;
};

export const useDashboardStore = create<DashboardState>((set) => ({
  activeView: 'overview',
  setActiveView: (view) => set({ activeView: view }),
}));

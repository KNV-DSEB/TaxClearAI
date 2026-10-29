import { ReactNode } from 'react';
import { create } from 'zustand';

export type ModalType = 'confirm' | 'info' | 'success' | 'error' | 'warning';

export type ModalConfig = {
  id: string;
  type: ModalType;
  title?: ReactNode;
  content?: ReactNode;
  okText?: string;
  cancelText?: string;
  danger?: boolean;
  showCancel?: boolean;
  onOk?: () => void | Promise<void>;
  onCancel?: () => void;
};

type ModalStoreState = {
  modals: ModalConfig[];
  open: (config: Omit<ModalConfig, 'id'>) => string;
  close: (id: string) => void;
};

// Backs Modal's imperative API (Modal.confirm/info/success/error/warning) —
// a queue any code can push into (including outside React, e.g. a catch
// block), rendered once by <ModalContainer/> mounted in App.tsx.
export const useModalStore = create<ModalStoreState>((set) => ({
  modals: [],
  open: (config) => {
    const id = crypto.randomUUID();
    set((state) => ({ modals: [...state.modals, { ...config, id }] }));
    return id;
  },
  close: (id) => set((state) => ({ modals: state.modals.filter((modal) => modal.id !== id) })),
}));

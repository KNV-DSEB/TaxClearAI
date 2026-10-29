'use client';

import { type ReactElement } from 'react';
import { AlertTriangle, CheckCircle2, HelpCircle, Info, XCircle } from 'lucide-react';

import { Button } from '@/components/common/Button';
import { type ModalType, useModalStore } from '@/store/modal.store';

import { Modal } from './Modal';

const iconByType: Record<ModalType, ReactElement> = {
  confirm: <HelpCircle className="h-6 w-6 shrink-0 text-primary" aria-hidden />,
  info: <Info className="h-6 w-6 shrink-0 text-primary" aria-hidden />,
  success: <CheckCircle2 className="h-6 w-6 shrink-0 text-green-500" aria-hidden />,
  error: <XCircle className="h-6 w-6 shrink-0 text-destructive" aria-hidden />,
  warning: <AlertTriangle className="h-6 w-6 shrink-0 text-yellow-500" aria-hidden />,
};

// Mount this once near the root of the app (see App.tsx) so
// Modal.confirm()/info()/success()/error()/warning() can be called from
// anywhere. Reusable UI ONLY — no business logic beyond wiring the store's
// queue to the presentational Modal.
export function ModalContainer() {
  const modals = useModalStore((state) => state.modals);
  const close = useModalStore((state) => state.close);

  return (
    <>
      {modals.map((modal) => (
        <Modal
          key={modal.id}
          open
          closable={false}
          title={modal.title}
          onOpenChange={(next) => {
            if (!next) {
              close(modal.id);
              modal.onCancel?.();
            }
          }}
          footer={
            <>
              {modal.showCancel && (
                <Button
                  onClick={() => {
                    close(modal.id);
                    modal.onCancel?.();
                  }}
                >
                  {modal.cancelText ?? 'Cancel'}
                </Button>
              )}
              <Button
                type="primary"
                danger={modal.danger}
                onClick={async () => {
                  await modal.onOk?.();
                  close(modal.id);
                }}
              >
                {modal.okText ?? 'OK'}
              </Button>
            </>
          }
        >
          <div className="flex gap-3">
            {iconByType[modal.type]}
            <div className="flex-1 pt-0.5">{modal.content}</div>
          </div>
        </Modal>
      ))}
    </>
  );
}

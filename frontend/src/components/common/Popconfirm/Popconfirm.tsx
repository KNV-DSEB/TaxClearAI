'use client';

import { ReactElement, ReactNode, useState } from 'react';

import { Button } from '@/components/common/Button';
import { Popover } from '@/components/common/Popover';

type PopconfirmProps = {
  title: ReactNode;
  description?: ReactNode;
  children: ReactElement;
  onConfirm?: () => void;
  onCancel?: () => void;
  okText?: string;
  cancelText?: string;
  danger?: boolean;
  disabled?: boolean;
  placement?: 'top' | 'bottom' | 'left' | 'right';
};

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics".
export function Popconfirm({
  title,
  description,
  children,
  onConfirm,
  onCancel,
  okText = 'OK',
  cancelText = 'Cancel',
  danger = false,
  disabled = false,
  placement = 'top',
}: PopconfirmProps) {
  const [open, setOpen] = useState(false);

  if (disabled) {
    return children;
  }

  return (
    <Popover
      open={open}
      onOpenChange={setOpen}
      placement={placement}
      trigger={children}
      content={
        <div className="flex flex-col gap-2">
          <div className="text-sm font-medium text-foreground">{title}</div>
          {description && <div className="text-sm text-muted-foreground">{description}</div>}
          <div className="mt-1 flex justify-end gap-2">
            <Button
              size="sm"
              onClick={() => {
                setOpen(false);
                onCancel?.();
              }}
            >
              {cancelText}
            </Button>
            <Button
              type="primary"
              danger={danger}
              size="sm"
              onClick={() => {
                setOpen(false);
                onConfirm?.();
              }}
            >
              {okText}
            </Button>
          </div>
        </div>
      }
    />
  );
}

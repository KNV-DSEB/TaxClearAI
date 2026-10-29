'use client';

import { forwardRef, useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

import { Input, type InputProps } from './Input';

export const Password = forwardRef<HTMLInputElement, Omit<InputProps, 'suffix' | 'type'>>((props, ref) => {
  const [visible, setVisible] = useState(false);

  return (
    <Input
      ref={ref}
      type={visible ? 'text' : 'password'}
      suffix={
        <button
          type="button"
          tabIndex={-1}
          aria-label={visible ? 'Hide password' : 'Show password'}
          onClick={() => setVisible((prev) => !prev)}
          className="flex items-center text-muted-foreground hover:text-foreground"
        >
          {visible ? <EyeOff className="h-4 w-4" aria-hidden /> : <Eye className="h-4 w-4" aria-hidden />}
        </button>
      }
      {...props}
    />
  );
});

Password.displayName = 'Input.Password';

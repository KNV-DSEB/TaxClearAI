'use client';

import { cloneElement, type ReactElement } from 'react';
import { Controller, useFormContext, type FieldPath, type FieldValues } from 'react-hook-form';

import { cn } from '@/utils/cn';

type ItemProps<T extends FieldValues> = {
  name: FieldPath<T>;
  label?: string;
  required?: boolean;
  className?: string;
  children: ReactElement;
};

export function Item<T extends FieldValues>({ name, label, required, className, children }: ItemProps<T>) {
  const { control } = useFormContext<T>();

  return (
    <Controller
      control={control}
      name={name}
      render={({ field: { ref: _ref, ...field }, fieldState: { error } }) => (
        <div className={cn('flex flex-col gap-1.5', className)}>
          {label && (
            <label className="text-sm font-medium text-foreground">
              {label}
              {required && <span className="ml-0.5 text-destructive">*</span>}
            </label>
          )}
          {cloneElement(children, field)}
          {error && <span className="text-xs text-destructive">{error.message}</span>}
        </div>
      )}
    />
  );
}

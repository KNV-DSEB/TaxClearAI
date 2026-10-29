'use client';

import type { ReactNode } from 'react';
import { FormProvider, type FieldValues } from 'react-hook-form';

import type { FormController } from '@/hooks/useForm';

type FormRootProps<T extends FieldValues> = {
  form: FormController<T>;
  onFinish?: (values: T) => void;
  onFinishFailed?: (errors: FormController<T>['formState']['errors']) => void;
  /** Lets an external button submit this form via `<button form={id}>` — e.g. a Modal footer action. */
  id?: string;
  className?: string;
  children: ReactNode;
};

export function FormRoot<T extends FieldValues>({
  form,
  onFinish,
  onFinishFailed,
  id,
  className,
  children,
}: FormRootProps<T>) {
  return (
    <FormProvider {...form}>
      <form
        id={id}
        noValidate
        className={className}
        onSubmit={form.handleSubmit(onFinish ?? (() => {}), onFinishFailed)}
      >
        {children}
      </form>
    </FormProvider>
  );
}

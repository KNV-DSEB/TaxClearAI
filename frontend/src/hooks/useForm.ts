import {
  useForm as useRHFForm,
  type DefaultValues,
  type FieldValues,
  type Path,
  type PathValue,
  type UseFormProps,
  type UseFormReturn,
} from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import type { ZodType } from 'zod';

export type FormController<T extends FieldValues> = UseFormReturn<T> & {
  getFieldsValue: () => T;
  setFieldsValue: (values: Partial<T>) => void;
  setFieldValue: <K extends Path<T>>(name: K, value: PathValue<T, K>) => void;
  resetFields: (values?: DefaultValues<T>) => void;
  validateFields: () => Promise<boolean>;
};

export function useForm<T extends FieldValues>(
  // `ZodType<T, any, any>` instead of `ZodType<T>`: the abstract generic
  // `ZodType<T>` doesn't carry enough concrete `_def` info to match
  // zodResolver's overload — only a real schema instance (e.g. `z.object({...})`)
  // has a concrete `_def.typeName`, so Def/Input are loosened for compatibility.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  schema: ZodType<T, any, any>,
  options?: Omit<UseFormProps<T>, 'resolver'>
): [FormController<T>] {
  const form = useRHFForm<T>({ resolver: zodResolver(schema), ...options });

  const controller: FormController<T> = {
    ...form,
    getFieldsValue: () => form.getValues(),
    setFieldsValue: (values) => {
      (Object.keys(values) as Path<T>[]).forEach((key) => {
        form.setValue(key, values[key] as PathValue<T, Path<T>>);
      });
    },
    setFieldValue: (name, value) => form.setValue(name, value),
    resetFields: (values) => form.reset(values),
    validateFields: () => form.trigger(),
  };

  return [controller];
}

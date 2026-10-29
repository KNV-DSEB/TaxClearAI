import { useForm } from '@/hooks/useForm';

import { FormRoot } from './FormRoot';
import { Item } from './Item';

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics". Mirrors antd's Form API: <Form form={form} onFinish={...}>
// <Form.Item name="email" label="Email"><Input /></Form.Item></Form>,
// form built with Form.useForm(schema).
export const Form = Object.assign(FormRoot, { Item, useForm });
export type { FormController } from '@/hooks/useForm';

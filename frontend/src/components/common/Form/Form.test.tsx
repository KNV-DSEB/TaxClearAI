import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { z } from 'zod';

import { Input } from '@/components/common/Input';

import { Form } from './index';

const schema = z.object({
  email: z.string().min(1, 'Email is required').email('Invalid email'),
});

type FormValues = z.infer<typeof schema>;

function TestForm({ onFinish }: { onFinish: (values: FormValues) => void }) {
  const [form] = Form.useForm(schema, { defaultValues: { email: '' } });

  return (
    <Form form={form} onFinish={onFinish}>
      <Form.Item<FormValues> name="email" label="Email" required>
        <Input placeholder="you@example.com" />
      </Form.Item>
      <button type="submit">Submit</button>
    </Form>
  );
}

describe('Form', () => {
  it('renders the label and field', () => {
    render(<TestForm onFinish={vi.fn()} />);
    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('you@example.com')).toBeInTheDocument();
  });

  it('calls onFinish with the field values when valid', async () => {
    const onFinish = vi.fn();
    render(<TestForm onFinish={onFinish} />);

    fireEvent.change(screen.getByPlaceholderText('you@example.com'), { target: { value: 'a@b.com' } });
    fireEvent.click(screen.getByRole('button', { name: 'Submit' }));

    await vi.waitFor(() => expect(onFinish).toHaveBeenCalledTimes(1));
    expect(onFinish.mock.calls[0][0]).toEqual({ email: 'a@b.com' });
  });

  it('shows a validation error and does not call onFinish when invalid', async () => {
    const onFinish = vi.fn();
    render(<TestForm onFinish={onFinish} />);

    fireEvent.change(screen.getByPlaceholderText('you@example.com'), { target: { value: 'not-an-email' } });
    fireEvent.click(screen.getByRole('button', { name: 'Submit' }));

    expect(await screen.findByText('Invalid email')).toBeInTheDocument();
    expect(onFinish).not.toHaveBeenCalled();
  });
});

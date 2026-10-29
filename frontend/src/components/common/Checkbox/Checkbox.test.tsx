import type { ChangeEvent } from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { Checkbox } from './Checkbox';

describe('Checkbox', () => {
  it('renders unchecked by default', () => {
    render(<Checkbox label="Bật đăng nhập OTP" />);
    expect(screen.getByRole('checkbox', { name: 'Bật đăng nhập OTP' })).not.toBeChecked();
  });

  it('reflects the checked prop', () => {
    render(<Checkbox label="Bật đăng nhập OTP" checked readOnly />);
    expect(screen.getByRole('checkbox', { name: 'Bật đăng nhập OTP' })).toBeChecked();
  });

  it('falls back to the value prop when checked is not provided (Form.Item compatibility)', () => {
    render(<Checkbox label="Bật đăng nhập OTP" value readOnly />);
    expect(screen.getByRole('checkbox', { name: 'Bật đăng nhập OTP' })).toBeChecked();
  });

  it('calls onChange with the native event when toggled', () => {
    let checkedAtCallTime: boolean | undefined;
    const onChange = vi.fn((e: ChangeEvent<HTMLInputElement>) => {
      checkedAtCallTime = e.target.checked;
    });
    render(<Checkbox label="Bật đăng nhập OTP" checked={false} onChange={onChange} />);

    fireEvent.click(screen.getByRole('checkbox', { name: 'Bật đăng nhập OTP' }));

    expect(onChange).toHaveBeenCalledTimes(1);
    expect(checkedAtCallTime).toBe(true);
  });

  it('is disabled when disabled prop is set', () => {
    render(<Checkbox label="Bật đăng nhập OTP" disabled />);
    expect(screen.getByRole('checkbox', { name: 'Bật đăng nhập OTP' })).toBeDisabled();
  });
});

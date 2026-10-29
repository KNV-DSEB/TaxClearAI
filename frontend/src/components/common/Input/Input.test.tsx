import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { Input } from './index';

describe('Input', () => {
  it('renders and accepts typed input', () => {
    render(<Input placeholder="Email" />);
    const input = screen.getByPlaceholderText('Email');
    fireEvent.change(input, { target: { value: 'a@b.com' } });
    expect(input).toHaveValue('a@b.com');
  });

  it('calls onChange handler', () => {
    const onChange = vi.fn();
    render(<Input placeholder="Email" onChange={onChange} />);
    fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: 'x' } });
    expect(onChange).toHaveBeenCalledTimes(1);
  });

  it('renders prefix and suffix', () => {
    render(<Input placeholder="Search" prefix={<span>P</span>} suffix={<span>S</span>} />);
    expect(screen.getByText('P')).toBeInTheDocument();
    expect(screen.getByText('S')).toBeInTheDocument();
  });

  it('is disabled when disabled prop is set', () => {
    render(<Input placeholder="Email" disabled />);
    expect(screen.getByPlaceholderText('Email')).toBeDisabled();
  });

  describe('Input.TextArea', () => {
    it('renders a textarea element', () => {
      render(<Input.TextArea placeholder="Description" />);
      expect(screen.getByPlaceholderText('Description').tagName).toBe('TEXTAREA');
    });
  });

  describe('Input.Password', () => {
    it('masks the value by default and toggles visibility', () => {
      render(<Input.Password placeholder="Password" />);
      const input = screen.getByPlaceholderText('Password');
      expect(input).toHaveAttribute('type', 'password');

      fireEvent.click(screen.getByRole('button', { name: 'Show password' }));
      expect(input).toHaveAttribute('type', 'text');
    });
  });
});

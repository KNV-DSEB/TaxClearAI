import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { Select } from './Select';

const options = [
  { label: 'Apple', value: 'apple' },
  { label: 'Banana', value: 'banana' },
];

describe('Select', () => {
  it('renders the placeholder when no value is selected', () => {
    render(<Select options={options} placeholder="Pick a fruit" />);
    expect(screen.getByText('Pick a fruit')).toBeInTheDocument();
  });

  it('shows the options after opening the trigger', async () => {
    render(<Select options={options} />);

    fireEvent.click(screen.getByRole('combobox'));

    expect(await screen.findByText('Apple')).toBeInTheDocument();
    expect(screen.getByText('Banana')).toBeInTheDocument();
  });

  it('calls onChange when an option is selected', async () => {
    const onChange = vi.fn();
    render(<Select options={options} onChange={onChange} />);

    fireEvent.click(screen.getByRole('combobox'));
    fireEvent.click(await screen.findByText('Apple'));

    expect(onChange).toHaveBeenCalledWith('apple');
  });

  it('shows the clear button and clears the value when allowClear is set', () => {
    const onChange = vi.fn();
    render(<Select options={options} value="apple" onChange={onChange} allowClear />);

    fireEvent.click(screen.getByRole('button', { name: 'Clear selection' }));

    expect(onChange).toHaveBeenCalledWith(undefined);
  });
});

import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { DatePicker } from './DatePicker';

describe('DatePicker', () => {
  it('renders the placeholder when no value is selected', () => {
    render(<DatePicker placeholder="Pick a date" />);
    expect(screen.getByText('Pick a date')).toBeInTheDocument();
  });

  it('renders the formatted value when provided', () => {
    render(<DatePicker value={new Date(2026, 0, 15)} />);
    expect(screen.getByText('15/01/2026')).toBeInTheDocument();
  });

  it('opens the calendar after clicking the trigger', async () => {
    render(<DatePicker />);

    fireEvent.click(screen.getByRole('button', { name: /select date/i }));

    expect(await screen.findByRole('grid')).toBeInTheDocument();
  });

  it('calls onChange with the selected date', async () => {
    const onChange = vi.fn();
    render(<DatePicker value={new Date(2026, 0, 15)} onChange={onChange} />);

    fireEvent.click(screen.getByRole('button', { name: /15\/01\/2026/i }));
    await screen.findByRole('grid');

    const dayButtons = screen.getAllByRole('gridcell').flatMap((cell) => Array.from(cell.querySelectorAll('button')));
    const day16 = dayButtons.find((button) => button.textContent?.trim() === '16');
    expect(day16).toBeDefined();
    fireEvent.click(day16!);

    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange.mock.calls[0][0]).toBeInstanceOf(Date);
  });
});

import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { ColorPicker } from './ColorPicker';

describe('ColorPicker', () => {
  it('renders the current value on the trigger', () => {
    render(<ColorPicker value="#1DA597" />);
    expect(screen.getByRole('button', { name: /#1DA597/i })).toBeInTheDocument();
  });

  it('shows preset swatches after opening', async () => {
    render(<ColorPicker value="#257BF4" presets={['#257BF4', '#EE862B']} />);

    fireEvent.click(screen.getByRole('button', { name: /#257BF4/i }));

    expect(await screen.findByRole('button', { name: '#EE862B' })).toBeInTheDocument();
  });

  it('calls onChange with the picked preset', async () => {
    const onChange = vi.fn();
    render(<ColorPicker value="#257BF4" presets={['#257BF4', '#EE862B']} onChange={onChange} />);

    fireEvent.click(screen.getByRole('button', { name: /#257BF4/i }));
    fireEvent.click(await screen.findByRole('button', { name: '#EE862B' }));

    expect(onChange).toHaveBeenCalledWith('#EE862B');
  });

  it('calls onChange only once a typed hex value is valid', async () => {
    const onChange = vi.fn();
    render(<ColorPicker value="#257BF4" onChange={onChange} />);

    fireEvent.click(screen.getByRole('button', { name: /#257BF4/i }));
    const input = await screen.findByPlaceholderText('#RRGGBB');

    fireEvent.change(input, { target: { value: '#12' } });
    expect(onChange).not.toHaveBeenCalled();

    fireEvent.change(input, { target: { value: '#112233' } });
    expect(onChange).toHaveBeenCalledWith('#112233');
  });
});

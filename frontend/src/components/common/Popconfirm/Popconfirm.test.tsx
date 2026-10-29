import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { Popconfirm } from './Popconfirm';

describe('Popconfirm', () => {
  it('renders the trigger element', () => {
    render(
      <Popconfirm title="Delete this item?">
        <button type="button">Delete</button>
      </Popconfirm>
    );
    expect(screen.getByRole('button', { name: 'Delete' })).toBeInTheDocument();
  });

  it('shows the confirmation title after clicking the trigger', async () => {
    render(
      <Popconfirm title="Delete this item?">
        <button type="button">Delete</button>
      </Popconfirm>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Delete' }));

    expect(await screen.findByText('Delete this item?')).toBeInTheDocument();
  });

  it('calls onConfirm when the confirm button is clicked', async () => {
    const onConfirm = vi.fn();
    render(
      <Popconfirm title="Delete this item?" onConfirm={onConfirm}>
        <button type="button">Delete</button>
      </Popconfirm>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Delete' }));
    fireEvent.click(await screen.findByRole('button', { name: 'OK' }));

    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('calls onCancel when the cancel button is clicked', async () => {
    const onCancel = vi.fn();
    render(
      <Popconfirm title="Delete this item?" onCancel={onCancel}>
        <button type="button">Delete</button>
      </Popconfirm>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Delete' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Cancel' }));

    expect(onCancel).toHaveBeenCalledTimes(1);
  });
});

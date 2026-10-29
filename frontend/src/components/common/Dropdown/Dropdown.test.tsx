import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { Dropdown } from './Dropdown';

describe('Dropdown', () => {
  it('renders the trigger element', () => {
    render(
      <Dropdown menu={{ items: [{ key: 'edit', label: 'Edit' }] }}>
        <button type="button">Actions</button>
      </Dropdown>
    );
    expect(screen.getByRole('button', { name: 'Actions' })).toBeInTheDocument();
  });

  it('shows menu items after clicking the trigger', async () => {
    render(
      <Dropdown menu={{ items: [{ key: 'edit', label: 'Edit' }, { key: 'delete', label: 'Delete', danger: true }] }}>
        <button type="button">Actions</button>
      </Dropdown>
    );

    fireEvent.pointerDown(screen.getByRole('button', { name: 'Actions' }), { button: 0 });

    expect(await screen.findByText('Edit')).toBeInTheDocument();
    expect(screen.getByText('Delete')).toBeInTheDocument();
  });

  it('calls the item onClick when selected', async () => {
    const onClick = vi.fn();
    render(
      <Dropdown menu={{ items: [{ key: 'edit', label: 'Edit', onClick }] }}>
        <button type="button">Actions</button>
      </Dropdown>
    );

    fireEvent.pointerDown(screen.getByRole('button', { name: 'Actions' }), { button: 0 });
    fireEvent.click(await screen.findByText('Edit'));

    expect(onClick).toHaveBeenCalledTimes(1);
  });
});

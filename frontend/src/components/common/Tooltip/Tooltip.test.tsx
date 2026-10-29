import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Tooltip } from './Tooltip';

describe('Tooltip', () => {
  it('renders the trigger element', () => {
    render(
      <Tooltip content="Helpful hint">
        <button type="button">Hover me</button>
      </Tooltip>
    );
    expect(screen.getByRole('button', { name: 'Hover me' })).toBeInTheDocument();
  });

  it('shows the tooltip content on focus', async () => {
    render(
      <Tooltip content="Helpful hint">
        <button type="button">Hover me</button>
      </Tooltip>
    );

    screen.getByRole('button', { name: 'Hover me' }).focus();

    expect(await screen.findByText('Helpful hint')).toBeInTheDocument();
  });

  it('renders only the children when disabled', () => {
    render(
      <Tooltip content="Helpful hint" disabled>
        <button type="button">Hover me</button>
      </Tooltip>
    );
    expect(screen.queryByText('Helpful hint')).not.toBeInTheDocument();
  });
});

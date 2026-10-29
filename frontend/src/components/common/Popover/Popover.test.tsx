import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Popover } from './Popover';

describe('Popover', () => {
  it('renders the trigger element', () => {
    render(<Popover trigger={<button type="button">Open</button>} content={<div>Panel content</div>} />);
    expect(screen.getByRole('button', { name: 'Open' })).toBeInTheDocument();
  });

  it('shows the content after clicking the trigger', async () => {
    render(<Popover trigger={<button type="button">Open</button>} content={<div>Panel content</div>} />);

    fireEvent.click(screen.getByRole('button', { name: 'Open' }));

    expect(await screen.findByText('Panel content')).toBeInTheDocument();
  });

  it('respects a controlled open state', () => {
    render(<Popover trigger={<button type="button">Open</button>} content={<div>Panel content</div>} open />);
    expect(screen.getByText('Panel content')).toBeInTheDocument();
  });
});

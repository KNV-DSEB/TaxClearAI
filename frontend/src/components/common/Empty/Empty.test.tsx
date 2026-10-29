import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Empty } from './Empty';

describe('Empty', () => {
  it('renders the default description', () => {
    render(<Empty />);
    expect(screen.getByText('No data')).toBeInTheDocument();
  });

  it('renders a custom description', () => {
    render(<Empty description="No users found" />);
    expect(screen.getByText('No users found')).toBeInTheDocument();
  });

  it('renders extra children below the description', () => {
    render(
      <Empty description="No users found">
        <button type="button">Create user</button>
      </Empty>
    );
    expect(screen.getByRole('button', { name: 'Create user' })).toBeInTheDocument();
  });
});

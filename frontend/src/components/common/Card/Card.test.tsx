import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Card } from './Card';

describe('Card', () => {
  it('renders its children', () => {
    render(<Card>Body content</Card>);
    expect(screen.getByText('Body content')).toBeInTheDocument();
  });

  it('renders title and extra when provided', () => {
    render(
      <Card title="My Card" extra={<span>More</span>}>
        Body
      </Card>
    );
    expect(screen.getByText('My Card')).toBeInTheDocument();
    expect(screen.getByText('More')).toBeInTheDocument();
  });

  it('does not render a header when title and extra are absent', () => {
    render(<Card>Body</Card>);
    expect(screen.queryByText('My Card')).not.toBeInTheDocument();
  });

  it('renders actions in the footer', () => {
    render(<Card actions={[<span key="edit">Edit</span>, <span key="delete">Delete</span>]}>Body</Card>);
    expect(screen.getByText('Edit')).toBeInTheDocument();
    expect(screen.getByText('Delete')).toBeInTheDocument();
  });
});

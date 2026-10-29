import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { Button } from './Button';

describe('Button', () => {
  it('renders its children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('renders with the default variant classes', () => {
    render(<Button>Default</Button>);
    expect(screen.getByRole('button', { name: 'Default' })).toHaveClass('border-input');
  });

  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Submit</Button>);

    fireEvent.click(screen.getByRole('button', { name: 'Submit' }));

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled and does not fire onClick when loading', () => {
    const onClick = vi.fn();
    render(
      <Button loading onClick={onClick}>
        Saving
      </Button>
    );

    const button = screen.getByRole('button', { name: 'Saving' });
    expect(button).toBeDisabled();

    fireEvent.click(button);
    expect(onClick).not.toHaveBeenCalled();
  });

  it('applies destructive styling when danger is true', () => {
    render(
      <Button type="primary" danger>
        Delete
      </Button>
    );
    expect(screen.getByRole('button', { name: 'Delete' })).toHaveClass('bg-destructive');
  });
});

import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { Menu } from './Menu';

describe('Menu', () => {
  it('renders top-level items', () => {
    render(<Menu items={[{ key: 'home', label: 'Home' }, { key: 'users', label: 'Users' }]} />);
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Users')).toBeInTheDocument();
  });

  it('calls onSelect when a leaf item is clicked', () => {
    const onSelect = vi.fn();
    render(<Menu items={[{ key: 'home', label: 'Home' }]} onSelect={onSelect} />);
    fireEvent.click(screen.getByText('Home'));
    expect(onSelect).toHaveBeenCalledWith('home');
  });

  it('expands a submenu instead of selecting when it has children', () => {
    const onSelect = vi.fn();
    render(
      <Menu
        items={[{ key: 'settings', label: 'Settings', children: [{ key: 'profile', label: 'Profile' }] }]}
        onSelect={onSelect}
      />
    );

    expect(screen.queryByText('Profile')).not.toBeInTheDocument();

    fireEvent.click(screen.getByText('Settings'));

    expect(screen.getByText('Profile')).toBeInTheDocument();
    expect(onSelect).not.toHaveBeenCalled();
  });

  it('highlights the selected key', () => {
    render(<Menu items={[{ key: 'home', label: 'Home' }]} selectedKeys={['home']} />);
    expect(screen.getByText('Home').closest('button')).toHaveClass('text-primary');
  });
});

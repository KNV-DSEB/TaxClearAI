import { fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { useModalStore } from '@/store/modal.store';

import { Modal } from './Modal';
import { ModalContainer } from './ModalContainer';

afterEach(() => {
  useModalStore.setState({ modals: [] });
});

describe('Modal (controlled)', () => {
  it('renders its content when open', () => {
    render(
      <Modal open onOpenChange={() => {}} title="My Modal">
        Body content
      </Modal>
    );
    expect(screen.getByText('My Modal')).toBeInTheDocument();
    expect(screen.getByText('Body content')).toBeInTheDocument();
  });

  it('does not render content when closed', () => {
    render(
      <Modal open={false} onOpenChange={() => {}} title="My Modal">
        Body content
      </Modal>
    );
    expect(screen.queryByText('Body content')).not.toBeInTheDocument();
  });

  it('calls onOpenChange when the close button is clicked', () => {
    const onOpenChange = vi.fn();
    render(
      <Modal open onOpenChange={onOpenChange} title="My Modal">
        Body content
      </Modal>
    );
    fireEvent.click(screen.getByRole('button', { name: 'Close' }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });
});

describe('Modal.confirm (imperative)', () => {
  it('renders a queued confirm modal via ModalContainer and calls onOk', async () => {
    const onOk = vi.fn();
    render(<ModalContainer />);

    Modal.confirm({ title: 'Delete item?', content: 'This cannot be undone.', onOk });

    fireEvent.click(await screen.findByRole('button', { name: 'OK' }));

    expect(onOk).toHaveBeenCalledTimes(1);
  });
});

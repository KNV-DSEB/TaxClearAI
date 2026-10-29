import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { Image } from './Image';

// next/image needs Next's build-time loader/runtime, unavailable under plain
// Vitest — swap it for a passthrough <img> so `fill`/`sizes` are dropped but
// src/alt/onLoad/onError (what these tests assert on) behave identically.
vi.mock('next/image', () => ({
  default: ({ fill: _fill, sizes: _sizes, ...props }: Record<string, unknown>) => <img {...props} />,
}));

describe('Image', () => {
  it('renders the image with the given src and alt', () => {
    render(<Image src="https://example.com/photo.png" alt="Photo" preview={false} />);
    const img = screen.getByRole('img', { name: 'Photo' }) as HTMLImageElement;
    expect(img.src).toBe('https://example.com/photo.png');
  });

  it('falls back to the placeholder image when src is empty', () => {
    render(<Image src={undefined} alt="Empty" preview={false} />);
    const img = screen.getByRole('img', { name: 'Empty' }) as HTMLImageElement;
    expect(img.src).toContain('/images/image-placeholder.svg');
  });

  it('falls back to the placeholder image when the img fires onError', () => {
    render(<Image src="https://example.com/broken.png" alt="Broken" preview={false} />);
    const img = screen.getByRole('img', { name: 'Broken' }) as HTMLImageElement;

    fireEvent.error(img);

    expect(img.src).toContain('/images/image-placeholder.svg');
  });

  it('shows a loading spinner before onLoad fires, and hides it after', () => {
    render(<Image src="https://example.com/photo.png" alt="Photo" preview={false} />);
    const img = screen.getByRole('img', { name: 'Photo' });

    expect(document.querySelector('.animate-spin')).toBeTruthy();

    fireEvent.load(img);

    expect(document.querySelector('.animate-spin')).toBeNull();
  });

  it('calls onUpload with the picked file', async () => {
    const onUpload = vi.fn().mockResolvedValue(undefined);
    render(<Image src="https://example.com/photo.png" alt="Photo" preview={false} onUpload={onUpload} />);

    const file = new File(['content'], 'avatar.png', { type: 'image/png' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => expect(onUpload).toHaveBeenCalledWith(file));
  });

  it('calls onRemove after confirming the Popconfirm', async () => {
    const onRemove = vi.fn().mockResolvedValue(undefined);
    render(<Image src="https://example.com/photo.png" alt="Photo" preview={false} onRemove={onRemove} />);

    fireEvent.click(screen.getByLabelText('Remove image'));
    fireEvent.click(screen.getByRole('button', { name: 'Remove' }));

    await waitFor(() => expect(onRemove).toHaveBeenCalledTimes(1));
  });

  it('hides upload/remove controls when disabled', () => {
    render(
      <Image
        src="https://example.com/photo.png"
        alt="Photo"
        preview={false}
        disabled
        onUpload={vi.fn()}
        onRemove={vi.fn()}
      />
    );

    expect(screen.queryByLabelText('Upload image')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Remove image')).not.toBeInTheDocument();
  });

  it('hides upload/remove controls when handlers are not passed', () => {
    render(<Image src="https://example.com/photo.png" alt="Photo" preview={false} />);

    expect(screen.queryByLabelText('Upload image')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Remove image')).not.toBeInTheDocument();
  });

  it('opens the preview modal when clicking the image', async () => {
    render(<Image src="https://example.com/photo.png" alt="Photo" />);

    fireEvent.click(screen.getByRole('button', { name: 'Preview Photo' }));

    await waitFor(() => expect(screen.getByRole('dialog')).toBeInTheDocument());
  });
});

import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { Table, type TableColumn } from './Table';

type User = { id: number; name: string; age: number };

const columns: TableColumn<User>[] = [
  { key: 'name', title: 'Name', dataIndex: 'name' },
  { key: 'age', title: 'Age', dataIndex: 'age', sorter: (a, b) => a.age - b.age },
];

const dataSource: User[] = [
  { id: 1, name: 'Alice', age: 30 },
  { id: 2, name: 'Bob', age: 25 },
];

describe('Table', () => {
  it('renders rows from dataSource', () => {
    render(<Table columns={columns} dataSource={dataSource} rowKey="id" />);
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Bob')).toBeInTheDocument();
  });

  it('shows Empty when dataSource is empty', () => {
    render(<Table columns={columns} dataSource={[]} rowKey="id" emptyText="No users" />);
    expect(screen.getByText('No users')).toBeInTheDocument();
  });

  it('shows a loading state', () => {
    render(<Table columns={columns} dataSource={dataSource} rowKey="id" loading />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(screen.queryByText('Alice')).not.toBeInTheDocument();
  });

  it('sorts rows when clicking a sortable column header', () => {
    render(<Table columns={columns} dataSource={dataSource} rowKey="id" />);

    fireEvent.click(screen.getByText('Age'));

    const rows = screen.getAllByRole('row').slice(1);
    expect(rows[0]).toHaveTextContent('Bob');
    expect(rows[1]).toHaveTextContent('Alice');
  });

  it('calls pagination.onChange when the next page button is clicked', () => {
    const onChange = vi.fn();
    render(
      <Table
        columns={columns}
        dataSource={dataSource}
        rowKey="id"
        pagination={{ current: 1, pageSize: 10, total: 20, onChange }}
      />
    );

    fireEvent.click(screen.getByText('Sau'));

    expect(onChange).toHaveBeenCalledWith(2, 10);
  });

  it('calls onRowClick with the record when a row is clicked', () => {
    const onRowClick = vi.fn();
    render(<Table columns={columns} dataSource={dataSource} rowKey="id" onRowClick={onRowClick} />);

    fireEvent.click(screen.getByText('Alice'));

    expect(onRowClick).toHaveBeenCalledWith(dataSource[0]);
  });
});

'use client';

import { useEffect, useState } from 'react';

import { Button } from '../components/common/Button';
import { healthService } from '../services/health.service';
import { HealthResponse } from '../types/api.types';

// Sample page demonstrating the required call chain: component → service →
// api.client (never fetch() directly in a component — see AGENTS.md
// "Frontend specifics").
export default function HomePage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = () => {
    healthService
      .check()
      .then((data) => {
        setHealth(data);
        setError(null);
      })
      .catch((err: Error) => setError(err.message));
  };

  useEffect(checkHealth, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-24">
      <h1 className="text-2xl font-bold">[PROJECT_NAME]</h1>
      {error && <p className="text-red-600">Backend unreachable: {error}</p>}
      {health && <pre className="rounded bg-gray-100 p-4">{JSON.stringify(health, null, 2)}</pre>}
      <Button onClick={checkHealth}>Re-check backend health</Button>
    </main>
  );
}

import { useEffect, useMemo, useState } from 'react';
import { Bar, BarChart, Cell, Pie, PieChart, Tooltip, XAxis, YAxis } from 'recharts';
import { fetchDashboard, startTask, stopTask } from '../api';
import type { DashboardStats } from '../types';

const COLORS = ['#38bdf8', '#a855f7', '#f97316', '#22d3ee', '#f43f5e'];

export function DashboardView() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState('cs.LG');
  const [textFilter, setTextFilter] = useState('');
  const [taskInterval, setTaskInterval] = useState(900);

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      setLoading(true);
      try {
        const data = await fetchDashboard();
        if (!cancelled) setStats(data);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    run();
    const timer = window.setInterval(run, 60_000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const categoryData = useMemo(
    () =>
      stats
        ? Object.entries(stats.categories).map(([name, value]) => ({ name, value }))
        : [],
    [stats],
  );

  const handleStartTask = async () => {
    await startTask({ category_filter: categoryFilter, text_filter: textFilter, interval_seconds: taskInterval });
    const refreshed = await fetchDashboard();
    setStats(refreshed);
  };

  const handleStopTask = async (taskId: string) => {
    await stopTask(taskId);
    const refreshed = await fetchDashboard();
    setStats(refreshed);
  };

  return (
    <section className="card">
      <h2>Dashboard</h2>
      {loading && <p>Updating metrics...</p>}
      {stats && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <article className="card">
              <h3>Total Papers</h3>
              <p style={{ fontSize: '2rem' }}>{stats.total_papers}</p>
            </article>
            <article className="card">
              <h3>Starred</h3>
              <p style={{ fontSize: '2rem' }}>{stats.starred}</p>
            </article>
            <article className="card">
              <h3>Read</h3>
              <p style={{ fontSize: '2rem' }}>{stats.read}</p>
            </article>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
            <article className="card">
              <h3>Papers by Category</h3>
              <BarChart width={400} height={240} data={categoryData}>
                <XAxis dataKey="name" hide />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" fill="#38bdf8" />
              </BarChart>
            </article>
            <article className="card">
              <h3>Topic Distribution</h3>
              <PieChart width={400} height={240}>
                <Pie data={categoryData} dataKey="value" nameKey="name" outerRadius={80} label>
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${entry.name}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </article>
          </div>
          <article className="card">
            <h3>Continuous Import Tasks</h3>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <input value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} placeholder="Category filter" />
              <input value={textFilter} onChange={(e) => setTextFilter(e.target.value)} placeholder="Text filter" />
              <input type="number" value={taskInterval} onChange={(e) => setTaskInterval(Number(e.target.value))} />
              <button onClick={handleStartTask}>Start Task</button>
            </div>
            <ul>
              {stats.tasks.map((task) => (
                <li key={task.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong>{task.category_filter || 'any'}</strong> – every {task.interval_seconds}s – {task.status}
                    <br />Imported {task.total_imported}/{task.total_attempted}
                  </div>
                  {task.status === 'running' && <button onClick={() => handleStopTask(task.id)}>Stop</button>}
                </li>
              ))}
            </ul>
          </article>
          <article className="card">
            <h3>Recent Activity</h3>
            <ul>
              {stats.recent_activity.map((event) => (
                <li key={event.ts}>
                  {new Date(event.ts).toLocaleTimeString()} – {event.title}
                </li>
              ))}
            </ul>
          </article>
        </>
      )}
    </section>
  );
}

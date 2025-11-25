import { useEffect, useMemo, useState } from 'react';
import { listPapers, manualIngest, updatePaperStatus } from '../api';
import type { Paper, PaperStatus } from '../types';

interface Props {
  onSelect: (paper: Paper) => void;
  onRefreshDetail: () => void;
}

const STATUS_OPTIONS: Array<{ label: string; value: PaperStatus | '' }> = [
  { label: 'All', value: '' },
  { label: 'New', value: 'new' },
  { label: 'Read', value: 'read' },
  { label: 'Starred', value: 'starred' },
];

export function PaperListView({ onSelect, onRefreshDetail }: Props) {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState<PaperStatus | ''>('');
  const [starredOnly, setStarredOnly] = useState(false);
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [ingestUrl, setIngestUrl] = useState('');
  const [ingestTags, setIngestTags] = useState('');
  const [error, setError] = useState<string | null>(null);

  const filters = useMemo(
    () => ({ search, category, status, starredOnly }),
    [search, category, status, starredOnly],
  );

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      setLoading(true);
      try {
        const response = await listPapers({
          text: filters.search,
          category: filters.category || undefined,
          status: filters.status || undefined,
          starred: filters.starredOnly ? 'true' : undefined,
          limit: 50,
          offset: 0,
        });
        if (!cancelled) {
          setPapers(response.items);
        }
      } catch (err) {
        console.error('Failed to load papers', err);
        if (!cancelled) setError('Unable to load papers');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    run();
    return () => {
      cancelled = true;
    };
  }, [filters]);

  const handleToggleStar = async (paper: Paper) => {
    const updated = await updatePaperStatus(paper.id, { starred: !paper.starred });
    setPapers((prev) => prev.map((item) => (item.id === paper.id ? updated : item)));
    onRefreshDetail();
  };

  const handleMarkRead = async (paper: Paper) => {
    const updated = await updatePaperStatus(paper.id, { status: 'read' });
    setPapers((prev) => prev.map((item) => (item.id === paper.id ? updated : item)));
    onRefreshDetail();
  };

  const handleIngest = async () => {
    setError(null);
    try {
      const tags = ingestTags
        .split(',')
        .map((chunk) => chunk.trim())
        .filter(Boolean);
      const paper = await manualIngest(ingestUrl, tags);
      onSelect(paper);
      setIngestUrl('');
      setIngestTags('');
    } catch (err) {
      console.error('Ingestion failed', err);
      setError('Ingestion failed - see console for details');
    }
  };

  return (
    <section>
      <div className="card">
        <h2>Manual Ingestion</h2>
        <input value={ingestUrl} onChange={(e) => setIngestUrl(e.target.value)} placeholder="arXiv URL" />
        <input value={ingestTags} onChange={(e) => setIngestTags(e.target.value)} placeholder="Tags (comma-separated)" />
        <button onClick={handleIngest} disabled={!ingestUrl}>Ingest Paper</button>
        {error && <p style={{ color: '#f87171' }}>{error}</p>}
      </div>

      <div className="card">
        <h2>Paper Catalog</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem' }}>
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search" />
          <input value={category} onChange={(e) => setCategory(e.target.value)} placeholder="Category" />
          <select value={status} onChange={(e) => setStatus(e.target.value as PaperStatus | '')}>
            {STATUS_OPTIONS.map((option) => (
              <option key={option.label} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <input type="checkbox" checked={starredOnly} onChange={(e) => setStarredOnly(e.target.checked)} />
            Starred only
          </label>
        </div>
        {loading ? (
          <p>Loading...</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Authors</th>
                  <th>Category</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {papers.map((paper) => (
                  <tr key={paper.id}>
                    <td>
                      <button onClick={() => onSelect(paper)} style={{ background: 'transparent', color: '#38bdf8' }}>
                        {paper.title}
                      </button>
                    </td>
                    <td>{paper.authors.join(', ')}</td>
                    <td>{paper.categories.join(', ')}</td>
                    <td>{new Date(paper.published_at).toLocaleDateString()}</td>
                    <td>
                      <span className="badge">{paper.status}</span>
                    </td>
                    <td style={{ display: 'flex', gap: '0.5rem' }}>
                      <button onClick={() => handleToggleStar(paper)}>{paper.starred ? 'Unstar' : 'Star'}</button>
                      <button onClick={() => handleMarkRead(paper)}>Mark Read</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}

import { useState } from 'react';
import { runTheory } from '../api';
import type { TheoryResponse } from '../types';

interface Props {
  llmAvailable: boolean;
}

export function TheoryModeView({ llmAvailable }: Props) {
  const [hypothesis, setHypothesis] = useState('');
  const [topK, setTopK] = useState(5);
  const [result, setResult] = useState<TheoryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    setError(null);
    setLoading(true);
    try {
      const response = await runTheory({ hypothesis, top_k: topK });
      setResult(response);
    } catch (err) {
      console.error('Theory mode failed', err);
      setError('Theory analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <h2>Theory Mode</h2>
      {!llmAvailable && <p style={{ color: '#f97316' }}>LLM unavailable. Theory mode is read-only.</p>}
      <textarea value={hypothesis} onChange={(e) => setHypothesis(e.target.value)} placeholder="Enter hypothesis" />
      <input type="number" min={1} max={10} value={topK} onChange={(e) => setTopK(Number(e.target.value))} />
      <button onClick={handleSubmit} disabled={!llmAvailable || !hypothesis || loading}>
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>
      {error && <p style={{ color: '#f87171' }}>{error}</p>}
      {result && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
          <article className="card">
            <h3>Pro Arguments</h3>
            {result.pro.length === 0 && <p>No supporting evidence.</p>}
            {result.pro.map((argument) => (
              <div key={argument.paper_id}>
                <strong>{argument.title}</strong>
                <p>{argument.argument}</p>
                <small>Relevance {(argument.relevance * 100).toFixed(1)}%</small>
              </div>
            ))}
          </article>
          <article className="card">
            <h3>Contra Arguments</h3>
            {result.contra.length === 0 && <p>No contradicting evidence.</p>}
            {result.contra.map((argument) => (
              <div key={argument.paper_id}>
                <strong>{argument.title}</strong>
                <p>{argument.argument}</p>
                <small>Relevance {(argument.relevance * 100).toFixed(1)}%</small>
              </div>
            ))}
          </article>
        </div>
      )}
    </section>
  );
}

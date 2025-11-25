import { useEffect, useState } from 'react';
import { addNote, fetchGraph, fetchSimilar, fetchPaper } from '../api';
import type { GraphResponse, Paper, SimilarPaper } from '../types';

interface Props {
  paper: Paper | null;
  onUpdate: (paper: Paper) => void;
}

export function PaperDetailView({ paper, onUpdate }: Props) {
  const [current, setCurrent] = useState<Paper | null>(paper);
  const [noteText, setNoteText] = useState('');
  const [similar, setSimilar] = useState<SimilarPaper[]>([]);
  const [graph, setGraph] = useState<GraphResponse | null>(null);

  useEffect(() => {
    setCurrent(paper);
    if (!paper) return;
    const load = async () => {
      const [fresh, similarPapers, graphData] = await Promise.all([
        fetchPaper(paper.id),
        fetchSimilar(paper.id),
        fetchGraph(paper.id),
      ]);
      setCurrent(fresh);
      setSimilar(similarPapers);
      setGraph(graphData);
    };
    load().catch((error) => console.error('Failed loading detail', error));
  }, [paper]);

  if (!current) {
    return (
      <section className="card">
        <p>Select a paper to see details.</p>
      </section>
    );
  }

  const handleAddNote = async () => {
    const updated = await addNote(current.id, noteText);
    setNoteText('');
    setCurrent(updated);
    onUpdate(updated);
  };

  return (
    <section className="card">
      <h2>{current.title}</h2>
      <p>
        <strong>Authors:</strong> {current.authors.join(', ')}
      </p>
      <p>
        <strong>Categories:</strong> {current.categories.join(', ')}
      </p>
      <p>
        <strong>Abstract:</strong> {current.abstract}
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
        <article className="card">
          <h3>Summary</h3>
          <p>{current.summary}</p>
        </article>
        <article className="card">
          <h3>Methodology</h3>
          <p>{current.methodology}</p>
        </article>
        <article className="card">
          <h3>Results</h3>
          <p>{current.results}</p>
        </article>
        <article className="card">
          <h3>Further Work</h3>
          <p>{current.further_work}</p>
        </article>
      </div>
      <div className="card">
        <h3>Notes</h3>
        <ul>
          {current.notes.map((note) => (
            <li key={note.id}>
              <small>{new Date(note.created_at).toLocaleString()}:</small> {note.text}
            </li>
          ))}
        </ul>
        <textarea value={noteText} onChange={(e) => setNoteText(e.target.value)} placeholder="Add a note" />
        <button onClick={handleAddNote} disabled={!noteText.trim()}>
          Save Note
        </button>
      </div>
      <div className="card">
        <h3>Similar Papers</h3>
        {similar.length === 0 ? <p>No similar papers yet.</p> : (
          <ul>
            {similar.map((item) => (
              <li key={item.paper_id}>
                {item.title} – score {(item.score * 100).toFixed(1)}%
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="card">
        <h3>Relationship Graph</h3>
        {graph ? (
          <div>
            <p>{graph.nodes.length} nodes / {graph.edges.length} edges</p>
            <ul>
              {graph.edges.map((edge) => (
                <li key={`${edge.source}-${edge.target}`}>
                  {edge.source} → {edge.target} ({edge.reason})
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p>No graph data.</p>
        )}
      </div>
      <a href={current.pdf_url} target="_blank" rel="noreferrer">
        Open PDF
      </a>
    </section>
  );
}

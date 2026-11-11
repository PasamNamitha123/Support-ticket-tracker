export default function TicketList({ tickets, onStatusChange }) {
  if (tickets.length === 0) return <p className="muted">No tickets yet. Create your first one above.</p>;

  return (
    <div>
      <h2>Your tickets</h2>
      {tickets.map((t) => (
        <article className="card" key={t.id}>
          <div className="row">
            <h3>{t.title}</h3>
            <select value={t.status} onChange={(e) => onStatusChange(t.id, e.target.value)}>
              <option value="open">Open</option>
              <option value="in_progress">In progress</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
          <div className="badges">
            <span className="badge">{t.category.replace("_", " ")}</span>
            <span className={`badge priority-${t.priority}`}>{t.priority} priority</span>
            <span className="badge">{t.ai_generated ? "AI triage" : "Rule-based triage"}</span>
          </div>
          <p>{t.description}</p>
          {t.summary && (
            <p>
              <strong>Summary:</strong> {t.summary}
            </p>
          )}
          {t.suggested_reply && (
            <p>
              <strong>Suggested reply:</strong> {t.suggested_reply}
            </p>
          )}
        </article>
      ))}
    </div>
  );
}

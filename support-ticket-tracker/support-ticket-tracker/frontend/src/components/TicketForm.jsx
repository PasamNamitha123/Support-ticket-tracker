import { useState } from "react";

export default function TicketForm({ onCreate }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    const ok = await onCreate(title, description);
    setBusy(false);
    if (ok) {
      setTitle("");
      setDescription("");
    }
  }

  return (
    <form className="card" onSubmit={submit}>
      <h2>New ticket</h2>
      <label>
        Title
        <input value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} required />
      </label>
      <label>
        Describe the problem
        <textarea
          rows={4}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={5000}
          required
        />
      </label>
      <button type="submit" disabled={busy}>
        {busy ? "Submitting (triaging)..." : "Submit ticket"}
      </button>
    </form>
  );
}

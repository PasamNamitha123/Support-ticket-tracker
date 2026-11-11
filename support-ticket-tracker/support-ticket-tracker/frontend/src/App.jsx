import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import AuthForm from "./components/AuthForm.jsx";
import TicketForm from "./components/TicketForm.jsx";
import TicketList from "./components/TicketList.jsx";

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [email, setEmail] = useState("");
  const [tickets, setTickets] = useState([]);
  const [error, setError] = useState("");

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setToken(null);
    setTickets([]);
    setEmail("");
  }, []);

  const handleError = useCallback(
    (err) => {
      if (err.status === 401) logout(); // token expired or invalid
      else setError(err.message);
    },
    [logout]
  );

  useEffect(() => {
    if (!token) return;
    api("/users/me", { token }).then((u) => setEmail(u.email)).catch(handleError);
    api("/tickets", { token }).then(setTickets).catch(handleError);
  }, [token, handleError]);

  function handleAuth(newToken) {
    localStorage.setItem("token", newToken);
    setToken(newToken);
  }

  async function createTicket(title, description) {
    setError("");
    try {
      const ticket = await api("/tickets", { method: "POST", token, json: { title, description } });
      setTickets((prev) => [ticket, ...prev]);
      return true;
    } catch (err) {
      handleError(err);
      return false;
    }
  }

  async function changeStatus(id, status) {
    try {
      const updated = await api(`/tickets/${id}/status`, { method: "PATCH", token, json: { status } });
      setTickets((prev) => prev.map((t) => (t.id === id ? updated : t)));
    } catch (err) {
      handleError(err);
    }
  }

  if (!token) return <AuthForm onAuth={handleAuth} />;

  return (
    <div className="container">
      <header className="topbar">
        <h1>Support Tickets</h1>
        <div>
          <span className="muted">{email}</span>
          <button className="secondary" onClick={logout}>Log out</button>
        </div>
      </header>
      {error && <p className="error">{error}</p>}
      <TicketForm onCreate={createTicket} />
      <TicketList tickets={tickets} onStatusChange={changeStatus} />
    </div>
  );
}

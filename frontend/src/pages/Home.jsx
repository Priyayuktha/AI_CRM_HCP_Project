import { ChatPanel } from '../components/ChatPanel';
import { InteractionForm } from '../components/InteractionForm';
import { Notification } from '../components/Notification';

export function Home() {
  return (
    <main className="app-shell">
      <Notification />
      <section className="dashboard-grid" aria-label="AI CRM dashboard">
        <InteractionForm />
        <ChatPanel />
      </section>
    </main>
  );
}

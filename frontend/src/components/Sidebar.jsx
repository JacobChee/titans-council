import './Sidebar.css';

const TITANS = [
  { emoji: '⚡', name: 'Elon Musk' },
  { emoji: '🍎', name: 'Steve Jobs' },
  { emoji: '📦', name: 'Jeff Bezos' },
  { emoji: '💪', name: 'Alex Hormozi' },
  { emoji: '🟢', name: 'Jensen Huang' },
];

export default function Sidebar({ conversations, currentConversationId, onSelectConversation, onNewConversation }) {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <span className="sidebar-logo-icon">🏛️</span>
          <div>
            <div className="sidebar-logo-text">Titans Council</div>
            <div className="sidebar-logo-sub">5 minds. 1 answer.</div>
          </div>
        </div>
        <button className="new-conversation-btn" onClick={onNewConversation}>
          + New Question
        </button>
      </div>

      <div className="sidebar-titans">
        <div className="sidebar-titans-label">The Council</div>
        {TITANS.map(t => (
          <div key={t.name} className="sidebar-titan">
            <span className="sidebar-titan-emoji">{t.emoji}</span>
            <span className="sidebar-titan-name">{t.name}</span>
          </div>
        ))}
      </div>

      <div className="conversation-list" />
    </div>
  );
}

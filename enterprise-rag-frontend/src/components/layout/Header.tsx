import { useSettingsStore } from '../../store/settingsStore';

export function Header() {
  const { settings, updateSettings } = useSettingsStore();

  return (
    <header className="app-header">
      <div>
        <p className="eyebrow">ENTERPRISE KNOWLEDGE</p>
        <h1>Workspace</h1>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <button
          className="icon-button"
          onClick={() => updateSettings({ theme: settings.theme === 'dark' ? 'light' : 'dark' })}
          aria-label="Toggle theme"
          style={{ width: '36px', height: '36px', borderRadius: '8px', border: '1px solid var(--line)', background: 'transparent' }}
        >
          {settings.theme === 'dark' ? '☀' : '◐'}
        </button>

        <button className="feedback-btn" onClick={() => alert('Feedback submitted! Thank you for helping us improve Rag chatbot.')}>
          Give feedback
        </button>

        <div className="avatar" style={{ width: '36px', height: '36px', borderRadius: '50%', background: '#dff3e7', color: '#27735c', display: 'grid', placeItems: 'center', fontWeight: '800', fontSize: '11px' }}>
          TM
        </div>
      </div>
    </header>
  );
}

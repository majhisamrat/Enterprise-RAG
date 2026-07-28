import { useSettingsStore } from '../../store/settingsStore';

export function ModelCard() {
  const { settings } = useSettingsStore();

  return (
    <div className="card model-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div>
        <p className="eyebrow" style={{ marginBottom: '4px' }}>ACTIVE CONFIGURATION</p>
        <strong style={{ fontSize: '18px' }}>{settings.llmProvider.toUpperCase()}</strong>
        <span style={{ marginLeft: '12px', fontSize: '13px', color: 'var(--muted)' }}>
          {settings.embeddingModel} • Top {settings.topK} retrieval • {settings.maxTokens} output tokens
        </span>
      </div>
      <span className="badge success">Active Engine</span>
    </div>
  );
}

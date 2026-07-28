import { ModelSelector } from '../components/settings/ModelSelector';
import { EmbeddingSelector } from '../components/settings/EmbeddingSelector';
import { ThemeSwitch } from '../components/settings/ThemeSwitch';
import { ProviderCard } from '../components/settings/ProviderCard';
import { useSettingsStore } from '../store/settingsStore';

export function Settings() {
  const { settings, updateSettings } = useSettingsStore();

  return (
    <div>
      <div className="page-heading">
        <div>
          <p className="eyebrow">CONFIGURATION</p>
          <h2>Workspace Settings</h2>
          <p>Configure model inference providers, chunking parameters, and vector search parameters.</p>
        </div>
      </div>

      <div className="settings-grid">
        <ModelSelector />
        <EmbeddingSelector />

        <div className="card settings-card">
          <h3>Chunking Strategy</h3>
          <label className="field">
            Chunk Size (tokens)
            <input
              type="number"
              value={settings.chunkSize}
              onChange={(e) => updateSettings({ chunkSize: Number(e.target.value) })}
            />
          </label>
          <label className="field">
            Chunk Overlap (tokens)
            <input
              type="number"
              value={settings.chunkOverlap}
              onChange={(e) => updateSettings({ chunkOverlap: Number(e.target.value) })}
            />
          </label>
          <label className="switch-field">
            <span>Enable Cross-Encoder Reranker</span>
            <input
              type="checkbox"
              checked={settings.enableReranker}
              onChange={(e) => updateSettings({ enableReranker: e.target.checked })}
            />
            <span></span>
          </label>
        </div>

        <ThemeSwitch />
      </div>

      <div style={{ marginTop: '30px' }}>
        <h3 style={{ fontSize: '16px', letterSpacing: '-0.03em', marginBottom: '14px' }}>System Integrations</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          <ProviderCard name="FastAPI Backend" status="Connected" />
          <ProviderCard name="Qdrant Vector Database" status="Online" />
          <ProviderCard name="Redis Cache & Memory" status="Active" />
        </div>
      </div>
    </div>
  );
}

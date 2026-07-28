import { useSettingsStore } from '../../store/settingsStore';

export function EmbeddingSelector() {
  const { settings, updateSettings } = useSettingsStore();

  return (
    <div className="card settings-card">
      <h3>Vector Retrieval Config</h3>
      <label className="field">
        Embedding Model
        <select
          value={settings.embeddingModel}
          onChange={(e) => updateSettings({ embeddingModel: e.target.value })}
        >
          <option value="BAAI/bge-small-en-v1.5">BAAI/bge-small-en-v1.5 (Fast)</option>
          <option value="BAAI/bge-base-en-v1.5">BAAI/bge-base-en-v1.5 (Balanced)</option>
          <option value="text-embedding-3-small">OpenAI text-embedding-3-small</option>
        </select>
      </label>
      <label className="field">
        Top-K Chunks
        <input
          type="number"
          value={settings.topK}
          onChange={(e) => updateSettings({ topK: Number(e.target.value) })}
        />
      </label>
    </div>
  );
}

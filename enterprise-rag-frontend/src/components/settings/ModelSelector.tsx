import { useSettingsStore } from '../../store/settingsStore';

export function ModelSelector() {
  const { settings, updateSettings } = useSettingsStore();

  return (
    <div className="card settings-card">
      <h3>LLM Provider & Model</h3>
      <label className="field">
        Provider
        <select
          value={settings.llmProvider}
          onChange={(e) => updateSettings({ llmProvider: e.target.value as any })}
        >
          <option value="groq">Groq (Ultra-fast LPUs)</option>
          <option value="cerebras">Cerebras CS-3</option>
          <option value="gemini">Google Gemini 1.5 Flash</option>
          <option value="openai">OpenAI GPT-4o</option>
        </select>
      </label>
      <label className="field">
        Max Output Tokens
        <input
          type="number"
          value={settings.maxTokens}
          onChange={(e) => updateSettings({ maxTokens: Number(e.target.value) })}
        />
      </label>
    </div>
  );
}

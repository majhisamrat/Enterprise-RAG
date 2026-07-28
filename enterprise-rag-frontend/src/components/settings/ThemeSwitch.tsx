import { useSettingsStore } from '../../store/settingsStore';

export function ThemeSwitch() {
  const { settings, updateSettings } = useSettingsStore();

  return (
    <div className="card settings-card">
      <h3>Appearance</h3>
      <label className="switch-field">
        <span>Dark Mode</span>
        <input
          type="checkbox"
          checked={settings.theme === 'dark'}
          onChange={(e) => updateSettings({ theme: e.target.checked ? 'dark' : 'light' })}
        />
        <span></span>
      </label>
    </div>
  );
}

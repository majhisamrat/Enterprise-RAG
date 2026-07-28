import { useEffect } from 'react';
import { useSettingsStore } from '../store/settingsStore';

export function useTheme() {
  const theme = useSettingsStore((s) => s.settings.theme);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return theme;
}

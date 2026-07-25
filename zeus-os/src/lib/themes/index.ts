export type ThemeId = 'catppuccin-mocha' | 'tokyo-night' | 'gruvbox-dark';

export interface ThemeMeta {
  id: ThemeId;
  label: string;
  preview: { bg: string; accent: string };
}

export const THEMES: ThemeMeta[] = [
  { id: 'catppuccin-mocha', label: 'Catppuccin Mocha', preview: { bg: '#1e1e2e', accent: '#89b4fa' } },
  { id: 'tokyo-night', label: 'Tokyo Night', preview: { bg: '#1a1b26', accent: '#7aa2f7' } },
  { id: 'gruvbox-dark', label: 'Gruvbox Dark', preview: { bg: '#282828', accent: '#fabd2f' } }
];

export function applyTheme(id: ThemeId) {
  if (typeof document !== 'undefined') {
    document.documentElement.dataset.theme = id;
  }
}

export function nextTheme(current: ThemeId): ThemeId {
  const i = THEMES.findIndex((t) => t.id === current);
  return THEMES[(i + 1) % THEMES.length].id;
}

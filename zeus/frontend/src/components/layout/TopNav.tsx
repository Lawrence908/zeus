// zeus/frontend/src/components/layout/TopNav.tsx
import { NavLink, useNavigate } from 'react-router-dom'
import { useSettingsStore } from '../../store/settingsStore'
import { useVoiceStore } from '../../store/voiceStore'

interface NavItem {
  to: string
  label: string
}

const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Chat' },
  { to: '/ingest', label: 'Ingest' },
  { to: '/agents', label: 'Agents' },
  { to: '/settings', label: 'Settings' },
]

interface IconButtonProps {
  icon: string
  title: string
  onClick?: () => void
}

function IconButton({ icon, title, onClick }: IconButtonProps) {
  return (
    <button
      title={title}
      onClick={onClick}
      className="w-8 h-8 flex items-center justify-center text-on-surface-variant hover:text-on-surface transition-colors"
    >
      <span className="material-symbols-outlined text-[18px]">{icon}</span>
    </button>
  )
}

export function TopNav() {
  const { theme, setTheme } = useSettingsStore()
  const { connected: voiceConnected } = useVoiceStore()
  const navigate = useNavigate()

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark')

  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-[52px] bg-surface-container-lowest border-b border-outline-variant/20 flex items-center px-4 gap-6">
      {/* Logo */}
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-1.5 font-headline font-bold text-base tracking-tight shrink-0"
        style={{ color: '#00d4ff' }}
      >
        <span>⚡</span>
        <span>Zeus</span>
      </button>

      {/* Nav links */}
      <nav className="flex items-center gap-1 h-full">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              [
                'relative h-full flex items-center px-3 text-sm font-label font-medium transition-colors',
                isActive
                  ? 'text-primary-container after:absolute after:bottom-0 after:left-3 after:right-3 after:h-[2px] after:bg-primary-container'
                  : 'text-on-surface-variant hover:text-on-surface',
              ].join(' ')
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Voice connection status */}
      {voiceConnected && (
        <div className="flex items-center gap-1.5 text-xs font-label font-medium text-on-surface-variant">
          <span className="w-1.5 h-1.5 rounded-full bg-primary-container pulsar" />
          <span className="uppercase tracking-widest text-[10px]">Voice Active</span>
        </div>
      )}

      {/* Icon buttons */}
      <div className="flex items-center gap-0.5">
        <IconButton icon="cell_tower" title="Signal" />
        <IconButton icon="shield_with_heart" title="Aegis" />
        <IconButton icon="settings_voice" title="Voice Settings" />
        <IconButton icon="contrast" title="Toggle Theme" onClick={toggleTheme} />
      </div>
    </header>
  )
}

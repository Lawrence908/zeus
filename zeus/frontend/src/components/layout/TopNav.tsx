// zeus/frontend/src/components/layout/TopNav.tsx
import { useState, type ReactNode } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useSettingsStore } from '../../store/settingsStore'
import { useVoiceStore } from '../../store/voiceStore'

interface NavItem {
  to: string
  label: string
}

const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Chat' },
  { to: '/memories', label: 'Memories' },
  { to: '/knowledge', label: 'Knowledge' },
  { to: '/ingest', label: 'Ingest' },
  { to: '/agents', label: 'Agents' },
  { to: '/jobs', label: 'Jobs' },
  { to: '/tools', label: 'Tools' },
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
      className="w-9 h-9 flex items-center justify-center text-on-surface-variant hover:text-on-surface transition-colors"
    >
      <span className="material-symbols-outlined text-[18px]">{icon}</span>
    </button>
  )
}

interface TopNavProps {
  // Page-specific controls shown only on mobile, to the left/right of the bar.
  // Chat uses these to toggle its sessions / status drawers.
  mobileLeftSlot?: ReactNode
  mobileRightSlot?: ReactNode
}

export function TopNav({ mobileLeftSlot, mobileRightSlot }: TopNavProps = {}) {
  const { theme, setTheme } = useSettingsStore()
  const { connected: voiceConnected } = useVoiceStore()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark')

  return (
    <>
      <header className="fixed top-0 left-0 right-0 z-50 h-[52px] bg-surface-container-lowest border-b border-outline-variant/20 flex items-center px-3 md:px-4 gap-2 md:gap-6">
        {/* Mobile: hamburger */}
        <button
          onClick={() => setMenuOpen(true)}
          className="md:hidden w-9 h-9 -ml-1 flex items-center justify-center text-on-surface-variant hover:text-on-surface"
          title="Menu"
          aria-label="Open navigation menu"
        >
          <span className="material-symbols-outlined text-[22px]">menu</span>
        </button>

        {/* Page-specific mobile control (left) */}
        {mobileLeftSlot && <div className="md:hidden flex items-center">{mobileLeftSlot}</div>}

        {/* Logo */}
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-1.5 font-headline font-bold text-base tracking-tight shrink-0"
          style={{ color: '#00d4ff' }}
        >
          <span>⚡</span>
          <span>Zeus</span>
        </button>

        {/* Desktop nav links */}
        <nav className="hidden md:flex items-center gap-1 h-full">
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
            <span className="hidden sm:inline uppercase tracking-widest text-[10px]">Voice Active</span>
          </div>
        )}

        {/* Desktop icon buttons */}
        <div className="hidden md:flex items-center gap-0.5">
          <IconButton icon="cell_tower" title="Signal" />
          <IconButton icon="shield_with_heart" title="Aegis" />
          <IconButton icon="settings_voice" title="Voice Settings" />
          <IconButton icon="contrast" title="Toggle Theme" onClick={toggleTheme} />
        </div>

        {/* Page-specific mobile control (right) */}
        {mobileRightSlot && <div className="md:hidden flex items-center">{mobileRightSlot}</div>}
      </header>

      {/* Mobile nav drawer */}
      {menuOpen && (
        <div className="md:hidden fixed inset-0 z-[60]">
          <button
            className="absolute inset-0 bg-black/50"
            aria-label="Close menu"
            onClick={() => setMenuOpen(false)}
          />
          <nav className="absolute top-0 left-0 bottom-0 w-[80vw] max-w-[300px] bg-surface-container-lowest border-r border-outline-variant/20 flex flex-col shadow-2xl">
            <div className="h-[52px] shrink-0 flex items-center justify-between px-4 border-b border-outline-variant/20">
              <span className="flex items-center gap-1.5 font-headline font-bold text-base" style={{ color: '#00d4ff' }}>
                <span>⚡</span>
                <span>Zeus</span>
              </span>
              <button
                onClick={() => setMenuOpen(false)}
                className="w-9 h-9 flex items-center justify-center text-on-surface-variant hover:text-on-surface"
                aria-label="Close menu"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <div className="flex-1 overflow-y-auto py-2">
              {NAV_ITEMS.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  onClick={() => setMenuOpen(false)}
                  className={({ isActive }) =>
                    [
                      'flex items-center px-5 py-3 text-sm font-label font-medium border-l-2 transition-colors',
                      isActive
                        ? 'border-primary-container text-primary-container bg-surface-container-low/60'
                        : 'border-transparent text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low/30',
                    ].join(' ')
                  }
                  style={({ isActive }: { isActive: boolean }) => (isActive ? { color: '#00d4ff', borderColor: '#00d4ff' } : undefined)}
                >
                  {item.label}
                </NavLink>
              ))}
            </div>
            <div className="shrink-0 flex items-center gap-1 px-3 py-2 border-t border-outline-variant/20">
              <IconButton icon="cell_tower" title="Signal" />
              <IconButton icon="shield_with_heart" title="Aegis" />
              <IconButton icon="settings_voice" title="Voice Settings" />
              <IconButton icon="contrast" title="Toggle Theme" onClick={toggleTheme} />
            </div>
          </nav>
        </div>
      )}
    </>
  )
}

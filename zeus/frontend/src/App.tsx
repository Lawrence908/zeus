// zeus/frontend/src/App.tsx
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import { ChatPage } from './pages/ChatPage'
import { VizPage } from './pages/VizPage'
import { AgentsPage } from './pages/AgentsPage'
import { SettingsPage } from './pages/SettingsPage'

const router = createBrowserRouter([
  {
    path: '/',
    element: <ChatPage />,
  },
  {
    path: '/viz',
    element: <VizPage />,
  },
  {
    path: '/agents',
    element: <AgentsPage />,
  },
  {
    path: '/settings',
    element: <SettingsPage />,
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
])

export function App() {
  return <RouterProvider router={router} />
}

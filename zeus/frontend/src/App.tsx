// zeus/frontend/src/App.tsx
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import { ChatPage } from './pages/ChatPage'
import { VizPage } from './pages/VizPage'
import { AgentsPage } from './pages/AgentsPage'
import { SettingsPage } from './pages/SettingsPage'
import { IngestPage } from './pages/IngestPage'
import { MemoriesPage } from './pages/MemoriesPage'
import { KnowledgePage } from './pages/KnowledgePage'
import { ToolsPage } from './pages/ToolsPage'
import { JobsPage } from './pages/JobsPage'

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
    path: '/ingest',
    element: <IngestPage />,
  },
  {
    path: '/memories',
    element: <MemoriesPage />,
  },
  {
    path: '/knowledge',
    element: <KnowledgePage />,
  },
  {
    path: '/tools',
    element: <ToolsPage />,
  },
  {
    path: '/jobs',
    element: <JobsPage />,
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
])

export function App() {
  return <RouterProvider router={router} />
}

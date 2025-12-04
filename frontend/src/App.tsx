import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Layout from './components/Layout';
import SessionDashboard from './components/SessionDashboard';
import ChatInterface from './components/ChatInterface';
import AgentBuilder from './components/AgentBuilder';
import ChatPlayground from './components/ChatPlayground';
import MobileTesterChat from './components/MobileTesterChat';
import MobileTesterChatSessions from './components/MobileTesterChatSessions';
import MCPManagementDashboard from './components/MCPManagementDashboard';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import AppProviderWithToast from './AppProviderWithToast';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <SessionDashboard />,
      } as any,
      {
        path: 'chat',
        element: <ChatInterface />,
      },
      {
        path: 'chat/:sessionId',
        element: <ChatInterface />,
      },
      {
        path: 'agents',
        element: <AgentBuilder />,
      },
      {
        path: 'playground',
        element: <ChatPlayground />,
      },
      {
        path: 'mcp',
        element: <MCPManagementDashboard />,
      },
      {
        path: 'mcp管理',
        element: <MCPManagementDashboard />,
      },
    ],
  },
  {
    path: '/tester/:agentId',
    children: [
      {
        index: true,
        element: <MobileTesterChatSessions />,
      },
      {
        path: 'sessions',
        element: <MobileTesterChatSessions />,
      },
      {
        path: 'chat/:sessionId',
        element: <MobileTesterChat />,
      }
    ],
  }
]);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppProviderWithToast>
        <RouterProvider router={router} />
        <ReactQueryDevtools initialIsOpen={false} />
      </AppProviderWithToast>
    </QueryClientProvider>
  );
}

export default App;

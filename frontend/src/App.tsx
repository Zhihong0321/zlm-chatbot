import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Layout from './components/Layout';
import SessionDashboard from './components/SessionDashboard';
import ChatInterface from './components/ChatInterface';
import AgentBuilder from './components/AgentBuilder';
import ChatPlayground from './components/ChatPlayground';
import MobileTesterChat from './components/MobileTesterChat';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AppProvider } from './context/AppContext';

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
    ],
  },
  {
    path: '/tester/:agentId',
    element: <MobileTesterChat />,
  }
]);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppProvider>
        <RouterProvider router={router} />
        <ReactQueryDevtools initialIsOpen={false} />
      </AppProvider>
    </QueryClientProvider>
  );
}

export default App;

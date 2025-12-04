import React from 'react';
import { AppProvider } from './context/AppContext';

interface AppProviderWithToastProps {
  children: React.ReactNode;
}

const AppProviderWithToast = ({ children }: AppProviderWithToastProps) => {
  return <AppProvider>{children}</AppProvider>;
};

export default AppProviderWithToast;

// Provide a simple alert hook for MCP
export const useAppToast = () => {
  return { notify: alert };
};

import React from 'react';
import { AppProvider } from './context/AppContext';
import { ToastProvider } from './hooks/useToast';

interface AppProviderWithToastProps {
  children: React.ReactNode;
}

const AppProviderWithToastContext = React.createContext<{
  showToast: (options: { message: string; type?: 'success' | 'error' | 'warning' | 'info' }) => void;
}>({
  showToast: () => {},
});

const useAppToast = () => React.useContext(AppProviderWithToastContext);

const AppProviderWithToast = ({ children }: AppProviderWithToastProps) => {
  const [toasts, setToasts] = React.useState<Array<{
    id: string;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
  }>>([]);

  const showToast = React.useCallback((options: { 
    message: string; 
    type?: 'success' | 'error' | 'warning' | 'info' 
  }) => {
    const id = Date.now().toString();
    const newToast = {
      id,
      message: options.message,
      type: options.type || 'info',
    };
    
    setToasts(prev => [...prev, newToast]);
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3000);
    
    return id;
  }, []);

  const hideToast = React.useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <AppProviderWithToastContext.Provider value={{ showToast }}>
      <AppProvider>
        {children}
        <ToastProvider toasts={toasts} onHide={hideToast} />
      </AppProvider>
    </AppProviderWithToastContext.Provider>
  );
};

export default AppProviderWithToast;
export { useAppToast };

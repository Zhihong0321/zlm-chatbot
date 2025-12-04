import React from 'react';
import { AppProvider } from './context/AppContext';

interface AppProviderWithToastProps {
  children: React.ReactNode;
}

const AppProviderWithToastContext = React.createContext<{
  notify: (message: string) => void;
}>({
  notify: () => {},
});

export const useAppToast = () => React.useContext(AppProviderWithToastContext);

const AppProviderWithToast = ({ children }: AppProviderWithToastProps) => {
  const [notification, setNotification] = React.useState<string>('');

  const notify = React.useCallback((message: string) => {
    setNotification(message);
    setTimeout(() => setNotification(''), 3000);
  }, []);

  return (
    <AppProviderWithToastContext.Provider value={{ notify }}>
      <AppProvider>
        {children}
        {notification && (
          <div className="fixed top-4 right-4 z-50 bg-green-500 text-white px-4 py-2 rounded-md">
            {notification}
          </div>
        )}
      </AppProvider>
    </AppProviderWithToastContext.Provider>
  );
};

export default AppProviderWithToast;
export { useAppToast };

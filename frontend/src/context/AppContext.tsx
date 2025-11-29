import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { Agent, Session, Message } from '../types';

interface AppState {
  agents: Agent[];
  sessions: Session[];
  currentSession: Session | null;
  messages: Message[];
  loading: boolean;
  error: string | null;
}

type AppAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_AGENTS'; payload: Agent[] }
  | { type: 'SET_SESSIONS'; payload: Session[] }
  | { type: 'SET_CURRENT_SESSION'; payload: Session | null }
  | { type: 'SET_MESSAGES'; payload: Message[] }
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'ADD_AGENT'; payload: Agent }
  | { type: 'ADD_SESSION'; payload: Session }
  | { type: 'DELETE_SESSION'; payload: string }
  | { type: 'UPDATE_SESSION'; payload: Session };

const initialState: AppState = {
  agents: [],
  sessions: [],
  currentSession: null,
  messages: [],
  loading: false,
  error: null,
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_AGENTS':
      return { ...state, agents: action.payload };
    case 'SET_SESSIONS':
      return { ...state, sessions: action.payload };
    case 'SET_CURRENT_SESSION':
      return { ...state, currentSession: action.payload };
    case 'SET_MESSAGES':
      return { ...state, messages: action.payload };
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] };
    case 'ADD_AGENT':
      return { ...state, agents: [...state.agents, action.payload] };
    case 'ADD_SESSION':
      return { ...state, sessions: [...state.sessions, action.payload] };
    case 'DELETE_SESSION':
      return {
        ...state,
        sessions: state.sessions.filter(s => s.id !== action.payload),
        currentSession: state.currentSession?.id === action.payload ? null : state.currentSession,
      };
    case 'UPDATE_SESSION':
      return {
        ...state,
        sessions: state.sessions.map(s => s.id === action.payload.id ? action.payload : s),
        currentSession: state.currentSession?.id === action.payload.id ? action.payload : state.currentSession,
      };
    default:
      return state;
  }
}

const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
} | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
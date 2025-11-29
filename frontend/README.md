# Frontend for Z.ai Chatbot API Server

This is the React frontend for the Z.ai Chatbot API Server, providing a modern web interface for interacting with AI agents.

## Features

- **Modern React Application**: Built with React 18, TypeScript, and Vite for optimal performance
- **Chat Interface**: Full-featured chat interface with real-time messaging
- **Agent Management**: Create and manage custom AI agents with different personalities
- **Session Dashboard**: View and manage all chat sessions
- **Playground**: Test agents before using them in conversations
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS
- **File Upload**: Support for knowledge file uploads (max 50KB)

## Technology Stack

- **Frontend**: React 18 with TypeScript
- **Build Tool**: Vite
- **Routing**: React Router v6
- **State Management**: React Query + React Context
- **UI Framework**: Tailwind CSS
- **HTTP Client**: Axios
- **Components**: Headless UI + Heroicons

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Create environment file:
   ```bash
   cp .env.example .env
   ```

5. Start the development server:
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:5173`

## Environment Variables

- `VITE_API_BASE_URL`: URL of the backend API server (default: `http://localhost:8000`)

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── components/          # React components
│   ├── Layout.tsx       # Main layout with navigation
│   ├── ChatInterface.tsx # Chat component
│   ├── AgentBuilder.tsx # Agent creation interface
│   ├── SessionDashboard.tsx # Session management
│   └── ChatPlayground.tsx # Agent testing
├── context/             # React Context
│   └── AppContext.tsx   # Global state management
├── hooks/               # Custom hooks
│   └── useApi.ts        # API integration hooks
├── services/            # API services
│   └── api.ts          # Axios configuration
├── types/               # TypeScript types
│   └── index.ts        # Interface definitions
└── App.tsx             # Main app component
```

## API Integration

The frontend connects to the backend API for:

- Agent management (CRUD operations)
- Session management (create, delete, list)
- Chat functionality (send messages, get history)
- File uploads for knowledge injection

## Deployment

The frontend is configured for deployment with:

- **Docker**: Multi-stage build with Nginx
- **Railway**: Optimized for Railway platform deployment

### Docker Build

```bash
docker build -t chatbot-frontend .
```

## Features by Component

### Session Dashboard
- View all chat sessions
- Create new chats
- Delete existing sessions
- Navigate to specific conversations

### Chat Interface
- Real-time messaging
- Agent selection
- File upload support
- Message history
- Token usage display

### Agent Builder
- Create custom agents
- Configure model parameters
- Set system prompts
- Adjust temperature settings

### Playground
- Test agent responses
- Compare different agents
- Temporary sessions for testing
- Real-time response preview

## Design Principles

- **Mobile-First**: Responsive design works on all devices
- **Accessible**: Semantic HTML and keyboard navigation
- **Performant**: Optimized bundle size and lazy loading
- **User-Friendly**: Clear feedback and error handling
- **Modern**: Latest React patterns and best practices

## Contributing

1. Follow the existing code style
2. Use TypeScript for all new components
3. Test thoroughly before submitting changes
4. Keep components small and focused

This frontend provides a complete interface for the Z.ai Chatbot API Server, enabling users to interact with AI agents through a modern, intuitive web interface.

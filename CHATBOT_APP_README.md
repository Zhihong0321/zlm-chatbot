# Z.ai Chatbot API Server

A complete chatbot application built with FastAPI backend and React frontend, featuring Z.ai GLM model integration, session management, and Railway deployment.

## Features

### Backend (FastAPI)
- **Z.ai Integration**: Support for GLM-4.6, GLM-4.5, GLM-4.5V, GLM-4.5-Air, GLM-4.5-Flash models
- **Session Management**: Create, view, and manage chat sessions
- **Agent System**: Custom agents with different system prompts and models
- **Knowledge Files**: Upload and inject knowledge context (max 50KB)
- **RESTful API**: Well-documented endpoints with OpenAPI/Swagger
- **PostgreSQL Database**: Persistent storage with SQLAlchemy ORM

### Frontend (React)
- **Real-time Chat**: Interactive messaging with typing indicators
- **Agent Playground**: Test and compare different agents
- **Session Dashboard**: View, search, and manage all conversations
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Modern UI**: Built with Tailwind CSS and React Query

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Railway CLI (for deployment)
- Z.ai API key

### Local Development

1. **Clone and Setup Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your ZAI_API_KEY
   uvicorn main:app --reload
   ```

2. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Milestone Progress

### Current Status: **Milestone 6 - Full Deployment & Integration Testing** 🔄

| Milestone | Status | Key Features |
|-----------|--------|--------------|
| 1: Backend API | ✅ Complete | FastAPI, Database, Z.ai Integration |
| 2: Railway Deploy | ✅ Complete | Docker, Production Deployment |
| 3: Frontend Foundation | ✅ Complete | React, State Management |
| 4: Chat Interface | ✅ Complete | Real-time Chat, Agent Management |
| 5: Session Management | ✅ Complete | Search, Analytics, Bulk Operations |
| 6: Full Deployment | 🔄 In Progress | Production Integration |
| 7: Polish & Optimize | ⏳ Pending | Performance & UX |

## Deployment

### Automated Deployment (Recommended)

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Set Environment Variables**
   ```bash
   export ZAI_API_KEY="your_zai_api_key_here"
   export DATABASE_URL="postgresql://user:password@host:port/database"
   ```

3. **Run Deployment Script**
   ```bash
   # On Unix/Linux/macOS
   ./deploy-milestone-6.sh
   
   # On Windows
   deploy-milestone-6.bat
   ```

### Manual Deployment

#### Backend
```bash
cd backend
railway init
railway variables set ZAI_API_KEY=$ZAI_API_KEY
railway variables set DATABASE_URL=$DATABASE_URL
railway up
```

#### Frontend
```bash
cd frontend
railway init
echo "VITE_API_BASE_URL=https://your-backend.railway.app" > .env.production
railway up
```

## API Documentation

### Core Endpoints

#### Sessions
- `POST /api/v1/sessions` - Create new session
- `GET /api/v1/sessions/{id}` - Get session details
- `POST /api/v1/sessions/{id}/messages` - Send message
- `GET /api/v1/sessions/{id}/history` - Get conversation history
- `DELETE /api/v1/sessions/{id}` - Delete session

#### Agents
- `POST /api/v1/agents` - Create agent
- `GET /api/v1/agents` - List all agents
- `PUT /api/v1/agents/{id}` - Update agent
- `DELETE /api/v1/agents/{id}` - Delete agent

#### Knowledge Files
- `POST /api/v1/sessions/{id}/upload` - Upload knowledge file
- `GET /api/v1/sessions/{id}/knowledge` - Get knowledge files

### Health Check
- `GET /api/v1/ui/health` - Application health status

## Configuration

### Environment Variables

#### Backend
- `ZAI_API_KEY` - Z.ai API key for model access
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Server port (default: 8000)

#### Frontend
- `VITE_API_BASE_URL` - Backend API URL

### Database Schema

#### Tables
- `users` - User accounts
- `chat_sessions` - Chat conversation sessions
- `chat_messages` - Individual messages
- `agents` - AI agent configurations
- `session_knowledge` - Knowledge file attachments

## Z.ai Integration

### Models
- **GLM-4.6**: Latest flagship, best performance (128K context)
- **GLM-4.5**: High performance (96K context)
- **GLM-4.5V**: Vision/image analysis (16K context)
- **GLM-4.5-Air**: Cost-efficient (128K context)
- **GLM-4.5-Flash**: Free model with all features (128K context)

### Special Features
- **Reasoning Content**: Access to model's thinking process (coding endpoint)
- **Streaming Responses**: Real-time message generation
- **Function Calling**: For advanced agent capabilities

## Development Guide

### Project Structure
```
oneapi/
├── backend/              # FastAPI application
│   ├── app/             # Application code
│   │   ├── api/         # API routes
│   │   ├── core/        # Core functionality
│   │   ├── crud/        # Database operations
│   │   ├── db/          # Database setup
│   │   ├── models/      # SQLAlchemy models
│   │   └── schemas/     # Pydantic schemas
│   ├── alembic/         # Database migrations
│   └── tests/           # Backend tests
├── frontend/             # React application
│   ├── src/            # Source code
│   │   ├── components/ # React components
│   │   ├── hooks/      # Custom hooks
│   │   ├── pages/      # Page components
│   │   └── utils/      # Utility functions
│   └── public/         # Static assets
└── docs/               # Documentation
```

### Adding New Features

1. **Backend API Changes**
   - Update models in `backend/app/models/`
   - Create/update schemas in `backend/app/schemas/`
   - Implement CRUD operations in `backend/app/crud/`
   - Add API routes in `backend/app/api/`

2. **Frontend Changes**
   - Create components in `frontend/src/components/`
   - Add custom hooks in `frontend/src/hooks/`
   - Update API client if needed
   - Add tests as appropriate

### Testing

#### Backend Tests
```bash
cd backend
python -m pytest
```

#### Frontend Tests
```bash
cd frontend
npm test
```

## Monitoring & Maintenance

### Logs
- Application logs available in Railway dashboard
- Error tracking with detailed stack traces
- Performance metrics collection

### Backups
- Database backups configured in Railway
- Configuration backups in version control
- Recovery procedures documented

### Updates
- Regular dependency updates
- Security patches applied promptly
- Feature updates tested thoroughly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

### Documentation
- [Milestone Progress](milestone.md)
- [Deployment Guide](MILESTONE_6_README.md)
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)
- [API Documentation](http://localhost:8000/docs)

### Resources
- [Z.ai API Documentation](https://z.ai/docs)
- [Railway Documentation](https://docs.railway.app)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)

## License

This project is licensed under the MIT License.

---

**Current Status**: Working on Milestone 6 - Full Deployment & Integration Testing. See [MILESTONE_6_STATUS.md](MILESTONE_6_STATUS.md) for detailed progress.
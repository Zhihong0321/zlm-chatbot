# Chatbot API Server with Z.ai Integration

A complete backend API server for building AI chatbots using Z.ai's GLM models. This project provides session management, agent configuration, and knowledge file integration.

## Features

- 🤖 **Z.ai GLM Model Integration** - Support for GLM-4.6, GLM-4.5, GLM-4.5V, GLM-4.5-Air, GLM-4.5-Flash
- 🗣️ **Session Management** - Create, manage, and persist chat sessions
- 🎭 **Agent System** - Customizable agents with system prompts and model settings
- 📚 **Knowledge Integration** - Upload files to provide context for conversations
- 🚀 **Railway Ready** - One-click deployment with Railway
- 📊 **API Documentation** - Auto-generated OpenAPI/Swagger docs

## Quick Start

### 1. Setup Development Environment

```bash
# Clone and setup
git clone <repository-url>
cd oneapi
chmod +x setup-backend.sh
./setup-backend.sh

# Or manually:
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
```

### 2. Configure Environment

Edit the `.env` file:

```env
# Your Z.ai API key from https://z.ai/manage-apikey/apikey-list
ZAI_API_KEY=your_actual_api_key

# PostgreSQL database connection
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_db

# CORS origins (add your frontend URL)
CORS_ORIGINS=["http://localhost:3000"]
```

### 3. Run the Server

```bash
cd backend
python main.py
```

The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/ui/health

## API Endpoints

### Agents
- `POST /api/v1/agents` - Create new agent
- `GET /api/v1/agents` - List all agents
- `GET /api/v1/agents/{id}` - Get agent details
- `PUT /api/v1/agents/{id}` - Update agent
- `DELETE /api/v1/agents/{id}` - Delete agent

### Sessions
- `POST /api/v1/sessions` - Create new chat session
- `GET /api/v1/sessions` - List all sessions
- `GET /api/v1/sessions/{id}` - Get session details
- `DELETE /api/v1/sessions/{id}` - Delete session
- `GET /api/v1/sessions/{id}/history` - Get conversation history
- `GET /api/v1/sessions/{id}/knowledge` - Get session knowledge files

### Chat
- `POST /api/v1/chat/{session_id}/messages` - Send message to session
- `POST /api/v1/chat/{session_id}/upload` - Upload knowledge file
- `POST /api/v1/chat` - Chat with agent (creates sessions)

### UI
- `GET /api/v1/ui/health` - Health check endpoint

## Database Schema

The application uses PostgreSQL with the following tables:

- **agents** - Store agent configurations and prompts
- **chat_sessions** - Track conversation sessions
- **chat_messages** - Store individual messages
- **session_knowledge** - Knowledge files for context
- **users** - User management (prepared for future features)

## Railway Deployment

### 1. Connect Repository
1. Create a Railway account
2. Connect your GitHub repository
3. Select the backend folder as root directory

### 2. Configure Environment
Set these environment variables in Railway dashboard:
- `ZAI_API_KEY` - Your Z.ai API key
- `DATABASE_URL` - Railway PostgreSQL connection
- `PORT` - Railway port (automatically set)

### 3. Deploy
Railway will automatically:
- Build the Docker container
- Run database migrations
- Start the API server
- Provide a public URL

## Example Usage

### Create an Agent
```bash
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Code Assistant",
    "description": "Helps with programming questions",
    "system_prompt": "You are an expert programming assistant. Provide clear, helpful code examples.",
    "model": "glm-4.6",
    "temperature": 0.3
  }'
```

### Create a Session
```bash
curl -X POST "http://localhost:8000/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Help Session",
    "agent_id": 1
  }'
```

### Send a Message
```bash
curl -X POST "http://localhost:8000/api/v1/chat/1/messages" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'message=How do I create a Python virtual environment?'
```

## Development

### Running Tests
```bash
cd backend
pytest
```

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "Add new feature"
alembic upgrade head
```

### Adding New Models
1. Define model in `backend/app/models/models.py`
2. Add schema in `backend/app/schemas/schemas.py`
3. Add CRUD operations in `backend/app/crud/crud.py`
4. Create migration with Alembic
5. Add API endpoints as needed

## Security Features

- CORS configuration for frontend integration
- Input validation with Pydantic schemas
- SQL injection protection through SQLAlchemy
- Rate limiting ready (can be added with FastAPI middleware)
- API key management through environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review the Railway logs
- Ensure your environment variables are correctly set
- Verify your Z.ai API key is valid and has sufficient balance
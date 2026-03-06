# 🎓 Edunovas AI Learning Platform

> **Next-Generation AI-Powered Educational Ecosystem for Technical Excellence**

Edunovas is a comprehensive AI-driven learning platform that provides personalized mentorship, adaptive assessments, and career guidance for students pursuing technical careers. Built with React, FastAPI, and powered by advanced LLM technology.

![Edunovas Dashboard](https://img.shields.io/badge/Status-Production%20Ready-success)
![License](https://img.shields.io/badge/License-MIT-blue)
![React](https://img.shields.io/badge/React-19.2.0-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?logo=fastapi)

---

## ✨ Features

### 🤖 **8 Specialized AI Assistants**
- **Interview Coach** - Resume analysis, skill gap detection, personalized roadmaps
- **Quiz Master** - Adaptive assessments with AI-powered feedback
- **Coding Mentor** - Code review, bug detection, optimization suggestions
- **Career Pathfinder** - Structured learning paths with market insights
- **Teacher AI** - Concept explanations and academic support
- **Success Coach** - Motivation and progress tracking
- **Router** - Intelligent mode detection
- **Support Agent** - Platform assistance

### 🎯 **Core Capabilities**
- **Resume Intelligence** - OCR support (PDF, DOCX, Images) with skill extraction
- **Market Research** - Real-time job market data integration via DuckDuckGo
- **RAG System** - Knowledge base retrieval using FAISS + SentenceTransformers
- **Gamification** - XP points, levels, badges, and streak tracking
- **Admin Analytics** - Real-time metrics, domain distribution, skill mapping
- **Progress Tracking** - Quiz history, interview scores, coding patterns

---

## 🏗️ Architecture

```
Edunovas/
├── src/                    # React Frontend
│   ├── components/         # Reusable UI components
│   ├── pages/             # Main application pages
│   │   └── forge/         # Student learning modules
│   ├── hooks/             # Custom React hooks
│   ├── data/              # Static configurations
│   └── types/             # TypeScript definitions
│
├── backend/               # FastAPI Backend
│   ├── assistants/        # Specialized AI modules
│   ├── services/          # Business logic
│   │   ├── rewards.py     # Gamification engine
│   │   ├── tracker.py     # Progress tracking
│   │   ├── rag.py         # Knowledge retrieval
│   │   └── market_research.py
│   ├── main.py            # API endpoints
│   ├── database.py        # SQLAlchemy models
│   └── llm_service.py     # Groq AI integration
│
└── supabase/              # Database migrations
```

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.10+
- **PostgreSQL** (via Supabase or local)
- **Groq API Key** ([Get one here](https://console.groq.com))

### Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost:5432/edunovas
GROQ_API_KEY=your_groq_api_key_here
JWT_SECRET_KEY=your_secret_key_here
EOF

# Initialize database
python init_db.py

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
DATABASE_URL=postgresql://user:password@host:port/database
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
JWT_SECRET_KEY=your-secret-key
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=gemma3:latest
```

**Frontend**
- API endpoint configured in component files (default: `http://127.0.0.1:8000`)

---

## 📊 Database Schema

**Core Tables:**
- `users` - Authentication & roles
- `student_profiles` - Academic information
- `user_progress` - XP, levels, badges
- `chat_messages` - Conversation history
- `quiz_history` - Assessment results
- `interview_history` - Mock interview scores
- `coding_errors` - Mistake patterns
- `domain_stats` - Interaction tracking

---

## 🎨 Tech Stack

### Frontend
- **React 19** with TypeScript
- **React Router** for navigation
- **Vite** for blazing-fast builds
- **Custom CSS** with glassmorphism design

### Backend
- **FastAPI** - High-performance API framework
- **SQLAlchemy** - ORM with PostgreSQL
- **Groq AI** - LLM inference (Llama 3.3 70B)
- **FAISS** - Vector similarity search
- **PyTesseract** - OCR for resume parsing
- **DuckDuckGo Search** - Market research

### Infrastructure
- **Supabase** - PostgreSQL hosting
- **JWT** - Secure authentication
- **bcrypt** - Password hashing

---

## 🎯 API Endpoints

### Authentication
- `POST /signup` - User registration
- `POST /login` - User authentication

### Student
- `POST /chat` - AI conversation
- `POST /save-profile` - Update profile
- `GET /student/progress` - Fetch progress
- `GET /performance-stats` - Analytics

### Learning Modules
- `POST /upload-resume` - Resume OCR
- `POST /analyze-resume` - Deep analysis
- `GET /generate-quiz` - Create quiz
- `POST /submit-quiz` - Submit answers
- `POST /analyze-code` - Code review

### Admin
- `GET /admin/analytics` - Platform metrics

---

## 🎮 Gamification System

| Activity | XP Points |
|----------|-----------|
| Quiz Complete | 50 |
| Interview Complete | 100 |
| Code Analysis | 25 |
| Daily Streak | 10 |
| Profile Update | 20 |

**Level System:** Every 500 XP = 1 Level Up

---

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt (72-byte limit)
- Role-based access control (Student/Admin)
- Protected routes with authentication guards
- Environment variable isolation

---

## 📈 Performance

- **Frontend:** Vite HMR for instant updates
- **Backend:** FastAPI async support
- **Database:** Indexed queries with SQLAlchemy
- **AI:** Groq's optimized LLM inference
- **Caching:** RAG knowledge base in-memory

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

**Edunovas Team**
- Platform Architecture & Development
- AI Integration & Optimization

---

## 🙏 Acknowledgments

- **Groq** - Lightning-fast LLM inference
- **Supabase** - PostgreSQL hosting
- **React Team** - Amazing frontend framework
- **FastAPI** - Modern Python web framework

---

## 📞 Support

For issues and questions:
- 📧 Email: support@edunovas.ai
- 🐛 Issues: [GitHub Issues](https://github.com/vinaykr8807/Edunovas/issues)
- 📖 Docs: [Documentation](https://github.com/vinaykr8807/Edunovas/wiki)

---

<div align="center">

**Built with ❤️ by the Edunovas Team**

⭐ Star us on GitHub — it motivates us a lot!

</div>

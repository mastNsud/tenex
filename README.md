# Tenex Tutorials Assistant 🎓

An ultra-low-cost, high-performance platform for Class 10 students (Indian CBSE/ICSE), optimized for the Railway Hobby plan.

## 🚀 Architecture

- **Backend**: FastAPI (Python)
- **Database**: [Neon](https://neon.tech/) (Free PostgreSQL - 3GB)
- **Cache**: [Upstash](https://upstash.com/) (Free Redis - 10K commands/day)
- **AI**: [Groq](https://groq.com/) (Llama 3.1 - Free unlimited inference)
- **File Storage**: [Cloudflare R2](https://www.cloudflare.com/developer-platform/r2/) (10GB Free, No egress fees)
- **Email**: [Resend](https://resend.com/) (3K emails/month)
- **Monitoring**: [Better Stack](https://betterstack.com/) (Free logs & uptime)

## 🛠️ Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd tenex
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your API keys.
   ```bash
   cp .env.example .env
   ```

4. **Run locally**:
   ```bash
   uvicorn main:app --reload
   ```

## 🚆 Deployment on Railway

1. Install [Railway CLI](https://docs.railway.app/guides/cli).
2. Login and link project:
   ```bash
   railway login
   railway link
   ```
3. Deploy:
   ```bash
   railway up
   ```

## 🤖 Telegram Bot

The bot script is located in `bot.py`. In production, you can run it as a separate worker on Railway or integrate it into the FastAPI lifecycle.

## 📁 Project Structure

- `main.py`: FastAPI application & AI integration.
- `models.py`: SQLAlchemy database models.
- `bot.py`: Telegram bot implementation.
- `storage.py`: Cloudflare R2 storage utility.
- `railway.toml`: Deployment configuration.
- `requirements.txt`: Python package dependencies.

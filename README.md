# HackSignal - Hackathon Monitor

A full-stack application that monitors X (formerly Twitter) to surface AI and crypto-focused hackathons matching an "indie-friendly" profile.

## 🏗️ Monorepo Structure

This project is organized as a monorepo containing:

-   **`/backend`** - Python backend for X monitoring, scoring, and data processing
-   **`/frontend`** - Next.js + TypeScript + Tailwind CSS web interface

## 🚀 Quick Start

### Prerequisites

-   Node.js 18+ and npm
-   Python 3.8+
-   X (Twitter) API credentials (for backend monitoring)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd hacksignal
```

2. Install all dependencies:

```bash
# Install frontend dependencies
npm install

# Install backend dependencies
cd backend && pip install -r requirements.txt && cd ..
```

3. Set up environment variables:

```bash
# Backend environment variables
cd backend
cp .env.example .env
# Edit .env with your X API credentials

# Frontend environment variables (if needed)
cd ../frontend
cp .env.example .env.local
```

### Development

Run both frontend and backend in development mode:

```bash
npm run dev
```

Or run them separately:

```bash
# Backend only
npm run dev:backend

# Frontend only
npm run dev:frontend
```

## 🎯 Target Criteria

The system monitors for hackathons matching these criteria:

| Criterion               | Target Band                          |
| ----------------------- | ------------------------------------ |
| Promoter follower count | **2,000 – 50,000**                   |
| Prize pool              | **$2,160 – $27,000** (or equivalent) |
| Event duration          | **≤ 72 hours**                       |
| Team size implied       | Solo or small team (≤ 3)             |

## 📊 Architecture

### Backend (Python)

-   **Ingestion**: Monitors configured X sources for hackathon announcements
-   **Scoring**: Assigns relevance scores using weighted keyword analysis
-   **Enrichment**: Extracts prize amounts, duration, and calculates ROI
-   **Alerting**: Generates alerts for qualifying hackathons

### Frontend (Next.js)

-   **Dashboard**: Real-time view of discovered hackathons
-   **Filtering**: Search and filter by criteria
-   **Details**: Detailed view of each hackathon
-   **Settings**: Configure monitoring preferences

## 🧪 Testing

Run all tests:

```bash
npm test
```

Run specific tests:

```bash
# Backend tests
npm run test:backend

# Frontend tests
npm run test:frontend
```

## 📦 Deployment

### Backend Deployment

The Python backend can be deployed as a service. See [backend/README.md](backend/README.md) for details.

### Frontend Deployment

The Next.js frontend can be deployed to Vercel, Netlify, or any Node.js hosting:

```bash
npm run build:frontend
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

-   [Backend Documentation](backend/README.md)
-   [Backend Scoring Algorithm](backend/SCORING_README.md)
-   [Privacy & Compliance Policy](backend/Policy.md)
-   [Changelog](CHANGELOG.md)

---

**Disclaimer**: This tool monitors public social media posts for hackathon announcements. Users are responsible for verifying event details and terms before participating.

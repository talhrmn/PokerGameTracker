# Poker Game Tracker

A comprehensive poker game management and tracking application designed for serious poker players and organizers.

## Project Overview

Poker Game Tracker is an all-in-one solution for managing poker games, events, and player statistics. The application provides a complete toolkit for poker game organizers and players to manage their poker activities efficiently.

## Key Features

### Game Management

- Create and manage poker events with customizable settings
- Invite players and manage player lists
- Track buy-ins and cashouts in real-time
- Manage game rules and blinds structure

### Financial Tracking

- Detailed financial tracking for each game
- Automatic calculation of player profits/losses
- Export game data with financial distribution
- Track player contributions and payouts

### Statistics & Analytics

- Track player performance over time
- View trends in game results
- Detailed statistics for individual players
- Customizable reports and visualizations

### Social Features

- Invite and manage friends
- Track player history across multiple games
- Collaborative game management
- Share game results and statistics

## Tech Stack

### Frontend

- Next.js 15.2.0
- TypeScript
- React 18.3.1
- Ant Design (antd) for UI components
- React Query for state management

### Backend

- Python
- FastAPI
- MongoDB database
- Docker for containerization

## Project Structure

```
PokerGameTracker/
├── client/           # Next.js frontend application
├── server/           # FastAPI backend server
├── docker-compose.yml # Docker configuration
└── .env              # Environment configuration
```

## Getting Started

1. Clone the repository
2. Copy `.env.example` to `.env` and configure your environment variables
3. Install dependencies:

   ```bash
   # Install frontend dependencies
   cd client
   npm install

   # Install backend dependencies
   cd ../server
   pip install -r requirements.txt
   ```

4. Start the development servers:

   ```bash
   # Start backend server
   cd server
   uvicorn app.main:app --reload

   # In another terminal, start frontend
   cd client
   npm run dev
   ```

5. The application will be available at `http://localhost:3000`

## Development Notes

The application features custom implementations of many components and features, built from scratch for maximum flexibility and learning.

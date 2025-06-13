import { GameStats } from "@/features/dashboard/game/types/games.types";

export interface RecentGamesProps {
  recentGames: GameStats[];
  isLoading: boolean;
}

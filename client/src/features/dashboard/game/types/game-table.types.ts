import { GamePlayerProps } from "@/features/dashboard/game/types/games.types";

export interface GameTableProps {
  players: GamePlayerProps[];
  totalPot: number;
  onPlayerSelect: (player: GamePlayerProps) => void;
}

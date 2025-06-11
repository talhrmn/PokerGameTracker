import { GamePlayerProps } from "@/app/dashboard/games/types";

export interface PokerTableProps {
  players: GamePlayerProps[];
  totalPot: number;
  onPlayerSelect: (player: GamePlayerProps) => void;
}

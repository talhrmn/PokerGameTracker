import { GameStatusEnum } from "@/features/dashboard/game/types/games.types";

export interface GameHeaderProps {
  venue: string;
  date: Date | string;
  status: GameStatusEnum;
  totalPot: number;
  onBackClick: () => void;
}

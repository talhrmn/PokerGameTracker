import { GameStatusEnum } from "@/app/dashboard/games/types";

export interface GameHeaderProps {
  venue: string;
  date: Date | string;
  status: GameStatusEnum;
  totalPot: number;
  onBackClick: () => void;
}

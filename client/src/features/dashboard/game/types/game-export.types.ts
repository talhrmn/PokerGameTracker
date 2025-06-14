import { GameProps } from "@/features/dashboard/game/types/games.types";

export interface GameModelProps {
  game: GameProps;
  isOpen: boolean;
  onClose: () => void;
}

export interface OptimizedPayment {
  from: string;
  to: string;
  amount: number;
}

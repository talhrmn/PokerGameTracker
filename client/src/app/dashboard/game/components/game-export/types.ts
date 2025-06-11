import { GameProps } from "@/app/dashboard/games/types";

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

import { GamePlayerProps, GameProps } from "@/features/dashboard/game/types/games.types";

export interface PlayerDetailsProps {
  player: GamePlayerProps;
  game: GameProps;
  gameId: string;
  onClose: () => void;
}

export interface PlayerChangeProps {
  amount: number;
  time: Date;
}

export interface BuyInProps {
  gameId: string;
  buyIn: PlayerChangeProps;
}

export interface CashOutProps {
  gameId: string;
  cashOut: PlayerChangeProps;
}

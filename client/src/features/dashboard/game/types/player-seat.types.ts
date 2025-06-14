import { GamePlayerProps } from "@/features/dashboard/game/types/games.types";

export interface Position {
  top: string;
  left: string;
}

export interface PlayerSeatProps {
  player: GamePlayerProps;
  isTableLeader: boolean;
  position: Position;
  onClick: () => void;
}

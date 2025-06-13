import { GameProps, GameStatusEnum } from "@/features/dashboard/game/types/games.types";

export interface GameControlsProps {
  game: GameProps;
  gameId: string;
  isCreator: boolean;
  gameStatus: GameStatusEnum;
}

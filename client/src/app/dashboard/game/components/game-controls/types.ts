import { GameProps, GameStatusEnum } from "@/app/dashboard/games/types";

export interface GameControlsProps {
  game: GameProps;
  gameId: string;
  isCreator: boolean;
  gameStatus: GameStatusEnum;
}

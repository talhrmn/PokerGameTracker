import { GameProps, NotableHandProps } from "@/features/dashboard/game/types/games.types";

export interface GameDetailsProps {
  game: GameProps;
  onClose: () => void;
}

export interface NotableHandsDetailProps extends NotableHandProps {
  username: string;
}

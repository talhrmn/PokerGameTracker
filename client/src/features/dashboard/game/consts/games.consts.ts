import { ColumnDefinition } from "@/features/common/types";
import { GameProps } from "@/features/dashboard/game/types/games.types";
import {
  CircleDollarSign,
  // Ellipsis,
  Users,
} from "lucide-react";

export const GAME_COLUMNS: ColumnDefinition<GameProps>[] = [
  {
    key: "date",
    header: "Date",
    render: (game: GameProps) =>
      new Date(game.date).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "2-digit",
      }),
  },
  {
    key: "venue",
    header: "Venue",
  },
  {
    key: "players",
    header: "Players",
    icon: Users,
    render: (game: GameProps) => game.players.length.toString(),
  },
  {
    key: "total_pot",
    header: "Pot Size",
    icon: CircleDollarSign,
  },
  {
    key: "status",
    header: "Status",
    render: (game: GameProps) => game.status.replace("_", " ").toUpperCase(),
    // icon: Ellipsis,
  },
];

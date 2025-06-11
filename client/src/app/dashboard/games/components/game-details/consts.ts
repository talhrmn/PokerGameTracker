import { ColumnDefinition } from "@/app/dashboard/components/generic-table/types";
import { NotableHandsDetailProps } from "@/app/dashboard/games/components/game-details/types";
import { GamePlayerProps } from "@/app/dashboard/games/types";

export const PLAYER_COLUMNS: ColumnDefinition<GamePlayerProps>[] = [
  {
    key: "username",
    header: "Username",
  },
  {
    key: "buy_ins",
    header: "Total Buy Ins",
    render: (player) =>
      player.buy_ins.reduce((sum, buyin) => sum + buyin.amount, 0),
  },
  {
    key: "cash_out",
    header: "Total Cash Out",
  },
  {
    key: "net_profit",
    header: "Net Profit",
  },
];

export const HANDS_COLUMNS: ColumnDefinition<NotableHandsDetailProps>[] = [
  {
    key: "username",
    header: "Username",
  },
  {
    key: "description",
    header: "Description",
  },
  {
    key: "amount_won",
    header: "Amount Won",
  },
];

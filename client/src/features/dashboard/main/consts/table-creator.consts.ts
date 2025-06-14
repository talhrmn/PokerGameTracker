import { TableGameFormProps } from "@/features/common/types";

export const DEFAULT_FORM_STATE = {
  name: "",
  venue: "",
  scheduled_date: "",
  scheduled_time: "",
  minimum_buy_in: 50,
  maximum_players: 10,
  game_type: "Texas Hold'em",
  blind_structure: "1/2",
  description: "",
} as TableGameFormProps;

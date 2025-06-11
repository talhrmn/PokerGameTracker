export interface TableForm {
  name: string;
  venue: string;
  scheduled_date: string;
  scheduled_time: string;
  minimum_buy_in: number;
  maximum_players: number;
  game_type: "Texas Hold'em";
  blind_structure: "1/2";
  description: string;
  date?: string;
}

export interface PokerTableFormProps {
  formTitle: string;
  initialData: TableForm;
  handleFormSubmit: (params: TableForm) => void;
  onClose: () => void;
  formActions: JSX.Element;
  editDisabled: boolean;
}

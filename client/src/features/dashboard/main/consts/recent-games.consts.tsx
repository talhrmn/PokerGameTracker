import { ColumnDefinition } from "@/features/common/types";
import { GameStats } from "@/features/dashboard/game/types/games.types";
import styles from "@/features/dashboard/main/components/recent-games/styles.module.css";
import { Clock, Users } from "lucide-react";

export const GAME_COLUMNS: ColumnDefinition<GameStats>[] = [
	{
		key: "date",
		header: "Date",
	},
	{
		key: "venue",
		header: "Venue",
	},
	{
		key: "players",
		header: "Players",
		icon: Users,
	},
	{
		key: "duration",
		header: "Duration",
		icon: Clock,
		// hidden: true,
	},
	{
		key: "profit",
		header: "Profit/Loss",
		// align: "right",
		render: (game: GameStats) => (
			<span
				className={
					game.profit_loss >= 0 ? styles.profitPositive : styles.profitNegative
				}
			>
				$
				{game.profit_loss >= 0
					? game.profit_loss
					: Math.abs(game.profit_loss) * -1}
			</span>
		),
	},
];

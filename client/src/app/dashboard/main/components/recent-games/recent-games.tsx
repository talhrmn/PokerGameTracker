import GenericTable from "@/app/dashboard/components/generic-table/generic-table";
import { GAME_COLUMNS } from "@/app/dashboard/main/components/recent-games/consts";
import { RecentGamesProps } from "@/app/dashboard/main/components/recent-games/types";

export default function RecentGames({ recentGames }: RecentGamesProps) {
	return (
		<GenericTable
			data={recentGames}
			columns={GAME_COLUMNS}
			title="Recent Games"
			viewAllLink="/games"
			titleBarColor="#f56565"
		/>
	);
}

import GenericTable from "@/features/common/components/generic-table/generic-table";
import LoadingSpinner from "@/features/common/components/loading-spinner/loading-spinner";
import { GAME_COLUMNS } from "../../consts/recent-games.consts";
import { RecentGamesProps } from "../../types/recent-games.types";

export default function RecentGames({
	recentGames,
	isLoading,
}: RecentGamesProps) {
	if (isLoading) {
		return <LoadingSpinner message="Loading games data..." />;
	}

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

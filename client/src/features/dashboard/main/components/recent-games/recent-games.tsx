import GenericTable from "@/features/common/components/generic-table/generic-table";
import commonStyles from "@/features/common/styles.module.css";
import { GAME_COLUMNS } from "../../consts/recent-games.consts";
import { RecentGamesProps } from "../../types/recent-games.types";

export default function RecentGames({
	recentGames,
	isLoading,
}: RecentGamesProps) {
	if (isLoading) {
		return (
			<div className={commonStyles.loadingContainer}>
				<div className={commonStyles.loadingSpinner}></div>
				<p>Loading game data...</p>
			</div>
		);
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

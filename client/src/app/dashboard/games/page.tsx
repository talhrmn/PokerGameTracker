"use client";

import GenericTable from "@/features/common/components/generic-table/generic-table";
import GameDetailsModal from "@/features/dashboard/game/components/game-details/game-details";
import { GAME_COLUMNS } from "@/features/dashboard/game/consts/games.consts";
import {
	useFetchGamesQuery,
	useTotalGamesCountQuery,
} from "@/features/dashboard/game/hooks/game.queries";
import { GameProps } from "@/features/dashboard/game/types/games.types";
import { useMemo, useState } from "react";

const Games = () => {
	const [currentPage, setCurrentPage] = useState(1);
	const [selectedGame, setSelectedGame] = useState<GameProps | null>(null);
	const gamesPerPage = 10;

	const skip = useMemo(
		() => (currentPage - 1) * gamesPerPage,
		[currentPage, gamesPerPage]
	);

	const {
		data: totalGameCount,
		// isLoading: countLoading,
		isError: countError,
	} = useTotalGamesCountQuery();

	if (countError) console.error("Failed to fetch games count");

	const {
		data: games = [] as GameProps[],
		// isLoading: gamesLoading,
		isError: gamesError,
	} = useFetchGamesQuery(gamesPerPage, skip);

	if (gamesError) console.error("Failed to fetch games");

	const handlePageChange = (newPage: number) => {
		setCurrentPage(newPage);
	};

	const handleRowClick = (game: GameProps) => {
		setSelectedGame(game);
	};

	const handleCloseModal = () => {
		setSelectedGame(null);
	};

	const totalPages = totalGameCount
		? Math.ceil(totalGameCount / gamesPerPage)
		: 1;

	return (
		<>
			<GenericTable
				data={games}
				columns={GAME_COLUMNS}
				title="Games"
				viewAllLink="/games"
				titleBarColor="#f56565"
				onRowClick={handleRowClick}
				pagination={{
					currentPage,
					totalPages,
					totalItems: totalGameCount || 1,
					itemsPerPage: gamesPerPage,
				}}
				onPageChange={handlePageChange}
			/>

			{selectedGame && (
				<GameDetailsModal game={selectedGame} onClose={handleCloseModal} />
			)}
		</>
	);
};

export default Games;

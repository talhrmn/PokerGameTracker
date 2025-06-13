"use client";

import GenericTable from "@/app/dashboard/components/generic-table/generic-table";
import GameDetailsModal from "@/app/dashboard/games/components/game-details/game-details";
import { GAME_COLUMNS } from "@/app/dashboard/games/consts";
import {
	useFetchGamesQuery,
	useTotalGamesCountQuery,
} from "@/app/dashboard/games/games-queries";
import { GameProps } from "@/app/dashboard/games/types";
import { useMemo, useState } from "react";

export default function Games() {
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
}

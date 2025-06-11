"use client";

import { useAuth } from "@/app/auth/context/context";
import GameControls from "@/app/dashboard/game/components/game-controls/game-controls";
import GameHeader from "@/app/dashboard/game/components/game-header/game-header";
import PokerTable from "@/app/dashboard/game/components/game-table/game-table";
import PlayerDetails from "@/app/dashboard/game/components/player-details/player-details";
import { useGameEvents, useGameQuery } from "@/app/dashboard/game/game-queries";
import styles from "@/app/dashboard/game/styles.module.css";
import { GamePlayerProps } from "@/app/dashboard/games/types";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

export default function PokerGamePage() {
	const { user } = useAuth();
	const router = useRouter();
	const params = useParams();

	const [selectedPlayer, setSelectedPlayer] = useState<GamePlayerProps | null>(
		null
	);

	const gameId = params.id as string;

	const {
		data: game,
		isLoading,
		isError,
		error: queryError,
	} = useGameQuery(gameId);

	const handleGameUpdate = () => {};

	useGameEvents(gameId, handleGameUpdate);

	const isCreator = user._id === game?.creator_id;

	const handlePlayerSelect = (player: GamePlayerProps) => {
		setSelectedPlayer(player);
	};

	const handlePlayerClose = () => {
		setSelectedPlayer(null);
	};

	const handleBackToTables = () => {
		router.push("/dashboard/tables");
	};

	if (isLoading) {
		return (
			<div className={styles.loadingContainer}>
				<div className={styles.loadingSpinner}></div>
				<p>Loading game data...</p>
			</div>
		);
	}

	if (isError || !game) {
		return (
			<div className={styles.errorContainer}>
				<h2>Error</h2>
				<p>{queryError?.message || "Game not found"}</p>
				<button className={styles.button} onClick={handleBackToTables}>
					Back to Tables
				</button>
			</div>
		);
	}

	return (
		<div className={styles.container}>
			<GameHeader
				venue={game.venue}
				date={game.date}
				status={game.status}
				totalPot={game.total_pot}
				onBackClick={handleBackToTables}
			/>

			<div className={styles.gameContainer}>
				<PokerTable
					players={game.players}
					totalPot={game.total_pot}
					onPlayerSelect={handlePlayerSelect}
				/>

				<GameControls
					game={game}
					gameId={params.id as string}
					isCreator={isCreator}
					gameStatus={game.status}
				/>
			</div>

			{selectedPlayer && (
				<PlayerDetails
					game={game}
					gameId={params.id as string}
					player={selectedPlayer}
					onClose={handlePlayerClose}
				/>
			)}
		</div>
	);
}

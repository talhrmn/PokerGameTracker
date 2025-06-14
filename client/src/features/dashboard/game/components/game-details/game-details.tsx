import GenericTable from "@/features/common/components/generic-table/generic-table";
import {
	HANDS_COLUMNS,
	PLAYER_COLUMNS,
} from "@/features/dashboard/game/consts/game-detail.consts";
import {
	GameDetailsProps,
	NotableHandsDetailProps,
} from "@/features/dashboard/game/types/game-details.types";
import { useGameTableQuery } from "@/features/dashboard/table/hooks/table.queries";
import {
	Calendar,
	Clock,
	DollarSign,
	LogIn,
	MapPin,
	PlayCircle,
	Tag,
	Type,
	X,
} from "lucide-react";
import { useRouter } from "next/navigation";
import React from "react";
import styles from "./styles.module.css";
import { ActionButton } from "@/features/common/components/action-button/action-button";

const GameDetailsModal: React.FC<GameDetailsProps> = ({
	game,
	onClose,
}: GameDetailsProps) => {
	const router = useRouter();

	const {
		data: table,
		isLoading: loading,
		isError: error,
	} = useGameTableQuery(game.table_id);

	const gameInProgress = game.status === "in_progress";

	const handleGoToGame = () => {
		router.push(`/dashboard/game/${table?.game_id}`);
	};

	const goToGameBtn = (
		<ActionButton
			action={{
				id: "goToGame",
				type: "button",
				label: "Enter Game",
				icon: LogIn,
				variant: "success",
				onClick: handleGoToGame,
			}}
		/>
	);

	const formatDate = (dateString: string) => {
		if (!dateString) return "N/A";
		try {
			const date = new Date(dateString);
			return date.toLocaleString();
		} catch {
			return dateString;
		}
	};

	const formatDuration = (hours: number, minutes: number) => {
		if (hours === 0 && minutes === 0) return "Not specified";
		return `${hours}h ${minutes}m`;
	};

	const notableHandsData = game.players
		.reduce((acc, player) => {
			const playerHands = player.notable_hands.map((hand) => ({
				username: player.username,
				description: hand.description,
				amount_won: hand.amount_won,
			}));

			return acc.concat(playerHands);
		}, [] as NotableHandsDetailProps[])
		.sort((handA, handB) => handB.amount_won - handA.amount_won);

	return (
		<div className={styles.modalOverlay} onClick={onClose}>
			<div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
				<button
					className={styles.closeButton}
					onClick={onClose}
					aria-label="Close"
				>
					<X size={20} />
				</button>

				<h3 className={styles.formTitle}>
					<PlayCircle className={styles.titleIcon} size={24} />
					Game Details Summary
				</h3>

				{loading ? (
					<div className={styles.loadingContainer}>
						<div className={styles.spinner}></div>
						<p>Loading game details...</p>
					</div>
				) : error ? (
					<div className={styles.errorMessage}>{error}</div>
				) : (
					<div className={styles.detailsContainer}>
						{/* Main game info card */}
						<div className={styles.detailsCard}>
							<div className={styles.cardHeader}>
								<h4>{table?.name || "Game Table"}</h4>
								<div
									className={styles.statusBadge}
									data-status={game?.status?.toLowerCase()}
								>
									{game?.status || "Unknown Status"}
								</div>
							</div>

							<div className={styles.detailsGrid}>
								<div className={styles.detailItem}>
									<div className={styles.detailIcon}>
										<MapPin size={16} />
									</div>
									<div>
										<span className={styles.detailLabel}>Venue</span>
										<span className={styles.detailValue}>
											{game?.venue || "N/A"}
										</span>
									</div>
								</div>

								<div className={styles.detailItem}>
									<div className={styles.detailIcon}>
										<Calendar size={16} />
									</div>
									<div>
										<span className={styles.detailLabel}>Date</span>
										<span className={styles.detailValue}>
											{formatDate(table?.date || "")}
										</span>
									</div>
								</div>

								<div className={styles.detailItem}>
									<div className={styles.detailIcon}>
										<Type size={16} />
									</div>
									<div>
										<span className={styles.detailLabel}>Game Type</span>
										<span className={styles.detailValue}>
											{table?.game_type || "N/A"}
										</span>
									</div>
								</div>

								<div className={styles.detailItem}>
									<div className={styles.detailIcon}>
										<Tag size={16} />
									</div>
									<div>
										<span className={styles.detailLabel}>Blind Structure</span>
										<span className={styles.detailValue}>
											{table?.blind_structure || "N/A"}
										</span>
									</div>
								</div>

								<div className={styles.detailItem}>
									<div className={styles.detailIcon}>
										<Clock size={16} />
									</div>
									<div>
										<span className={styles.detailLabel}>Duration</span>
										<span className={styles.detailValue}>
											{formatDuration(
												game.duration.hours,
												game.duration.minutes
											)}
										</span>
									</div>
								</div>

								<div className={styles.detailItem}>
									<div className={styles.detailIcon}>
										<DollarSign size={16} />
									</div>
									<div>
										<span className={styles.detailLabel}>Total Pot Size</span>
										<span className={styles.detailValue}>
											${game.total_pot}
										</span>
									</div>
								</div>
							</div>

							{table?.description && (
								<div className={styles.descriptionBox}>
									<span className={styles.detailLabel}>Description</span>
									<p className={styles.description}>{table.description}</p>
								</div>
							)}
						</div>

						<GenericTable
							data={game.players.sort(
								(playerA, playerB) => playerB.net_profit - playerA.net_profit
							)}
							columns={PLAYER_COLUMNS}
							title="Player Data"
							titleBarColor="#f56565"
						/>

						<GenericTable
							data={notableHandsData}
							columns={HANDS_COLUMNS}
							title="Notable Hands"
							titleBarColor="#f56565"
						/>
					</div>
				)}

				{gameInProgress && (
					<div className={styles.formActions}>{goToGameBtn}</div>
				)}
			</div>
		</div>
	);
};

export default GameDetailsModal;

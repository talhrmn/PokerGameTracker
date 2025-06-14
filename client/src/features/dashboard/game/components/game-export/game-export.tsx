import {
	GameModelProps,
	OptimizedPayment,
} from "@/features/dashboard/game/types/game-export.types";
import { GamePlayerProps } from "@/features/dashboard/game/types/games.types";
import { ArrowRight, Award, Clock, DollarSign, MapPin, X } from "lucide-react";
import { useCallback, useMemo } from "react";
import styles from "./styles.module.css";

export const GameExport = ({ game, isOpen, onClose }: GameModelProps) => {
	const winner = game.players.sort(
		(playerA, playerB) => playerB.net_profit - playerA.net_profit
	)[0];

	const calculatePayments = useCallback(
		(players: GamePlayerProps[]): OptimizedPayment[] => {
			const simplifiedPlayers = players.map((player) => ({
				username: player.username,
				net_profit: player.net_profit,
			}));

			const debtors = simplifiedPlayers
				.filter((player) => player.net_profit < 0)
				.map((player) => ({
					...player,
					net_profit: Math.abs(player.net_profit),
				}))
				.sort((a, b) => b.net_profit - a.net_profit);

			const creditors = simplifiedPlayers
				.filter((player) => player.net_profit > 0)
				.sort((a, b) => b.net_profit - a.net_profit);

			const payments: OptimizedPayment[] = [];

			let creditorIndex = 0;

			for (const debtor of debtors) {
				let debtRemaining = debtor.net_profit;

				while (debtRemaining > 0 && creditorIndex < creditors.length) {
					const creditor = creditors[creditorIndex];
					const amountToTransfer = Math.min(debtRemaining, creditor.net_profit);

					if (amountToTransfer > 0) {
						payments.push({
							from: debtor.username,
							to: creditor.username,
							amount: amountToTransfer,
						});

						debtRemaining -= amountToTransfer;
						creditor.net_profit -= amountToTransfer;
					}

					if (creditor.net_profit <= 0) {
						creditorIndex++;
					}
				}
			}

			return payments;
		},
		[]
	);

	const optimizedPayments = calculatePayments(game.players);

	const formatDuration = useMemo(() => {
		if (game.duration.hours === 0) {
			return `${game.duration.minutes}m`;
		}
		return `${game.duration.hours}h ${game.duration.minutes}m`;
	}, [game]);

	const handleOverlayClick = (e: React.MouseEvent) => {
		if (e.target === e.currentTarget) {
			onClose();
		}
	};

	return (
		<>
			<div
				className={`${styles.overlay} ${isOpen ? styles.overlayVisible : ""}`}
				onClick={handleOverlayClick}
			>
				<div
					className={`${styles.container} ${isOpen && styles.containerOpen}`}
				>
					<div className={styles.topHeader}>
						<div className={styles.status}>COMPLETED</div>
						<button className={styles.closeButton} onClick={onClose}>
							<X size={20} />
						</button>
					</div>
					<div className={styles.header}>
						<h2 className={styles.title}>Game Summary</h2>
					</div>

					<div className={styles.infoGrid}>
						<div className={styles.infoItem}>
							<div className={styles.infoIcon}>
								<MapPin size={20} />
							</div>
							<div className={styles.infoContent}>
								<div className={styles.infoLabel}>Venue</div>
								<div className={styles.infoValue}>{game.venue}</div>
							</div>
						</div>

						<div className={styles.infoItem}>
							<div className={styles.infoIcon}>
								<Clock size={20} />
							</div>
							<div className={styles.infoContent}>
								<div className={styles.infoLabel}>Date</div>
								<div className={styles.infoValue}>
									{new Date(game.date).toLocaleDateString("en-US", {
										year: "numeric",
										month: "short",
										day: "2-digit",
									})}
								</div>
							</div>
						</div>

						<div className={styles.infoItem}>
							<div className={styles.infoIcon}>
								<Clock size={20} />
							</div>
							<div className={styles.infoContent}>
								<div className={styles.infoLabel}>Duration</div>
								<div className={styles.infoValue}>{formatDuration}</div>
							</div>
						</div>

						<div className={styles.infoItem}>
							<div className={styles.infoIcon}>
								<DollarSign size={20} />
							</div>
							<div className={styles.infoContent}>
								<div className={styles.infoLabel}>Total Pot Size</div>
								<div className={styles.infoValue}>${game.total_pot}</div>
							</div>
						</div>
					</div>

					{winner && (
						<div className={styles.winnerSection}>
							<div className={styles.winnerHeader}>
								<Award size={20} />
								<h3>Winner</h3>
							</div>
							<div className={styles.winnerCard}>
								<div className={styles.winnerName}>{winner.username}</div>
								<div className={styles.winnerProfit}>+${winner.net_profit}</div>
							</div>
						</div>
					)}

					<div className={styles.paymentSection}>
						<h3 className={styles.paymentTitle}>Payment Plan</h3>
						<p className={styles.paymentDescription}>
							Settle debts between players:
						</p>

						{optimizedPayments.length === 0 ? (
							<div className={styles.noPayments}>All players are settled!</div>
						) : (
							<ul className={styles.paymentList}>
								{optimizedPayments.map((payment, index) => (
									<li key={index} className={styles.paymentItem}>
										<div className={styles.paymentFrom}>{payment.from}</div>
										<div className={styles.paymentArrow}>
											<ArrowRight size={16} />
										</div>
										<div className={styles.paymentTo}>{payment.to}</div>
										<div className={styles.paymentAmount}>
											${payment.amount}
										</div>
									</li>
								))}
							</ul>
						)}
					</div>
				</div>
			</div>
		</>
	);
};

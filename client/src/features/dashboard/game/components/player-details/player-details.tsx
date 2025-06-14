import { useAuth } from "@/features/auth/contexts/context";
import {
	useAddPlayerBuyIn,
	usePlayerCashOut,
} from "@/features/dashboard/game/hooks/game.queries";
import { BuyInsProps } from "@/features/dashboard/game/types/games.types";
import { PlayerDetailsProps } from "@/features/dashboard/game/types/player-details.types";
import { useState } from "react";
import styles from "./styles.module.css";

const PlayerDetails: React.FC<PlayerDetailsProps> = ({
	player,
	game,
	gameId,
	onClose,
}) => {
	const [activeTab, setActiveTab] = useState<"overview" | "buyins" | "hands">(
		"overview"
	);
	const { user } = useAuth();
	const isPlayer = player.user_id === user._id;

	const [playerBuyIns, setPlayerBuyIns] = useState<BuyInsProps[]>(
		player.buy_ins
	);

	const totalBuyIn = playerBuyIns.reduce((sum, buyIn) => sum + buyIn.amount, 0);
	const [newBuyIn, setNewBuyIn] = useState<number>(0);
	const [newCashOut, setNewCashOut] = useState<number>(
		totalBuyIn + player.net_profit
	);
	const [newHandDesc, setNewHandDesc] = useState<string>("");
	const [newHandAmount, setNewHandAmount] = useState<number>(0);
	const [loading, setLoading] = useState<boolean>(false);

	const addPlayerBuyInMutation = useAddPlayerBuyIn();
	const playerCashOutMutation = usePlayerCashOut();

	const handleAddBuyIn = async () => {
		if (newBuyIn <= 0) return;
		setLoading(true);
		try {
			const buyIn = {
				amount: newBuyIn,
				time: new Date(),
			};
			addPlayerBuyInMutation.mutate({ gameId, buyIn });
			setPlayerBuyIns([...playerBuyIns, buyIn]);
			setNewBuyIn(0);
		} catch {
			alert("Failed To Updated Buy In");
		} finally {
			setLoading(false);
		}
	};

	const handleCashOut = async () => {
		if (newCashOut <= 0 || newCashOut > game.available_cash_out) return;
		setLoading(true);
		const cashOut = {
			amount: newCashOut,
			time: new Date(),
		};
		playerCashOutMutation.mutate({ gameId, cashOut });
		setLoading(false);
	};

	// const handleAddNotableHand = async () => {
	//   if (!newHandDesc || newHandAmount === 0) return;

	//   try {
	//     setLoading(true);
	//     const newHand = {
	//       hand_id: `hand_${Date.now()}`,
	//       description: newHandDesc,
	//       amount_won: newHandAmount,
	//     };

	//     const updatedPlayer = {
	//       ...player,
	//       notable_hands: [...player.notable_hands, newHand],
	//     };

	//     const result = await updatePlayerData(gameId, updatedPlayer);
	//     onPlayerUpdate(result.players);
	//     setNewHandDesc("");
	//     setNewHandAmount(0);
	//   } catch (err) {
	//     console.error("Failed to add notable hand:", err);
	//   } finally {
	//     setLoading(false);
	//   }
	// };

	return (
		<div className={styles.overlay}>
			<div className={styles.modal}>
				<div className={styles.header}>
					<h2>{player.username}</h2>
					<button className={styles.closeButton} onClick={onClose}>
						✕
					</button>
				</div>

				<div className={styles.tabs}>
					<button
						className={`${styles.tab} ${
							activeTab === "overview" ? styles.activeTab : ""
						}`}
						onClick={() => setActiveTab("overview")}
					>
						Overview
					</button>
					<button
						className={`${styles.tab} ${
							activeTab === "buyins" ? styles.activeTab : ""
						}`}
						onClick={() => setActiveTab("buyins")}
					>
						Buy-ins
					</button>
					<button
						className={`${styles.tab} ${
							activeTab === "hands" ? styles.activeTab : ""
						}`}
						onClick={() => setActiveTab("hands")}
					>
						Notable Hands
					</button>
				</div>

				<div className={styles.content}>
					{activeTab === "overview" && (
						<div className={styles.overview}>
							<div className={styles.stat}>
								<span>Total Buy-in:</span>
								<span>${totalBuyIn.toLocaleString()}</span>
							</div>
							<div className={styles.stat}>
								<span>Cash Out:</span>
								<span>${newCashOut.toLocaleString()}</span>
							</div>
							<div className={styles.stat}>
								<span>Net Profit:</span>
								<span
									className={
										player.net_profit >= 0 ? styles.profit : styles.loss
									}
								>
									{player.net_profit >= 0 ? "+" : ""}$
									{player.net_profit.toLocaleString()}
								</span>
							</div>
							<div className={styles.stat}>
								<span>Notable Hands:</span>
								<span>{player.notable_hands.length}</span>
							</div>

							<div className={styles.cashOutContainer}>
								<div className={styles.inputGroup}>
									<label>Cash Out Amount</label>
									<div className={styles.inputWithPrefix}>
										<span>$</span>
										<input
											type="number"
											value={newCashOut}
											onChange={(e) => {
												setNewCashOut(Number(e.target.value));
											}}
											disabled={!isPlayer}
										/>
									</div>
								</div>
								<button
									className={styles.button}
									onClick={handleCashOut}
									disabled={!isPlayer || loading}
								>
									{loading ? "Saving..." : "Update Cash Out"}
								</button>
							</div>
						</div>
					)}

					{activeTab === "buyins" && (
						<div className={styles.buyins}>
							<div className={styles.listContainer}>
								{playerBuyIns.length === 0 ? (
									<p className={styles.emptyState}>No buy-ins recorded</p>
								) : (
									<ul className={styles.list}>
										{playerBuyIns.map((buyIn, index) => (
											<li key={index} className={styles.listItem}>
												<div className={styles.buyInAmount}>
													${buyIn.amount.toLocaleString()}
												</div>
												<div className={styles.buyInTime}>
													{new Date(buyIn.time).toLocaleString()}
												</div>
											</li>
										))}
									</ul>
								)}
							</div>

							<div className={styles.addBuyInContainer}>
								<div className={styles.inputGroup}>
									<label>Add Buy-in</label>
									<div className={styles.inputWithPrefix}>
										<span>$</span>
										<input
											type="number"
											value={newBuyIn || ""}
											onChange={(e) => setNewBuyIn(Number(e.target.value))}
											placeholder="Amount"
											disabled={!isPlayer}
										/>
									</div>
								</div>
								<button
									className={styles.button}
									onClick={handleAddBuyIn}
									disabled={!isPlayer || newBuyIn <= 0 || loading}
								>
									{loading ? "Adding..." : "Add Buy-in"}
								</button>
							</div>
						</div>
					)}

					{activeTab === "hands" && (
						<div className={styles.hands}>
							<div className={styles.listContainer}>
								{player.notable_hands.length === 0 ? (
									<p className={styles.emptyState}>No notable hands recorded</p>
								) : (
									<ul className={styles.list}>
										{player.notable_hands.map((hand) => (
											<li key={hand.hand_id} className={styles.handItem}>
												<div className={styles.handDescription}>
													{hand.description}
												</div>
												<div
													className={styles.handAmount}
													style={{
														color: hand.amount_won >= 0 ? "#32CD32" : "#FF4136",
													}}
												>
													{hand.amount_won >= 0 ? "+" : ""}$
													{hand.amount_won.toLocaleString()}
												</div>
											</li>
										))}
									</ul>
								)}
							</div>

							<div className={styles.addHandContainer}>
								<div className={styles.inputGroup}>
									<label>Hand Description</label>
									<input
										type="text"
										value={newHandDesc}
										onChange={(e) => setNewHandDesc(e.target.value)}
										placeholder="e.g., Pocket aces vs pocket kings"
										disabled={!isPlayer}
									/>
								</div>
								<div className={styles.inputGroup}>
									<label>Amount Won/Lost</label>
									<div className={styles.inputWithPrefix}>
										<span>$</span>
										<input
											type="number"
											value={newHandAmount || ""}
											onChange={(e) => setNewHandAmount(Number(e.target.value))}
											placeholder="Amount (negative for losses)"
											disabled={!isPlayer}
										/>
									</div>
								</div>
								<button
									className={styles.button}
									// onClick={handleAddNotableHand}
									disabled={
										!isPlayer || !newHandDesc || newHandAmount === 0 || loading
									}
								>
									{loading ? "Adding..." : "Add Hand"}
								</button>
							</div>
						</div>
					)}
				</div>
			</div>
		</div>
	);
};

export default PlayerDetails;

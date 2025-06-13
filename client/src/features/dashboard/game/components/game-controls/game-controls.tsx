import { GameExport } from "@/features/dashboard/game/components/game-export/game-export";
import { useGameCompletion } from "@/features/dashboard/game/hooks/game.queries";
import { GameControlsProps } from "@/features/dashboard/game/types/game-control.types";
import { CircleCheckBig } from "lucide-react";
import { useState } from "react";
import styles from "./styles.module.css";

const GameControls: React.FC<GameControlsProps> = ({
	game,
	gameId,
	isCreator,
	gameStatus,
}) => {
	const [exportModalOpen, setExportModalOpen] = useState<boolean>(false);
	const [loading, setLoading] = useState<boolean>(false);

	const gameCompletionMutation = useGameCompletion();

	const handleCompleteGame = async () => {
		setLoading(true);
		gameCompletionMutation.mutate(gameId);
		setLoading(false);
	};

	const handleExport = () => {
		setExportModalOpen(true);
	};

	const onCloseExport = () => {
		setExportModalOpen(false);
	};

	return (
		<div className={styles.controlsContainer}>
			{isCreator && (
				<div className={styles.statusControls}>
					<button
						className={`${styles.statusButton} ${
							gameStatus === "completed" ? styles.activeStatus : ""
						}`}
						onClick={handleCompleteGame}
						disabled={!isCreator || loading || gameStatus === "completed"}
					>
						<CircleCheckBig size={24} style={{ marginRight: "0.5rem" }} />
						Complete Game
					</button>
				</div>
			)}

			<div className={styles.actionButtons}>
				<button
					className={styles.actionButton}
					onClick={handleExport}
					disabled={gameStatus !== "completed"}
				>
					Export Results
				</button>
			</div>
			{/* {exportModalOpen && <GameExport game={game} onClose={onCloseExport} />} */}
			<GameExport
				game={game}
				isOpen={exportModalOpen}
				onClose={onCloseExport}
			/>
		</div>
	);
};

export default GameControls;

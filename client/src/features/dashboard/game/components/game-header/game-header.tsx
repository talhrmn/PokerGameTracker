import { statusHeadeParams } from "@/features/dashboard/game/consts/game-header.consts";
import { GameHeaderProps } from "@/features/dashboard/game/types/game-header.types";
import { GameStatusEnum } from "@/features/dashboard/game/types/games.types";
import styles from "./styles.module.css";

const GameHeader: React.FC<GameHeaderProps> = ({
	venue,
	date,
	status,
	totalPot,
	onBackClick,
}) => {
	const formattedDate = new Date(date).toLocaleString();

	return (
		<header className={styles.header}>
			<div className={styles.headerContent}>
				<button className={styles.backButton} onClick={onBackClick}>
					← Back to Tables
				</button>

				<div className={styles.gameInfo}>
					<h1 className={styles.title}>{venue}</h1>
					<div className={styles.meta}>
						<span className={styles.date}>{formattedDate}</span>
						<span
							className={styles.status}
							style={{
								backgroundColor:
									statusHeadeParams[status as GameStatusEnum].color,
							}}
						>
							{statusHeadeParams[status as GameStatusEnum].title}
						</span>
						<span className={styles.totalPot}>
							Total Pot: ${totalPot.toLocaleString()}
						</span>
					</div>
				</div>
			</div>
		</header>
	);
};

export default GameHeader;

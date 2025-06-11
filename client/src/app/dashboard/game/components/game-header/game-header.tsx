import { statusHeadeParams } from "@/app/dashboard/game/components/game-header/consts";
import styles from "@/app/dashboard/game/components/game-header/styles.module.css";
import { GameHeaderProps } from "@/app/dashboard/game/components/game-header/types";
import { GameStatusEnum } from "@/app/dashboard/games/types";

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

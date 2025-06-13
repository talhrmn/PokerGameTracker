import Chip from "@/features/dashboard/game/components/player-chip/player-chip";
import { PlayerSeatProps } from "@/features/dashboard/game/types/player-seat.types";
import { useMemo } from "react";
import styles from "./styles.module.css";

const PlayerSeat: React.FC<PlayerSeatProps> = ({
	player,
	isTableLeader,
	position,
	onClick,
}) => {
	const totalBuyIn = useMemo(() => {
		return player.buy_ins.reduce((sum, buyIn) => sum + buyIn.amount, 0);
	}, [player]);

	return (
		<div
			className={`${styles.playerSeat} ${
				isTableLeader ? styles.tableLeader : ""
			}`}
			style={{ top: position.top, left: position.left }}
			onClick={onClick}
		>
			<div className={styles.avatar}>
				{player.username.charAt(0).toUpperCase()}
			</div>
			<div className={styles.playerInfo}>
				<div className={styles.username}>{player.username}</div>
				<div className={styles.chipCount}>
					<div className={styles.chipIcon}>
						<Chip value={0} mini />
					</div>
					<div className={styles.chipInfo}>${totalBuyIn}</div>
				</div>
				<div
					className={styles.netProfit}
					style={{
						color:
							player.net_profit > 0
								? "#32CD32"
								: player.net_profit < 0
								? "#FF4136"
								: "#f0f0f0",
					}}
				>
					{player.net_profit > 0 ? "+" : ""}
					{player.net_profit.toLocaleString()}
				</div>
			</div>
		</div>
	);
};

export default PlayerSeat;

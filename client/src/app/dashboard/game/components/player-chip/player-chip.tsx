import { CHIP_COLORS } from "@/app/dashboard/game/components/player-chip/consts";
import styles from "@/app/dashboard/game/components/player-chip/styles.module.css";
import { ChipProps } from "@/app/dashboard/game/components/player-chip/types";

const Chip: React.FC<ChipProps> = ({ value, style, mini = false }) => {
	const chipColor = CHIP_COLORS[value] || CHIP_COLORS[0];
	return (
		<div
			className={`${styles.chip} ${mini ? styles.miniChip : ""}`}
			style={{
				backgroundColor: chipColor,
				...style,
			}}
		>
			{!mini && value > 0 && <span className={styles.chipValue}>${value}</span>}
		</div>
	);
};

export default Chip;

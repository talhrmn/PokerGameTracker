import { CHIP_COLORS } from "@/features/dashboard/game/consts/player-chip.consts";
import { ChipProps } from "@/features/dashboard/game/types/player-chip.types";
import styles from "./styles.module.css";

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

import Chip from "@/features/dashboard/game/components/player-chip/player-chip";
import PlayerSeat from "@/features/dashboard/game/components/player-seat/player-seat";
import { CHIP_VALUES } from "@/features/dashboard/game/consts/player-chip.consts";
import { GameTableProps } from "@/features/dashboard/game/types/game-table.types";
import { Position } from "@/features/dashboard/game/types/player-seat.types";
import { useCallback, useMemo } from "react";
import styles from "./styles.module.css";

const PokerTable: React.FC<GameTableProps> = ({
	players,
	totalPot,
	onPlayerSelect,
}) => {
	const calculatePlayerPosition = useCallback(
		(index: number): Position => {
			const tableCenter = { left: 350, top: 175 };
			const semiAxes = { a: 350, b: 175 };

			const theta = (2 * Math.PI * index) / players.length;

			const x = tableCenter.left + semiAxes.a * Math.cos(theta);
			const y = tableCenter.top + semiAxes.b * Math.sin(theta);

			return { left: `${(x / 700) * 100}%`, top: `${(y / 350) * 100}%` };
		},
		[players]
	);

	const playersWithPositions = useMemo(() => {
		return players.map((player, index) => ({
			...player,
			position: calculatePlayerPosition(index),
		}));
	}, [players, calculatePlayerPosition]);

	const getTableChips = () => {
		let remainingPot = totalPot;
		const chips: JSX.Element[] = [];

		CHIP_VALUES.forEach((value) => {
			const count = Math.floor(remainingPot / value);
			remainingPot -= count * value;

			const chipStack = count && (
				<div className={styles.chipStack} key={value}>
					{[...Array(count)].map((_, i) => (
						<Chip
							key={`${value}-${i}`}
							value={value}
							style={{
								transform: `translateY(${-i * 4}px)`,
								zIndex: 5 - i,
							}}
						/>
					))}
				</div>
			);

			if (chipStack) chips.push(chipStack);
		});

		return chips;
	};

	const tableLeader = useMemo(() => {
		return players.reduce((currentMax, player) => {
			return player.net_profit > currentMax.net_profit ? player : currentMax;
		});
	}, [players]);

	return (
		<div className={styles.tableContainer}>
			<div className={styles.table}>
				{playersWithPositions.map((player) => (
					<PlayerSeat
						key={player.user_id.toString()}
						player={player}
						position={player.position}
						isTableLeader={player.user_id === tableLeader.user_id}
						onClick={() => onPlayerSelect(player)}
					/>
				))}
				<div className={styles.tableFelt}>
					<div className={styles.potContainer}>
						{totalPot > 0 && (
							<>
								<div className={styles.chipContainer}>{getTableChips()}</div>
								<div className={styles.potAmount}>
									${totalPot.toLocaleString()}
								</div>
							</>
						)}
					</div>

					<div className={styles.tableRail}></div>
				</div>
			</div>
		</div>
	);
};

export default PokerTable;

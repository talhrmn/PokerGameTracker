import formStyles from "@/features/common/components/poker-table-form/styles.module.css";

import { useAuth } from "@/features/auth/contexts/context";
import PokerTableForm from "@/features/common/components/poker-table-form/poker-table-form";
import { TableForm } from "@/features/common/types";
import QRCodeInviteModal from "@/features/dashboard/table/components/table-invite/table-invite";
import {
	useGameResponse,
	useGameStart,
	useTableDelete,
	useTableSubmit,
} from "@/features/dashboard/table/hooks/table.queries";
import { TableDetailsModalProps } from "@/features/dashboard/table/types/table-detail.types";
import {
	CircleOff,
	CirclePlus,
	CircleX,
	Edit,
	LogIn,
	LucideIcon,
	Play,
	QrCode,
	Save,
	Trash2,
	View,
} from "lucide-react";
import { useRouter } from "next/navigation";
import React, { useMemo, useState } from "react";

const TableDetailsModal: React.FC<TableDetailsModalProps> = ({
	table,
	isCreator,
	onClose,
	onUpdateTables,
}) => {
	const { user } = useAuth();
	const router = useRouter();
	const [isEditing, setIsEditing] = useState(false);
	const [isQRModalOpen, setIsQRModalOpen] = useState(false);

	const myPlayer = table.players.find((player) => player.user_id === user._id);

	const formTitle = isCreator ? "Table Details" : "Table Invitation";

	const {
		mutate: tableSubmitMutation,
		isPending: submitLoading,
		// isError: submitError,
	} = useTableSubmit(onUpdateTables);

	const handleFormSubmit = async (params: TableForm) => {
		tableSubmitMutation({ tableId: table._id, params });
		setIsEditing(false);
	};

	const {
		mutate: tableDeleteMutation,
		isPending: deleteLoading,
		// isError: deleteError,
	} = useTableDelete(onUpdateTables, onClose);

	const handleDeleteTable = async () => {
		if (window.confirm("Are you sure you want to delete this table?"))
			tableDeleteMutation(table._id);
	};

	const handleOpenQRModal = () => {
		setIsQRModalOpen(true);
	};

	const redirectToGame = (gameId: string) => {
		router.push(`/dashboard/game/${gameId}`);
	};

	const {
		mutate: gameStartMutation,
		isPending: gameStartLoading,
		// isError: gameStartError,
	} = useGameStart(redirectToGame, onClose);

	const handleStartGame = async (params: Record<string, unknown>) => {
		gameStartMutation(params);
	};

	const {
		mutate: gameResponseMutation,
		isPending: gameResponseLoading,
		// isError: gameResponseError,
	} = useGameResponse(onUpdateTables, onClose);

	const handleJoinResponse = async (joinResponse: boolean) => {
		gameResponseMutation({ tableId: table._id, status: joinResponse });
	};

	const handleGoToGame = () => {
		router.push(`/dashboard/game/${table.game_id}`);
	};

	const getTableIcon = (Icon: LucideIcon) => {
		return <Icon size={16} style={{ marginRight: "0.5rem" }} />;
	};

	const loading = useMemo(
		() =>
			submitLoading || deleteLoading || gameStartLoading || gameResponseLoading,
		[submitLoading, deleteLoading, gameStartLoading, gameResponseLoading]
	);

	const cancelBtn = (
		<button
			type="button"
			onClick={() => setIsEditing(false)}
			className={formStyles.cancelButton}
			disabled={loading}
		>
			{getTableIcon(CircleX)}
			Cancel
		</button>
	);

	const saveEditBtn = (
		<button
			type="submit"
			className={formStyles.submitButton}
			disabled={loading}
		>
			{getTableIcon(Save)}
			{loading ? "Updating..." : "Save Changes"}
		</button>
	);

	const deleteBtn = (
		<button
			type="button"
			onClick={handleDeleteTable}
			className={formStyles.deleteButton}
			disabled={loading}
		>
			{getTableIcon(Trash2)}
			Delete Table
		</button>
	);

	const editBtn = (
		<button
			type="button"
			onClick={() => setIsEditing(true)}
			className={formStyles.submitButton}
		>
			{getTableIcon(Edit)}
			Edit Table
		</button>
	);

	const inviteBtn = (
		<button
			type="button"
			onClick={handleOpenQRModal}
			className={formStyles.inviteButton}
			disabled={loading}
		>
			{getTableIcon(QrCode)}
			Generate Invite
		</button>
	);

	const startGameBtn = (
		<button
			type="button"
			onClick={() =>
				handleStartGame({
					table_id: table._id,
					date: table.date,
					venue: table.venue,
					players: table.players,
				})
			}
			className={formStyles.playButton}
			disabled={loading}
		>
			{getTableIcon(Play)}
			Start Game
		</button>
	);

	const joinGameBtn = (
		<button
			type="button"
			onClick={() => handleJoinResponse(true)}
			className={formStyles.joinButton}
			disabled={loading || myPlayer?.status === "confirmed"}
		>
			{getTableIcon(CirclePlus)}
			Join Game
		</button>
	);

	const declineGameBtn = (
		<button
			type="button"
			onClick={() => handleJoinResponse(false)}
			className={formStyles.declineButton}
			disabled={loading || myPlayer?.status === "declined"}
		>
			{getTableIcon(CircleOff)}
			Decline Game
		</button>
	);

	const viewPlayersBtn = (
		<button
			type="button"
			onClick={handleOpenQRModal}
			className={formStyles.viewPlayersButton}
			disabled={loading}
		>
			{getTableIcon(View)}
			View Players
		</button>
	);

	const goToGameBtn = (
		<button
			type="button"
			onClick={handleGoToGame}
			className={formStyles.goToGameButton}
			disabled={loading}
		>
			{getTableIcon(LogIn)}
			Enter Game
		</button>
	);

	const getModeActions = (status: string) => {
		if (!isCreator) {
			switch (status) {
				case "scheduled":
				case "in_progress":
					return (
						<>
							{viewPlayersBtn}
							{myPlayer?.status === "invited" && declineGameBtn}
							{myPlayer?.status !== "confirmed" ? joinGameBtn : goToGameBtn}
						</>
					);
				default:
					return <>{viewPlayersBtn}</>;
			}
		} else {
			switch (status) {
				case "scheduled":
					return !isEditing ? (
						<>
							{editBtn}
							{inviteBtn}
							{startGameBtn}
						</>
					) : (
						<>
							{cancelBtn}
							{saveEditBtn}
							{deleteBtn}
						</>
					);
				case "in_progress":
					return (
						<>
							{inviteBtn}
							{goToGameBtn}
						</>
					);
				default:
					return <>{viewPlayersBtn}</>;
			}
		}
	};

	const formTable = {
		name: table.name,
		venue: table.venue,
		scheduled_date: new Date(table.date).toISOString().split("T")[0],
		scheduled_time: new Date(table.date)
			.toISOString()
			.split("T")[1]
			.slice(0, 5),
		minimum_buy_in: table.minimum_buy_in,
		maximum_players: table.maximum_players,
		game_type: table.game_type,
		blind_structure: table.blind_structure,
		description: table.description || "",
	} as TableForm;

	return (
		<>
			<PokerTableForm
				formTitle={formTitle}
				initialData={formTable}
				handleFormSubmit={(params: TableForm) => handleFormSubmit(params)}
				onClose={onClose}
				formActions={getModeActions(table.status)}
				editDisabled={!isEditing}
			/>

			{isQRModalOpen && (
				<QRCodeInviteModal
					tableId={table._id}
					tableStatus={table.status}
					isCreator={isCreator}
					tableName={table.name}
					players={table.players}
					onClose={() => setIsQRModalOpen(false)}
				/>
			)}
		</>
	);
};

export default TableDetailsModal;

import { TableForm } from "@/features/common/components/table-form/table-form";
import {
	TableActionHandlers,
	TableDetailsModalProps,
	TableGameFormProps,
} from "@/features/common/types";
import InviteModal from "@/features/dashboard/table/components/table-invite/table-invite";
import { useTableDetailsActions } from "@/features/dashboard/table/hooks/table-details.hook";
import {
	useGameResponse,
	useGameStart,
	useTableDelete,
	useTableSubmit,
} from "@/features/dashboard/table/hooks/table.queries";
import { useRouter } from "next/navigation";
import React, { useState } from "react";

export const TableDetailsModal: React.FC<TableDetailsModalProps> = ({
	table,
	isCreator,
	onClose,
	onUpdateTables,
}) => {
	const [isEditing, setIsEditing] = useState(false);
	const [isQRModalOpen, setIsQRModalOpen] = useState(false);
	const router = useRouter();

	// All your existing mutation hooks
	const { mutate: tableSubmitMutation, isPending: submitLoading } =
		useTableSubmit(onUpdateTables);
	const { mutate: tableDeleteMutation, isPending: deleteLoading } =
		useTableDelete(onUpdateTables, onClose);
	const { mutate: gameStartMutation, isPending: gameStartLoading } =
		useGameStart(
			(gameId: string) => router.push(`/dashboard/game/${gameId}`),
			onClose
		);
	const { mutate: gameResponseMutation, isPending: gameResponseLoading } =
		useGameResponse(onUpdateTables, onClose);

	const loading =
		submitLoading || deleteLoading || gameStartLoading || gameResponseLoading;

	const handleFormSubmit = (params: TableGameFormProps) => {
		tableSubmitMutation({ tableId: table._id, params });
		setIsEditing(false);
	};

	const actionHandlers: TableActionHandlers = {
		onDelete: () => {
			if (window.confirm("Are you sure you want to delete this table?")) {
				tableDeleteMutation(table._id);
			}
		},
		onStartGame: () => {
			gameStartMutation({
				table_id: table._id,
				date: table.date,
				venue: table.venue,
				players: table.players,
			});
		},
		onJoinGame: () =>
			gameResponseMutation({ tableId: table._id, status: true }),
		onDeclineGame: () =>
			gameResponseMutation({ tableId: table._id, status: false }),
		onViewPlayers: () => setIsQRModalOpen(true),
		onGoToGame: () => router.push(`/dashboard/game/${table.game_id}`),
		onInvite: () => setIsQRModalOpen(true),
	};

	const actions = useTableDetailsActions(
		table,
		isCreator,
		isEditing,
		setIsEditing,
		loading,
		actionHandlers
	);

	const formTable: TableGameFormProps = {
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
	};

	const formTitle = isCreator ? "Table Details" : "Table Invitation";

	return (
		<>
			<TableForm
				title={formTitle}
				initialData={formTable}
				onSubmit={handleFormSubmit}
				onClose={onClose}
				actions={actions}
				disabled={!isEditing}
				loading={loading}
			/>

			{isQRModalOpen && (
				<InviteModal
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

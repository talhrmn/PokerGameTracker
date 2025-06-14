// components/TableCreatorModal.tsx

import { TableForm } from "@/features/common/components/table-form/table-form";
import { TableGameFormProps } from "@/features/common/types";
import { useTableCreatorActions } from "@/features/dashboard/main/hooks/table-creator.hook";
import { useCreateTable } from "@/features/dashboard/table/hooks/table.queries";
import { Plus } from "lucide-react";
import React, { useState } from "react";
import { DEFAULT_FORM_STATE } from "../../consts/table-creator.consts";
import styles from "./styles.module.css";
import { ActionButton } from "@/features/common/components/action-button/action-button";

export const TableCreatorModal: React.FC = () => {
	const [isFormOpen, setIsFormOpen] = useState(false);
	const { mutate: createTableMutation, isPending: loading } = useCreateTable();

	const handleSubmit = (params: TableGameFormProps) => {
		createTableMutation(params);
	};

	const handleClose = () => {
		setIsFormOpen(false);
	};

	const actions = useTableCreatorActions(handleClose, loading);

	return (
		<div className={styles.container}>
			<ActionButton
				action={{
					id: "create-table",
					type: "button",
					label: "Schedule Game",
					icon: Plus,
					variant: "danger",
					onClick: () => setIsFormOpen(true),
				}}
				globalLoading={loading}
			/>

			{isFormOpen && (
				<TableForm
					title="Create New Poker Table"
					initialData={DEFAULT_FORM_STATE}
					onSubmit={handleSubmit}
					onClose={handleClose}
					actions={actions}
					loading={loading}
				/>
			)}
		</div>
	);
};

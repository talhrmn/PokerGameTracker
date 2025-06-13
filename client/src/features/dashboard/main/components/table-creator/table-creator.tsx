import formStyles from "@/features/dashboard/main/components/table-creator/styles.module.css";

import PokerTableForm from "@/features/common/components/poker-table-form/poker-table-form";
import { TableForm } from "@/features/common/types";
import { useCreateTable } from "@/features/dashboard/table/hooks/table.queries";
import { CalendarCheck, CircleX, Plus } from "lucide-react";
import { useState } from "react";
import { DEFAULT_FORM_STATE } from "../../consts/table-creator.consts";
import styles from "./styles.module.css";

const TableCreator = () => {
	const [isFormOpen, setIsFormOpen] = useState(false);

	const formTitle = "Create New Poker Table";

	const { mutate: createTableMutation, isPending: loading } = useCreateTable();

	const onClose = () => {
		setIsFormOpen(false);
	};

	const tableFormActions = (
		<>
			<button
				type="button"
				onClick={onClose}
				className={formStyles.cancelButton}
				disabled={loading}
			>
				<CircleX size={16} style={{ marginRight: "0.5rem" }} />
				Cancel
			</button>
			<button
				type="submit"
				className={formStyles.submitButton}
				disabled={loading}
			>
				<CalendarCheck size={16} style={{ marginRight: "0.5rem" }} />
				{loading ? "Creating..." : "Create Table"}
			</button>
		</>
	);

	return (
		<div className={styles.container}>
			<button
				type="button"
				className={styles.newTableButton}
				onClick={() => setIsFormOpen(true)}
			>
				<Plus className={styles.buttonIcon} />
				Schedule Game
			</button>
			{isFormOpen && (
				<PokerTableForm
					formTitle={formTitle}
					initialData={DEFAULT_FORM_STATE}
					handleFormSubmit={(params: TableForm) => createTableMutation(params)}
					onClose={onClose}
					formActions={tableFormActions}
					editDisabled={false}
				/>
			)}
		</div>
	);
};

export default TableCreator;

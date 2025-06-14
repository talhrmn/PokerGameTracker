// components/TableForm.tsx

import { ActionButton } from "@/features/common/components/action-button/action-button";
import { BLIND_OPTIONS, POKER_GAME_OPTIONS } from "@/features/common/consts";
import { useTableForm } from "@/features/common/hooks/table-form.hook";
import { TableFormProps } from "@/features/common/types";
import { Calendar, DollarSign, PlayCircle, Users, X } from "lucide-react";
import React from "react";
import styles from "./styles.module.css";

export const TableForm: React.FC<TableFormProps> = ({
	title,
	initialData,
	onSubmit,
	onClose,
	actions,
	disabled = false,
	loading: externalLoading = false,
}) => {
	const {
		formData,
		loading: internalLoading,
		error,
		handleInputChange,
		handleSubmit,
	} = useTableForm(initialData, onSubmit, onClose);

	const isLoading = internalLoading || externalLoading;
	const isDisabled = disabled || isLoading;

	const processedActions = actions.map((action) => ({
		...action,
		onClick: action.type === "submit" ? undefined : action.onClick,
	}));

	return (
		<div className={styles.modalOverlay} onClick={onClose}>
			<div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
				<button className={styles.closeButton} onClick={onClose}>
					<X size={20} />
				</button>

				<h3 className={styles.formTitle}>
					<PlayCircle className={styles.titleIcon} />
					{title}
				</h3>

				{error && <div className={styles.errorMessage}>{error}</div>}

				<form onSubmit={handleSubmit}>
					<div className={styles.formGrid}>
						<div className={styles.formFieldFull}>
							<label className={styles.fieldLabel}>Table Name</label>
							<input
								type="text"
								name="name"
								value={formData.name}
								onChange={handleInputChange}
								className={styles.inputField}
								required
								disabled={isDisabled}
							/>
						</div>

						<div className={styles.formFieldFull}>
							<label className={styles.fieldLabel}>Venue</label>
							<input
								type="text"
								name="venue"
								value={formData.venue}
								onChange={handleInputChange}
								className={styles.inputField}
								required
								disabled={isDisabled}
							/>
						</div>

						<div className={styles.formField}>
							<label className={styles.fieldLabel}>
								<Calendar className={styles.fieldIcon} /> Date
							</label>
							<input
								type="date"
								name="scheduled_date"
								value={formData.scheduled_date}
								onChange={handleInputChange}
								className={styles.inputField}
								required
								disabled={isDisabled}
							/>
						</div>

						<div className={styles.formField}>
							<label className={styles.fieldLabel}>Time</label>
							<input
								type="time"
								name="scheduled_time"
								value={formData.scheduled_time}
								onChange={handleInputChange}
								className={styles.inputField}
								required
								disabled={isDisabled}
							/>
						</div>

						<div className={styles.formField}>
							<label className={styles.fieldLabel}>
								<DollarSign className={styles.fieldIcon} /> Minimum Buy-in
							</label>
							<input
								type="number"
								name="minimum_buy_in"
								value={formData.minimum_buy_in}
								onChange={handleInputChange}
								className={styles.inputField}
								min="1"
								required
								disabled={isDisabled}
							/>
						</div>

						<div className={styles.formField}>
							<label className={styles.fieldLabel}>
								<Users className={styles.fieldIcon} /> Maximum Players
							</label>
							<input
								type="number"
								name="maximum_players"
								value={formData.maximum_players}
								onChange={handleInputChange}
								className={styles.inputField}
								min="2"
								max="14"
								required
								disabled={isDisabled}
							/>
						</div>

						<div className={styles.formField}>
							<label className={styles.fieldLabel}>Game Type</label>
							<select
								name="game_type"
								value={formData.game_type}
								onChange={handleInputChange}
								className={styles.selectField}
								disabled={isDisabled}
							>
								{POKER_GAME_OPTIONS.map((item, index) => (
									<option key={index} value={item}>
										{item}
									</option>
								))}
							</select>
						</div>

						<div className={styles.formField}>
							<label className={styles.fieldLabel}>Blind Structure</label>
							<select
								name="blind_structure"
								value={formData.blind_structure}
								onChange={handleInputChange}
								className={styles.selectField}
								disabled={isDisabled}
							>
								{BLIND_OPTIONS.map((item, index) => (
									<option key={index} value={item}>
										{item}
									</option>
								))}
							</select>
						</div>

						<div className={styles.formFieldFull}>
							<label className={styles.fieldLabel}>
								Description (Optional)
							</label>
							<textarea
								name="description"
								value={formData.description}
								onChange={handleInputChange}
								className={styles.textareaField}
								rows={3}
								disabled={isDisabled}
							/>
						</div>
					</div>

					<div className={styles.formActions}>
						{processedActions.map((action) => (
							<ActionButton
								key={action.id}
								action={action}
								globalLoading={isLoading}
							/>
						))}
					</div>
				</form>
			</div>
		</div>
	);
};

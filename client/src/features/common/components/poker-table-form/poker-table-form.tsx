import { BLIND_OPTIONS, POKER_GAME_OPTIONS } from "@/features/common/consts";
import { PokerTableFormProps } from "@/features/common/types";
import { Calendar, DollarSign, PlayCircle, Users, X } from "lucide-react";
import React, { useState } from "react";
import styles from "./styles.module.css";

const PokerTableForm: React.FC<PokerTableFormProps> = ({
	formTitle,
	initialData,
	handleFormSubmit,
	onClose,
	formActions,
	editDisabled,
}) => {
	const [formData, setFormData] = useState(initialData);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");

	const handleInputChange = (
		e: React.ChangeEvent<
			HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
		>
	) => {
		const { name, value } = e.target;
		setFormData({ ...formData, [name]: value });
	};

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setLoading(true);
		setError("");

		try {
			const dateTime = new Date(
				`${formData.scheduled_date}T${formData.scheduled_time}`
			);
			handleFormSubmit({
				...formData,
				date: dateTime.toISOString(),
			});
			onClose();
		} catch (err: unknown) {
			console.error(err);
			setError(err as string);
		} finally {
			setLoading(false);
		}
	};

	const formDisabled = editDisabled || loading;

	return (
		<div className={styles.modalOverlay} onClick={onClose}>
			<div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
				<button className={styles.closeButton} onClick={onClose}>
					<X size={20} />
				</button>

				<h3 className={styles.formTitle}>
					<PlayCircle className={styles.titleIcon} />
					{formTitle}
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
								disabled={formDisabled}
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
								disabled={formDisabled}
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
								disabled={formDisabled}
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
								disabled={formDisabled}
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
								disabled={formDisabled}
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
								disabled={formDisabled}
							/>
						</div>

						<div className={styles.formField}>
							<label className={styles.fieldLabel}>Game Type</label>
							<select
								name="game_type"
								value={formData.game_type}
								onChange={handleInputChange}
								className={styles.selectField}
								disabled={formDisabled}
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
								disabled={formDisabled}
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
								disabled={formDisabled}
							/>
						</div>
					</div>

					<div className={styles.formActions}>{formActions}</div>
				</form>
			</div>
		</div>
	);
};

export default PokerTableForm;

// components/ActionButton.tsx

import React from "react";
import styles from "./styles.module.css";
import { ActionButtonProps } from "@/features/common/types";

export const ActionButton: React.FC<ActionButtonProps> = ({
	action,
	globalLoading,
}) => {
	const getButtonClass = (variant: string) => {
		const baseClass = styles.actionButton;
		switch (variant) {
			case "primary":
				return `${baseClass} ${styles.primary}`;
			case "secondary":
				return `${baseClass} ${styles.secondary}`;
			case "danger":
				return `${baseClass} ${styles.danger}`;
			case "success":
				return `${baseClass} ${styles.success}`;
			case "warning":
				return `${baseClass} ${styles.warning}`;
			default:
				return `${baseClass} ${styles.primary}`;
		}
	};

	const isLoading = action.loading || globalLoading;
	const isDisabled = action.disabled || isLoading;

	return (
		<button
			type={action.type || "button"}
			onClick={action.onClick}
			className={getButtonClass(action.variant || "primary")}
			disabled={isDisabled}
		>
			{action.icon && (
				<action.icon size={16} style={{ marginRight: "0.5rem" }} />
			)}
			{isLoading ? action.loadingText || "Loading..." : action.label}
		</button>
	);
};

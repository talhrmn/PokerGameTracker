"use client";

import {
	AuthTab,
	AuthTabType,
	DEFAULT_AUTH_TAB,
	TabItems,
} from "@/features/auth/consts";
import { useAuth } from "@/features/auth/contexts/context";
import { Tabs } from "antd";
import React from "react";
import styles from "./styles.module.css";

const AuthLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
	const { activeForm, setActiveForm } = useAuth();
	const handleTabChange = (key: string) => {
		// key is "login" or "signup"
		if (key in AuthTab) {
			setActiveForm(key as AuthTabType);
		} else {
			// fallback
			setActiveForm(DEFAULT_AUTH_TAB.tabName as AuthTabType);
		}
	};

	return (
		<div className={styles.authContainer}>
			<div className={styles.authCard}>
				<div className={styles.tabsWrapper}>
					<Tabs
						activeKey={activeForm}
						onChange={(key) => handleTabChange(key)}
						size="large"
						tabPosition="top"
						className={styles.antTabsOverride}
						centered
						items={TabItems}
					/>
				</div>
				<div className={styles.contentWrapper}>{children}</div>
			</div>
		</div>
	);
};

export default AuthLayout;

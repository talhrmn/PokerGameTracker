"use client";

import { useAuth } from "@/features/auth/contexts/context";
import TableCreator from "@/features/dashboard/main/components/table-creator/table-creator";
import React from "react";
import styles from "./styles.module.css";

export default function MainLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	const { user } = useAuth();
	return (
		<>
			<div className={styles.header}>
				<div className={styles.headerContent}>
					<div className={styles.headerLeft}>
						<h2 className={styles.welcomeText}>
							Welcome back, {user.username}!
						</h2>
						<p className={styles.subtitle}>Manage you games</p>
					</div>
					<div className={styles.headerRight}>
						<div className={styles.headerButtons}>
							<TableCreator />
						</div>
					</div>
				</div>
			</div>
			<main className={styles.mainContainer}>{children}</main>
		</>
	);
}

"use client";

import Navbar from "@/features/common/components/navbar/navbar";
import React from "react";
import styles from "./styles.module.css";

export default function DashboardLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return (
		<div className={styles.dashboardContainer}>
			<Navbar />
			<main className={styles.mainContent}>{children}</main>
		</div>
	);
}

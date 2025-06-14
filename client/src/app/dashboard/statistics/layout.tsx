"use client";
import React from "react";
import styles from "./styles.module.css";

export default function StatisticsLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return (
		<>
			<h1 className={styles.title}>Statistics Over Time</h1>
			<main className={styles.statsContainer}>{children}</main>
		</>
	);
}

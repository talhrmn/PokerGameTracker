"use client";

import React from "react";
import styles from "./styles.module.css";

export default function TrendingsLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return (
		<>
			<h1 className={styles.title}>Game Trends Over Time</h1>
			<main className={styles.trendsContainer}>{children}</main>
		</>
	);
}

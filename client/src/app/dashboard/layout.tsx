"use client";

import Navbar from "@/app/dashboard/components/navbar/navbar";
import styles from "@/app/dashboard/styles.module.css";
import React from "react";

export default function DashboardLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return (
		<div className={styles.dashboardContainer}>
			<Navbar />
			{children}
		</div>
	);
}

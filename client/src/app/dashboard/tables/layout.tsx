"use client";

import React from "react";
import styles from "./styles.module.css";

export default function TablesLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return <main className={styles.tablesContainer}>{children}</main>;
}

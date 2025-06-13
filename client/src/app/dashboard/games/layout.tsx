"use client";

import React from "react";
import styles from "./styles.module.css";

export default function GamesLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return <main className={styles.gamesContainer}>{children}</main>;
}

"use client";

import React from "react";
import styles from "./styles.module.css";

export default function FriendsLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return <main className={styles.friendsContainer}>{children}</main>;
}

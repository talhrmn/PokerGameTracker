import React from "react";
import styles from "./header.styles.module.css";

export const Header = () => (
	<header className={styles.header}>
		<h1 className={styles.title}>Poker Game Manager</h1>
		<div className={styles.suits}>
			<span className={styles.black_suits}>♠</span>
			<span className={styles.red_suits}>♥</span>
			<span className={styles.red_suits}>♦</span>
			<span className={styles.black_suits}>♣</span>
		</div>
	</header>
);

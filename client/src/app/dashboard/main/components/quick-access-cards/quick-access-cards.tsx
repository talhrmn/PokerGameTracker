"use client";

import React from "react";
import Link from "next/link";
import { BarChart3, Users, Trophy } from "lucide-react";

import styles from "@/app/dashboard/main/components/quick-access-cards/styles.module.css";
import { QuickAccessCardsProps } from "@/app/dashboard/main/components/quick-access-cards/types";

export default function QuickAccessCards({ cards }: QuickAccessCardsProps) {
	const getIcon = (iconName: string) => {
		const iconClass = styles.icon;

		switch (iconName) {
			case "bar-chart-3":
				return <BarChart3 className={iconClass} />;
			case "users":
				return <Users className={iconClass} />;
			case "trophy":
				return <Trophy className={iconClass} />;
			default:
				return <BarChart3 className={iconClass} />;
		}
	};

	return (
		<div className={styles.container}>
			{cards.map((card, index) => (
				<div
					key={index}
					className={`${styles.card} ${styles[card.gradientFrom]} ${
						styles[card.gradientTo]
					}`}
				>
					<div className={styles.cardHeader}>
						{getIcon(card.icon)}
						<h3 className={styles.cardTitle}>{card.title}</h3>
					</div>
					<p className={styles.cardDescription}>{card.description}</p>
					<div className={styles.cardAction}>
						<Link
							href={card.link}
							className={`${styles.button} ${card.buttonColor}`}
						>
							{card.linkText}
						</Link>
					</div>
				</div>
			))}
		</div>
	);
}

import { Metadata } from "next";
import styles from "./styles.module.css";

export const metadata: Metadata = {
	title: "Poker Game | Live Table",
	description:
		"Live poker game interface for tracking players, buy-ins, and cash-outs",
};

export default function GameLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return <main className={styles.mainGameContainer}>{children}</main>;
}

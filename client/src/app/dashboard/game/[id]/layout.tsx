import { Metadata } from "next";

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
	return children;
}

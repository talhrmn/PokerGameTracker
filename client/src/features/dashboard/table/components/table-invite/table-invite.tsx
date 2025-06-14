import { useFriendsQuery } from "@/features/dashboard/friends/hooks/friends.queries";
import { FriendsProps } from "@/features/dashboard/friends/types";
import { useSendInvite } from "@/features/dashboard/table/hooks/table.queries";
import { statusOrder } from "@/features/dashboard/table/types/table-invite.consts";
import { InviteModalProps } from "@/features/dashboard/table/types/table-invite.types";
import { PlayerStatus } from "@/features/dashboard/table/types/tables.types";
import {
	Check,
	CircleX,
	Search,
	UserCheck,
	UserPlus,
	UserX,
} from "lucide-react";
import Image from "next/image";
import React, { useMemo, useState } from "react";
import styles from "./styles.module.css";

const InviteModal: React.FC<InviteModalProps> = ({
	tableId,
	tableStatus,
	isCreator,
	tableName,
	players: initialPlayers,
	onClose,
}) => {
	const [selectedFriends, setSelectedFriends] = useState<string[]>([]);
	const [searchTerm, setSearchTerm] = useState<string>("");
	const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false);
	const [players, setPlayers] = useState<PlayerStatus[]>(initialPlayers);
	const [playerIds, setPlayerIds] = useState<string[]>(
		initialPlayers.map((player) => player.user_id)
	);

	const formatFriendsList = (friendsList?: FriendsProps[]) => {
		if (!friendsList) return [];
		return friendsList.map((user: FriendsProps) => ({
			user_id: user._id,
			username: user.username,
		}));
	};

	const {
		data: friendsList,
		isLoading: friendsLoading,
		isError: friendsError,
	} = useFriendsQuery();

	if (friendsError) alert("Error fetching friends list");
	const friends = formatFriendsList(friendsList?.friends);

	const toggleFriendSelection = (friendId: string) => {
		setSelectedFriends((prev) =>
			prev.includes(friendId)
				? prev.filter((id) => id !== friendId)
				: [...prev, friendId]
		);
	};

	const {
		mutate: sendInviteMutation,
		isPending: invitePending,
		// isError: inviteError,
	} = useSendInvite();

	const sendInvites = async () => {
		if (selectedFriends.length === 0) return;
		const newPlayers = selectedFriends.map((friendId) => {
			const friend = friends.find(
				(f: Record<string, string>) => f.user_id === friendId
			);
			return {
				user_id: friendId,
				username: friend?.username || "",
				status: "invited" as const,
			};
		});

		sendInviteMutation({ tableId, params: newPlayers });
		setPlayers((prevPlayers) => [...prevPlayers, ...newPlayers]);
		setPlayerIds((prevIds) => [...prevIds, ...selectedFriends]);
		setSelectedFriends([]);
	};

	const filteredFriends = useMemo(() => {
		return friends
			.filter(
				(friend: Record<string, string>) => !playerIds.includes(friend.user_id)
			)
			.filter(
				(friend: Record<string, string>) =>
					searchTerm === "" ||
					friend.username.toLowerCase().includes(searchTerm.toLowerCase())
			);
	}, [friends, playerIds, searchTerm]);

	const tablePlayers = useMemo(() => {
		return (
			<>
				<h3 className={styles.sectionTitle}>Players</h3>
				{players.length === 0 ? (
					<p className={styles.noPlayers}>No players yet</p>
				) : (
					players
						.sort(
							(playerA, playerB) =>
								statusOrder[playerA.status] - statusOrder[playerB.status]
						)
						.map((player, index) => (
							<div key={player.user_id || index} className={styles.playerName}>
								{player.status === "confirmed" ? (
									<UserCheck className={styles.fieldIcon} />
								) : player.status === "invited" ? (
									<UserPlus className={styles.fieldIcon} />
								) : (
									<UserX className={styles.fieldIcon} />
								)}

								<div className={styles.usernameContainer}>
									{player.username}
								</div>

								<div
									className={`${
										player.status === "confirmed"
											? styles.confirmedPlayer
											: player.status === "invited"
											? styles.invitedPlayer
											: styles.declinedPlayer
									}`}
								>
									{player.status.toUpperCase()}
								</div>
							</div>
						))
				)}
			</>
		);
	}, [players]);

	return (
		<div className={styles.modalOverlay}>
			<div className={styles.modalContent}>
				<div className={styles.modalHeader}>
					<h2>Table Invite</h2>
					<button className={styles.closeButton} onClick={onClose}>
						<CircleX size={24} />
					</button>
				</div>

				<div className={styles.modalBody}>
					<h3 className={styles.tableName}>{tableName}</h3>
					{!isCreator || tableStatus === "completed" ? (
						tablePlayers
					) : (
						<>
							<div className={styles.qrCodeContainer}>
								<Image
									src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(
										JSON.stringify({ tableId, action: "join-request" })
									)}`}
									alt="QR Code Invite"
									width={200}
									height={200}
									className={styles.qrCode}
									unoptimized
								/>
								<p className={styles.scanText}>Scan to join table</p>
							</div>

							<div className={styles.divider}></div>

							{tablePlayers}

							<div className={styles.divider}></div>

							<div className={styles.friendsSection}>
								<h3 className={styles.sectionTitle}>Invite Friends</h3>

								<div className={styles.friendsDropdown}>
									<div
										className={styles.dropdownHeader}
										onClick={() => setIsDropdownOpen(!isDropdownOpen)}
									>
										<span>{selectedFriends.length} selected</span>
										<span
											className={`${styles.dropdownArrow} ${
												isDropdownOpen ? styles.open : ""
											}`}
										>
											▼
										</span>
									</div>

									{isDropdownOpen && (
										<div className={styles.dropdownContent}>
											<div className={styles.searchContainer}>
												<Search size={16} className={styles.searchIcon} />
												<input
													type="text"
													placeholder="Search by username..."
													value={searchTerm}
													onChange={(e) => setSearchTerm(e.target.value)}
													className={styles.searchInput}
												/>
											</div>

											{friendsLoading ? (
												<div className={styles.loadingState}>
													Loading friends...
												</div>
											) : filteredFriends.length === 0 ? (
												<p className={styles.noFriends}>
													{friends.length === 0
														? "No friends found"
														: searchTerm
														? "No matches found"
														: "All friends already invited"}
												</p>
											) : (
												<div className={styles.friendsList}>
													{filteredFriends.map(
														(friend: Record<string, string>) => (
															<div
																key={friend.user_id}
																className={`${styles.friendItem} ${
																	selectedFriends.includes(friend.user_id)
																		? styles.selected
																		: ""
																}`}
																onClick={() =>
																	toggleFriendSelection(friend.user_id)
																}
															>
																<div className={styles.friendAvatar}>
																	{friend.avatar_url ? (
																		<Image
																			src={friend.avatar_url}
																			alt={friend.username}
																			width={50}
																			height={50}
																			className={styles.avatar}
																			unoptimized
																		/>
																	) : (
																		<div className={styles.defaultAvatar}>
																			{friend.username.charAt(0)}
																		</div>
																	)}
																</div>
																<div className={styles.friendUsername}>
																	{friend.username}
																</div>
																{selectedFriends.includes(friend.user_id) && (
																	<div className={styles.checkmark}>
																		<Check size={16} />
																	</div>
																)}
															</div>
														)
													)}
												</div>
											)}
										</div>
									)}
								</div>

								<button
									className={`${styles.inviteButton} ${
										selectedFriends.length === 0 ? styles.disabled : ""
									}`}
									disabled={selectedFriends.length === 0 || friendsLoading}
									onClick={sendInvites}
								>
									{invitePending
										? "Sending..."
										: `Invite Selected (${selectedFriends.length})`}
								</button>
							</div>
						</>
					)}
				</div>
			</div>
		</div>
	);
};

export default InviteModal;

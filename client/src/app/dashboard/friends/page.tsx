"use client";

import GenericTable from "@/features/common/components/generic-table/generic-table";
import commonStyles from "@/features/common/styles.module.css";
import {
	FRIENDS_TABS,
	tableColumns,
} from "@/features/dashboard/friends/consts";
import {
	// useAddFriend,
	useFriendsQuery,
} from "@/features/dashboard/friends/hooks/friends.queries";
import {
	FriendsProps,
	FriendsTabKey,
} from "@/features/dashboard/friends/types";
import { Check, MailPlus, Trash2, X } from "lucide-react";
import { useCallback, /* useEffect, */ useMemo, useState } from "react";
import styles from "./styles.module.css";

export default function Friends() {
	const [activeTab, setActiveTab] = useState<string>(FRIENDS_TABS.friends.key);

	const [searchTerm, setSearchTerm] = useState<string>("");
	const [searchedFriends, setSearchedFriends] = useState<FriendsProps[]>([]);

	const { data, isLoading, isError } = useFriendsQuery();

	// const searchFriendMutation = useSearchFriend();

	// const addFriendMutation = useAddFriend();
	// const removeFriendMutation = useRemoveFriend();

	const onSearch = (input: string) => setSearchTerm(input);

	const addFriend = useCallback(
		async (friend_id: string) => {
			console.log("friend_id", friend_id);
			// addFriendMutation.mutate(friend_id);
		},
		[]
		// [addFriendMutation]
	);

	const removeFriend = useCallback(
		async (friend_id: string) => {
			console.log("friend_id", friend_id);
			// removeFriendMutation.mutate(friend_id);
		},
		[]
		// [removeFriendMutation]
	);

	const friendActions = useCallback(
		(tabName: string, friend_id: string, fromSearch: boolean = false) => (
			<div className={styles.center}>
				{tabName !== FRIENDS_TABS.friendInvites.key ? (
					<Trash2 onClick={() => removeFriend(friend_id)}>Delete</Trash2>
				) : (
					<>
						{!fromSearch ? (
							<>
								<Check onClick={() => addFriend(friend_id)}>Add</Check>
								<X>Decline</X>
							</>
						) : (
							<MailPlus onClick={() => addFriend(friend_id)}>I</MailPlus>
						)}
					</>
				)}
			</div>
		),
		[removeFriend, addFriend]
	);

	// useEffect(() => {
	// 	const fetchSearchResults = async () => {
	// 		if (activeTab === FRIENDS_TABS.friendInvites.key && searchTerm) {
	// 			const newFriends = await searchFriendMutation.mutateAsync(searchTerm);
	// 			const mappedFriends = newFriends.map((item: FriendsProps) => ({
	// 				...item,
	// 				actions: friendActions(activeTab, item._id, true),
	// 			}));
	// 			if (JSON.stringify(mappedFriends) !== JSON.stringify(searchedFriends)) {
	// 				setSearchedFriends(mappedFriends);
	// 			}
	// 		} else {
	// 			setSearchedFriends([]);
	// 		}
	// 	};

	// 	fetchSearchResults();
	// }, [searchTerm, activeTab, friendActions, searchFriendMutation]);

	const friendsList = useMemo(() => {
		if (!data) return [] as FriendsProps[];

		const friendsData = (data[activeTab as FriendsTabKey] || []).reduce<
			FriendsProps[]
		>((acc, item) => {
			if (
				item.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
				item.email.toLowerCase().includes(searchTerm.toLowerCase())
			) {
				acc.push({
					...item,
					actions: friendActions(activeTab, item._id),
				});
			}
			return acc;
		}, []);

		return friendsData.concat(searchedFriends);
	}, [data, activeTab, searchTerm, searchedFriends, friendActions]);

	// const deleteButton = (
	//   <Trash2 onClick={(e) => removeFriend(e)}>Delete</Trash2>
	// );
	// const addButton = <Plus onClick={(e) => addFriend(e)}>Add</Plus>;
	// const acceptButton = <Check onClick={(e) => addFriend(e)}>Add</Check>;
	// const declineButton = <X>Decline</X>;

	// const handleRowClick = (table: Table) => {
	//   setSelectedTable(table);
	// };

	if (isLoading) {
		return (
			<div className={commonStyles.loadingContainer}>
				<div className={commonStyles.loadingSpinner}></div>
				<p>Loading game data...</p>
			</div>
		);
	}

	if (isError) return <div>Error loading friends data</div>;

	const handleTabChange = (tabName: string) => {
		setSearchTerm("");
		setActiveTab(tabName);
	};

	return (
		<>
			<GenericTable
				data={friendsList}
				columns={tableColumns}
				title="Friends"
				onSearch={onSearch}
				tabs={Object.values(FRIENDS_TABS)}
				activeTab={activeTab}
				onTabChange={(tab) => handleTabChange(tab)}
				// onRowClick={handleRowClick}
				titleBarColor="#f56565"
			/>

			{/* {selectedTable && (
          <TableDetailsModal
            table={selectedTable}
            isCreator={activeTab === TABLE_TABS.created.key}
            onClose={handleCloseModal}
            onUpdateTables={fetchTables}
          />
        )} */}
		</>
	);
}

import { FriendsProps } from "@/app/dashboard/friends/types";
import styles from "@/app/dashboard/friends/styles.module.css";
import { ColumnDefinition } from "@/app/dashboard/components/generic-table/types";

export const FRIENDS_TABS = {
  friends: {
    key: "friends",
    label: "My Friends",
  },
  friendsInvited: {
    key: "friendsInvited",
    label: "Friends Invited",
  },
  friendInvites: {
    key: "friendInvites",
    label: "Friend Invites",
  },
};

export const tableColumns: ColumnDefinition<FriendsProps>[] = [
  {
    key: "username",
    header: "Username",
  },
  {
    key: "email",
    header: "User Email",
  },
  {
    key: "profile_pic",
    header: "User Porfile Picture",
  },
  {
    key: "actions",
    header: "Actions",
    className: styles.center,
  },
];

import { FRIENDS_TABS } from "@/features/dashboard/friends/consts";

export interface FriendsProps {
  _id: string;
  id: string;
  username: string;
  email: string;
  profile_pic?: string;
  actions?: React.JSX.Element;
}

export type FriendsTabKey = keyof typeof FRIENDS_TABS;

export interface FriendsResponse {
  friends: FriendsProps[];
  friends_invited: FriendsProps[];
  friend_invites: FriendsProps[];
}

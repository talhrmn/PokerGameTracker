import { AccessCard } from "@/features/dashboard/main/types/quick-access-cards.types";


export const ACCESS_CARDS: AccessCard[] = [
  {
    title: "Statistics Dashboard",
    description: "View analysis on you personal game play",
    icon: "bar-chart-3",
    link: "/dashboard/statistics",
    linkText: "View Statistics",
    gradientFrom: "purple500",
    gradientTo: "indigo600",
    buttonColor: "purple500",
  },
  {
    title: "Poker Trendings",
    description: "View graphs and charts recording the trends you and your friends achieve for all statistics over time",
    icon: "trophy",
    link: "/dashboard/trendings",
    linkText: "View Trends",
    gradientFrom: "blue500",
    gradientTo: "cyan600",
    buttonColor: "blue500",
  },
  {
    title: "Poker Buddies",
    description: "View analysis on statistics between you and your friends",
    icon: "users",
    link: "/dashboard/friends",
    linkText: "Manage Friends",
    gradientFrom: "red500",
    gradientTo: "orange600",
    buttonColor: "red500",
  },
];

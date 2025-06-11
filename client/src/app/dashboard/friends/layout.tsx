"use client";

import React from "react";
import styles from "@/app/dashboard/friends/styles.module.css";

export default function FriendsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div className={styles.tablesLayout}>{children}</div>;
}

"use client";

import React from "react";
import styles from "@/app/dashboard/tables/styles.module.css";

export default function TablesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div className={styles.tablesLayout}>{children}</div>;
}

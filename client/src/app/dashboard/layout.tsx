"use client";

// import { useAuth } from "@/app/auth/context/context";
import Navbar from "@/app/dashboard/components/navbar/navbar";
import styles from "@/app/dashboard/styles.module.css";
// import { useRouter } from "next/navigation";
import React from "react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // const { userIsAuthenticated, loading } = useAuth();
  // const router = useRouter();

  return (
    <div className={styles.container}>
      <Navbar />
      {children}
    </div>
  );
}

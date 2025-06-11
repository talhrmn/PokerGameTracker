"use client";

import {
  AuthTab,
  AuthTabType,
  DEFAULT_AUTH_TAB,
  TabItems,
} from "@/app/auth/consts";
import styles from "@/app/auth/styles.module.css";
import { Tabs } from "antd";
import { useRouter } from "next/navigation";
import React, { useState } from "react";

const AuthLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState(DEFAULT_AUTH_TAB);

  const handleTabClick = (tabName: AuthTabType) => {
    const tabValue = AuthTab[tabName];
    setActiveTab(tabValue);
    router.push(`/auth/${tabValue.tabName}`);
  };

  return (
    <div className={styles.container}>
      <div className={styles.authWindow}>
        <div className={styles.tabs}>
          <Tabs
            defaultActiveKey={activeTab.tabName}
            onChange={(e) => handleTabClick(e as AuthTabType)}
            size="large"
            tabPosition="top"
            className={styles.tabs}
            centered
            items={TabItems}
          />
          {children}
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;

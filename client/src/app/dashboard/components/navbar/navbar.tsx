"use client";

import { useAuth } from "@/app/auth/context/context";
import { MENU_ITEMS } from "@/app/dashboard/components/navbar/consts";
import styles from "@/app/dashboard/components/navbar/styles.module.css";
import { LogOut, User } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

export default function Navbar() {
	const pathname = usePathname();
	const { user, logout } = useAuth();
	const [isProfileMenuOpen, setIsProfileMenuOpen] = useState<boolean>(false);

	return (
		<nav className={styles.nav}>
			<div className={styles.container}>
				<div className={styles.navContent}>
					<div className={styles.leftSection}>
						<div className={styles.logoContainer}>
							<span className={styles.logoWrapper}>
								<span className={styles.logo}>PokerTracker</span>
								<span className={styles.logoSymbol}>♠</span>
							</span>
						</div>
						<div className={styles.desktopMenu}>
							<div className={styles.menuItems}>
								<nav>
									{Object.entries(MENU_ITEMS).map(([key, value]) => (
										<Link
											key={key}
											href={`/dashboard/${value.link}`}
											className={
												pathname.endsWith(value.link)
													? styles.activeMenuItem
													: styles.menuItem
											}
										>
											{value.title}
										</Link>
									))}
								</nav>
							</div>
						</div>
					</div>

					<div className={styles.rightSection}>
						<div className={styles.desktopProfile}>
							<div className={styles.profileContainer}>
								<button
									onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
									className={styles.profileButton}
								>
									<span className={styles.profileName}>{user.username}</span>
									<div className={styles.avatarContainer}>
										{user && user.username.charAt(0).toUpperCase()}
									</div>
								</button>

								{isProfileMenuOpen && (
									<div className={styles.profileMenu}>
										<Link href="/profile" className={styles.profileMenuItem}>
											<div className={styles.menuItemWithIcon}>
												<User className={styles.menuIcon} />
												Your Profile
											</div>
										</Link>
										<button
											onClick={logout}
											className={styles.profileMenuButton}
										>
											<div className={styles.menuItemWithIcon}>
												<LogOut className={styles.menuIcon} />
												Sign out
											</div>
										</button>
									</div>
								)}
							</div>
						</div>
					</div>
				</div>
			</div>
		</nav>
	);
}

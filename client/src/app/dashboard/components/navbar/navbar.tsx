"use client";

import React, { useState, useRef, useEffect } from "react";
import { useAuth } from "@/app/auth/context/context";
import { MENU_ITEMS } from "@/app/dashboard/components/navbar/consts";
import styles from "@/app/dashboard/components/navbar/styles.module.css";
import { LogOut, User } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
	const pathname = usePathname();
	const { user, logout } = useAuth();
	const [isProfileMenuOpen, setIsProfileMenuOpen] = useState<boolean>(false);

	// Close dropdown if clicking outside
	const profileRef = useRef<HTMLDivElement>(null);
	useEffect(() => {
		function handleClickOutside(event: MouseEvent) {
			if (
				profileRef.current &&
				!profileRef.current.contains(event.target as Node)
			) {
				setIsProfileMenuOpen(false);
			}
		}
		document.addEventListener("mousedown", handleClickOutside);
		return () => {
			document.removeEventListener("mousedown", handleClickOutside);
		};
	}, []);

	// Determine active menu key by checking if pathname ends with the link or contains it
	const isActive = (link: string) => {
		// e.g., pathname "/dashboard/stats" endsWith "stats"
		return pathname?.endsWith(link);
	};

	return (
		<nav className={styles.navbar}>
			<div className={styles.navbarContainer}>
				<div className={styles.navbarLeft}>
					<Link href="/dashboard" className={styles.logoLink}>
						<span className={styles.logoText}>PokerTracker</span>
						<span className={styles.logoSymbol}>♠</span>
					</Link>
					<div className={styles.menuWrapper}>
						<nav className={styles.menuList}>
							{Object.entries(MENU_ITEMS).map(([key, value]) => (
								<Link
									key={key}
									href={`/dashboard/${value.link}`}
									className={
										isActive(value.link)
											? styles.menuItemActive
											: styles.menuItem
									}
								>
									{value.title}
								</Link>
							))}
						</nav>
					</div>
				</div>

				<div className={styles.navbarRight}>
					<div className={styles.profileWrapper} ref={profileRef}>
						<button
							onClick={() => setIsProfileMenuOpen((prev) => !prev)}
							className={styles.profileButton}
						>
							<span className={styles.profileName}>{user.username}</span>
							<div className={styles.avatar}>
								{user.username.charAt(0).toUpperCase()}
							</div>
						</button>
						{isProfileMenuOpen && (
							<div className={styles.profileDropdown}>
								<Link href="/profile" className={styles.dropdownItem}>
									<div className={styles.itemWithIcon}>
										<User className={styles.icon} />
										Your Profile
									</div>
								</Link>
								<button
									onClick={logout}
									className={styles.dropdownItemButton}
									type="button"
								>
									<div className={styles.itemWithIcon}>
										<LogOut className={styles.icon} />
										Sign out
									</div>
								</button>
							</div>
						)}
					</div>
				</div>
			</div>
		</nav>
	);
}

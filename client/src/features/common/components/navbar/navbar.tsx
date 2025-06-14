"use client";

import { useAuth } from "@/features/auth/contexts/context";
import { ActionButton } from "@/features/common/components/action-button/action-button";
import { NAVBAR_MENU_ITEMS } from "@/features/common/consts";
import { LogOut, User } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import styles from "./styles.module.css";

export default function Navbar() {
	const pathname = usePathname();
	const { user, logout } = useAuth();
	const [isProfileMenuOpen, setIsProfileMenuOpen] = useState<boolean>(false);

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

	const isActive = (link: string) => {
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
							{Object.entries(NAVBAR_MENU_ITEMS).map(([key, value]) => (
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
						<ActionButton
							action={{
								id: "profile",
								type: "button",
								label:
									user.username.toLowerCase().charAt(0).toUpperCase() +
									user.username.toLowerCase().slice(1),
								icon: User,
								variant: "primary",
								onClick: () => setIsProfileMenuOpen((prev) => !prev),
							}}
						/>
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

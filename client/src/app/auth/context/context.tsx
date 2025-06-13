"use client";

import {
	AuthTabType,
	COOKIE_EXPERATION_IN_DAYS,
	DASHBOARD_ROUTE,
	DEFAULT_AUTH_TAB,
} from "@/app/auth/consts";
import { logoutUser, useAuthQuery } from "./auth-queries";

import { EMPTY_USER } from "@/app/auth/context/consts";
import { AuthContextType } from "@/app/auth/context/types";
import { message } from "antd";
import { AxiosError } from "axios";
import Cookies from "js-cookie";
import { redirect, usePathname, useRouter } from "next/navigation";
import {
	createContext,
	useCallback,
	useContext,
	useEffect,
	useState,
} from "react";

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
	children,
}) => {
	const router = useRouter();
	const pathname = usePathname();
	const [token, setToken] = useState<string | null>(
		Cookies.get("token") || null
	);

	const [activeForm, setActiveForm] = useState<AuthTabType>(() => {
		if (!pathname) return DEFAULT_AUTH_TAB.tabName as AuthTabType;

		// Check if pathname contains login or signup
		if (pathname.includes("login")) return "login";
		if (pathname.includes("signup")) return "signup";

		// Default fallback
		return DEFAULT_AUTH_TAB.tabName as AuthTabType;
	});

	const {
		data: user = EMPTY_USER,
		refetch: refetchUser,
		isLoading: loading,
	} = useAuthQuery(token);

	useEffect(() => {
		if (!token && !pathname.includes("auth")) redirect("/auth");
	}, [token, pathname]);

	const handleSuccess = useCallback(
		(access_token: string) => {
			Cookies.set("token", access_token, {
				expires: COOKIE_EXPERATION_IN_DAYS,
			});
			setToken(access_token);
			refetchUser();
			router.push(DASHBOARD_ROUTE);
		},
		[router, refetchUser]
	);

	const handleError = useCallback((err: unknown) => {
		const error = err as AxiosError<{ detail: { msg: string }[] | string }>;
		const detail = error.response?.data?.detail;
		const errorMessage = Array.isArray(detail)
			? detail.map((item) => item.msg).join(" ")
			: typeof detail === "string"
			? detail
			: "Unexpected error occurred";
		message.error(errorMessage);
	}, []);

	const logout = useCallback(() => {
		logoutUser();
		setToken(null);
		router.push("/auth");
	}, [router]);

	return (
		<AuthContext.Provider
			value={{
				user,
				token,
				setToken,
				logout,
				refetchUser,
				userIsAuthenticated: !!token,
				loading: loading,
				handleSuccess,
				handleError,
				activeForm,
				setActiveForm,
			}}
		>
			{children}
		</AuthContext.Provider>
	);
};

export const useAuth = () => {
	const context = useContext(AuthContext);
	if (!context) throw new Error("useAuth must be used within an AuthProvider");
	return context;
};

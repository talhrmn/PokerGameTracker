"use client";

import LoginForm from "@/features/auth/components/login-form";
import SignUpForm from "@/features/auth/components/signup-form";
import { useAuth } from "@/features/auth/contexts/context";

const AuthPage = () => {
	const { activeForm } = useAuth();
	return activeForm === "login" ? <LoginForm /> : <SignUpForm />;
};

export default AuthPage;

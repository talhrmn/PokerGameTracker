"use client";

import LoginForm from "@/features/auth/components/auth-forms/login-form";
import SignUpForm from "@/features/auth/components/auth-forms/signup-form";
import { useAuth } from "@/features/auth/contexts/context";

const AuthPage = () => {
	const { activeForm } = useAuth();
	return activeForm === "login" ? <LoginForm /> : <SignUpForm />;
};

export default AuthPage;

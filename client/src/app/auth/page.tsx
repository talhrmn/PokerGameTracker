"use client";

import LoginForm from "@/app/auth/components/login-form";
import SignUpForm from "@/app/auth/components/register-form";
import { useAuth } from "@/app/auth/context/context";

const AuthPage = () => {
	const { activeForm } = useAuth();
	return activeForm === "login" ? <LoginForm /> : <SignUpForm />;
};

export default AuthPage;

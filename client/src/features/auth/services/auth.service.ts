import { api } from "@/clients/api-client";
import {
	AccessType,
	CredentialsType,
	SignUpFormType,
	UserType,
} from "@/features/auth/types";
import { AuthTab } from "../consts";

class AuthService {
	async getCurrentUser(): Promise<UserType> {
		return api.getData<UserType>("/users/me");
	}

	async login(creds: CredentialsType): Promise<AccessType> {
		const loginData = new URLSearchParams({
			username: creds.username,
			password: creds.password,
		});
		return api.postData<URLSearchParams, AccessType>(
			AuthTab.login.submitRoute,
			loginData
		);
	}

	async signup(userData: SignUpFormType): Promise<AccessType> {
		return api.postData<SignUpFormType, AccessType>(
			AuthTab.signup.submitRoute,
			userData
		);
	}
}

export const authService = new AuthService();

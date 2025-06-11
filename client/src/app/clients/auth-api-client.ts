import { AuthTab } from "@/app/auth/consts";
import {
	AccessType,
	CredentialsType,
	SignUpFormType,
	UserType,
} from "@/app/auth/context/types";
import { api } from "@/app/clients/api-client";

class AuthApiClient {
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

export const authApiClient = new AuthApiClient();

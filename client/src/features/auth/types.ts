import { QueryObserverResult, RefetchOptions } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { AuthTabType } from "./consts";

export interface ErrorResponseDetail {
  msg?: string;
}

export interface ErrorResponse {
  detail?: string | ErrorResponseDetail[];
}

export interface UserType {
  username: string;
  email: string;
  _id: string;
}

export interface AuthContextType {
  user: UserType;
  token: string | null;
  setToken: (token: string | null) => void;
  logout: () => void;
  refetchUser: (options?: RefetchOptions) => Promise<QueryObserverResult>;
  userIsAuthenticated: boolean;
  loading: boolean;
  handleSuccess: (access_token: string) => void;
  handleError: (err: AxiosError) => void;
  activeForm: AuthTabType;
  setActiveForm: (tab: AuthTabType) => void;
}

export interface AccessType {
  access_token: string;
}

export interface CredentialsType {
  username: string;
  password: string;
}

export interface SignUpFormType extends CredentialsType {
  email: string;
}

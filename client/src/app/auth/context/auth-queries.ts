import { EMPTY_USER } from "@/app/auth/context/consts";
import {
  AccessType,
  CredentialsType,
  SignUpFormType
} from "@/app/auth/context/types";
import { authApiClient } from "@/app/clients/auth-api-client";
import { queryClient } from "@/app/clients/query-client";
import { useMutation, useQuery } from "@tanstack/react-query";
import { AxiosError } from "axios";
import Cookies from "js-cookie";

export const useAuthQuery = (token: string | null) => {
  return useQuery({
    queryKey: ["user"],
    queryFn: () => authApiClient.getCurrentUser(),
    enabled: !!token,
    retry: 1,
    select: (data) => data ?? EMPTY_USER,
    staleTime: 1000 * 60 * 60 * 24,
  });
};

export const useLoginMutation = (
  onSuccess: (token: string) => void,
  onError: (err: AxiosError) => void
) => {
  return useMutation<AccessType, AxiosError, CredentialsType>({
    mutationFn: (creds) => authApiClient.login(creds),
    onSuccess: (data) => onSuccess(data.access_token),
    onError,
  });
};

export const useSignUpMutation = (
  onSuccess: (token: string) => void,
  onError: (err: AxiosError) => void
) => {
  return useMutation<AccessType, AxiosError, SignUpFormType>({
    mutationFn: (userData) => authApiClient.signup(userData),
    onSuccess: (data) => onSuccess(data.access_token),
    onError,
  });
};

export const logoutUser = () => {
  Cookies.remove("token");
  queryClient.setQueryData(["user"], EMPTY_USER);
};

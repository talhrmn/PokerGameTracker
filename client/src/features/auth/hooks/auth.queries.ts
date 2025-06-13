import { queryClient } from "@/clients/query-client";
import { EMPTY_USER } from "@/features/auth/consts";
import { authService } from "@/features/auth/services/auth.service";
import {
  AccessType,
  CredentialsType,
  SignUpFormType
} from "@/features/auth/types";
import { useMutation, useQuery } from "@tanstack/react-query";
import { AxiosError } from "axios";
import Cookies from "js-cookie";

export const useAuthQuery = (token: string | null) => {
  return useQuery({
    queryKey: ["user"],
    queryFn: () => authService.getCurrentUser(),
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
    mutationFn: (creds) => authService.login(creds),
    onSuccess: (data) => onSuccess(data.access_token),
    onError,
  });
};

export const useSignUpMutation = (
  onSuccess: (token: string) => void,
  onError: (err: AxiosError) => void
) => {
  return useMutation<AccessType, AxiosError, SignUpFormType>({
    mutationFn: (userData) => authService.signup(userData),
    onSuccess: (data) => onSuccess(data.access_token),
    onError,
  });
};

export const logoutUser = () => {
  Cookies.remove("token");
  queryClient.setQueryData(["user"], EMPTY_USER);
};

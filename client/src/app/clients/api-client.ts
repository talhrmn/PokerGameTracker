import axios, { AxiosRequestConfig } from "axios";
import { BASE_URL } from "@/app/consts";
import Cookies from "js-cookie";
import { Params } from "@/app/clients/types";

export const apiClient = axios.create({ baseURL: BASE_URL });

apiClient.interceptors.request.use((config) => {
  const token = Cookies.get("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const api = {
  async getData<Res>(
    endpoint: string,
    params?: Params,
    config?: AxiosRequestConfig
  ): Promise<Res> {
    const { data } = await apiClient.get<Res>(endpoint, { params, ...config });
    return data;
  },

  async postData<Req, Res>(
    endpoint: string,
    body: Req,
    config?: AxiosRequestConfig
  ): Promise<Res> {
    const { data } = await apiClient.post<Res>(endpoint, body, config);
    return data;
  },

  async putData<Req, Res>(
    endpoint: string,
    body?: Req,
    config?: AxiosRequestConfig
  ): Promise<Res> {
    const { data } = await apiClient.put<Res>(endpoint, body, config);
    return data;
  },

  async deleteData<Req, Res>(
    endpoint: string,
    body?: Req,
    config?: AxiosRequestConfig
  ): Promise<Res> {
    const { data } = await apiClient.delete<Res>(endpoint, {
      ...config,
      data: body,
    });
    return data;
  },
};

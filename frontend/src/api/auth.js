import axiosInstance from "./axiosInstance";

export const loginRequest = async (credentials) => {
  const response = await axiosInstance.post("/auth/login", credentials);
  return response.data;
};
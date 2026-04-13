import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

export const loginRequest = async (credentials) => {
  const response = await axios.post(
    `${API_URL}/api/v1/auth/login`,
    credentials,
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  return response.data;
};
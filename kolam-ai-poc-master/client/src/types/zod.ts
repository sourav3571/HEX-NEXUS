import { z } from "zod";

export const LoginRequest = z.object({
  email: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
})
export type LoginRequestParams = z.infer<typeof LoginRequest>;
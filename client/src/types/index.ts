export interface ErrorRes {
  status: number;
  response: {
    data: {
      message: string;
      log?: string[];
    }
  }
}

export interface Response {
  success: boolean;
  message: string;
}
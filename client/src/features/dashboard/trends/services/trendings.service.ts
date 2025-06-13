import { api } from "@/clients/api-client";
import { TrendsProps } from "@/features/dashboard/trends/types";

class TrendingsService {
    async getTrends(): Promise<TrendsProps> {
        return api.getData<TrendsProps>("/trends")
    }
}

export const trendingsService = new TrendingsService();

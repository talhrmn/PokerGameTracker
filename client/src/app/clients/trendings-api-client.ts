import { api } from "@/app/clients/api-client";
import { TrendsProps } from "@/app/dashboard/trendings/types";

class TrendingsApiClient {
    async getTrends(): Promise<TrendsProps> {
        return api.getData<TrendsProps>("/trends")
    }
}

export const trendingsApiClient = new TrendingsApiClient();

import { api } from "@/app/clients/api-client";
import { DashboardStatsType } from "@/app/dashboard/main/types";

class DashStatsApiClient {
    async getDashStats(): Promise<DashboardStatsType> {
        return api.getData<DashboardStatsType>("/statistics/dashboard")
    }
}

export const dashStatsApiClient = new DashStatsApiClient();

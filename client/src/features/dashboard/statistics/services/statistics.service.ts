import { api } from "@/clients/api-client";
import { DashboardStatsType } from "@/features/dashboard/main/types";
import { UserStatsType } from "@/features/dashboard/statistics/types";

class StatisticsService {
    async getStatistics(): Promise<UserStatsType> {
        return api.getData<UserStatsType>("/statistics/")
    }

    async getDashStats(): Promise<DashboardStatsType> {
        return api.getData<DashboardStatsType>("/statistics/dashboard")
    }
}

export const statisticsService = new StatisticsService();

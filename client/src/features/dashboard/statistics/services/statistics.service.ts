import { api } from "@/clients/api-client";
import { DashboardStatsType } from "@/features/dashboard/main/types";
import { MonthlyStatsProps } from "@/features/dashboard/statistics/types";

class StatisticsService {
    async getStatistics(): Promise<MonthlyStatsProps[]> {
        return api.getData<MonthlyStatsProps[]>("/statistics/monthly")
    }

    async getDashStats(): Promise<DashboardStatsType> {
        return api.getData<DashboardStatsType>("/statistics/dashboard")
    }
}

export const statisticsService = new StatisticsService();

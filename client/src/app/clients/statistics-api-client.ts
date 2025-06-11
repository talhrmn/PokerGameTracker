import { api } from "@/app/clients/api-client";
import { MonthlyStatsProps } from "@/app/dashboard/statistics/types";

class StatisticsApiClient {
    async getStatistics(): Promise<MonthlyStatsProps[]> {
        return api.getData<MonthlyStatsProps[]>("/statistics/monthly")
    }
}

export const statisticsApiClient = new StatisticsApiClient();

import { statisticsService } from "@/features/dashboard/statistics/services/statistics.service";
import { useQuery } from "@tanstack/react-query";

export const useFetchStats = () => {
	return useQuery({
		queryKey: ["stats"],
		queryFn: () => statisticsService.getStatistics(),
	});
};

export const useFetchDashStatsQuery = () => {
	return useQuery({
		queryKey: ["dash-stats"],
		queryFn: () => statisticsService.getDashStats(),
	});
};

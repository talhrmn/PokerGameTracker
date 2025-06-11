import { dashStatsApiClient } from "@/app/clients/dash-stats-api-client";
import { useQuery } from "@tanstack/react-query";

export const useFetchDashStatsQuery = () => {
	return useQuery({
		queryKey: ["dash-stats"],
		queryFn: () => dashStatsApiClient.getDashStats(),
	});
};

import { statisticsApiClient } from "@/app/clients/statistics-api-client";
import { useQuery } from "@tanstack/react-query";

export const useFetchStats = () => {
	return useQuery({
		queryKey: ["monthly-stats"],
		queryFn: () => statisticsApiClient.getStatistics(),
	});
};

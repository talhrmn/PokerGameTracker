import { trendingsApiClient } from "@/app/clients/trendings-api-client";
import { useQuery } from "@tanstack/react-query";

export const useTrendingsQuery = () => {
	return useQuery({
		queryKey: ["trendings"],
		queryFn: () => trendingsApiClient.getTrends(),
	});
};

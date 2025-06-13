import { trendingsService } from "@/features/dashboard/trends/services/trendings.service";
import { useQuery } from "@tanstack/react-query";

export const useTrendingsQuery = () => {
	return useQuery({
		queryKey: ["trendings"],
		queryFn: () => trendingsService.getTrends(),
	});
};

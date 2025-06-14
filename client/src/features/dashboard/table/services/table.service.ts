import { api } from "@/clients/api-client";
import { TableGameFormProps } from "@/features/common/types";
import { TableResponseType } from "@/features/dashboard/table/types/table-detail.types";
import { SendInviteType } from "@/features/dashboard/table/types/table-invite.types";
import { PlayerStatus, Table, TablesData } from "@/features/dashboard/table/types/tables.types";

class TableService {
    async getTable(tableId: string): Promise<Table> {
        return api.getData<Table>(`/tables/${tableId}`)
    }
    
    async getTables(activeTab: string, limit: number, skip: number): Promise<TablesData> {
        return api.getData<TablesData>(`/tables/${activeTab}`, {
            limit: limit,
            skip: skip,
          })
    }

    async createTable(params: TableGameFormProps): Promise<Table> {
        return api.postData<TableGameFormProps, Table>("/tables/create", params)
    }

    async updateTable(params: { tableId: string; params: TableGameFormProps }): Promise<Table> {
        return api.putData<TableGameFormProps, Table>(
            `/tables/${params.tableId}`,
            params.params
          )
    }

    async deleteTable(tableId: string): Promise<Table> {
        return api.deleteData(`/tables/${tableId}`)
    }

    async sendTableInvite(params: SendInviteType): Promise<Table> {
        return api.putData<PlayerStatus[], Table>(`/tables/${params.tableId}/invite`, params.params)
    }

    async reponsedToTableInvite(params: TableResponseType): Promise<Table> {
        return api.putData<null, Table>(
            `/tables/${params.tableId}/${params.status ? "confirmed" : "declined"}`
        )
    }
}

export const tableService = new TableService();

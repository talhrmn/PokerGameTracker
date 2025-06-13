import { api } from "@/clients/api-client";
import { TableForm } from "@/features/common/types";
import { TableResponseType } from "@/features/dashboard/table/types/table-detail.types";
import { SendInviteType } from "@/features/dashboard/table/types/table-invite.types";
import { PlayerStatus, Table } from "@/features/dashboard/table/types/tables.types";

class TableService {
    async getTable(tableId: string): Promise<Table> {
        return api.getData<Table>(`/tables/${tableId}`)
    }
    
    async getTables(): Promise<Table[]> {
        return api.getData<Table[]>("/tables")
    }

    async createTable(params: TableForm): Promise<Table> {
        return api.postData<TableForm, Table>("/tables/create", params)
    }

    async updateTable(params: { tableId: string; params: TableForm }): Promise<Table> {
        return api.putData<TableForm, Table>(
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

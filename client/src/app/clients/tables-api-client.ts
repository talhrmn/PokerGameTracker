import { api } from "@/app/clients/api-client";
import { SendInviteType } from "@/app/dashboard/tables/components/table-invite/types";
import { TableResponseType } from "@/app/dashboard/tables/components/table-details/types";
import { PlayerStatus, Table } from "@/app/dashboard/tables/types";
import { TableForm } from "@/app/dashboard/components/poker-table-form/types";

class TablesApiClient {
    async getTable(tableId: string): Promise<Table> {
        return api.getData<Table>(`/tables/${tableId}`)
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

export const tablesApiClient = new TablesApiClient();

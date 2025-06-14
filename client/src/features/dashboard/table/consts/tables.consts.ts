import { ColumnDefinition } from "@/features/common/types";
import { Table } from "@/features/dashboard/table/types/tables.types";
import { Calendar, MapPin, Users } from "lucide-react";

export const TABLE_TABS = {
  created: {
    key: "created",
    label: "Tables I Created",
  },
  invited: {
    key: "invited",
    label: "Tables I'm Invited To",
  },
};

export const tableColumns: ColumnDefinition<Table>[] = [
  {
    key: "name",
    header: "Table Name",
  },
  {
    key: "game_type",
    header: "Game Type",
  },
  {
    key: "date",
    header: "Date",
    icon: Calendar,
    render: (table) =>
      new Date(table.date).toLocaleDateString("en-US", {
        month: "short",
        day: "2-digit",
        year: "numeric",
      }),
  },
  {
    key: "venue",
    header: "Venue",
    icon: MapPin,
  },
  {
    key: "players",
    header: "Players",
    render: (table) =>
      `${
        table.players.filter((player) => player.status !== "declined").length
      }/${table.maximum_players}`,
    icon: Users,
  },
  {
    key: "status",
    header: "Status",
    render: (table) => {
      return table.status.replace("_", " ").toUpperCase();
    },
  },
];

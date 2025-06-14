// hooks/useTableDetailsActions.ts

import { useAuth } from "@/features/auth/contexts/context";
import { FormAction, TableActionHandlers } from "@/features/common/types";
import {
  CircleOff,
  CirclePlus,
  CircleX,
  Edit,
  LogIn,
  Play,
  QrCode,
  Save,
  Trash2,
  View,
} from "lucide-react";

export const useTableDetailsActions = (
  table: any, // Replace with proper type
  isCreator: boolean,
  isEditing: boolean,
  setIsEditing: (editing: boolean) => void,
  loading: boolean,
  handlers: TableActionHandlers
): FormAction[] => {
  const { user } = useAuth();
  const myPlayer = table.players.find((player: any) => player.user_id === user._id);

  if (!isCreator) {
    // Guest user actions
    const guestActions: FormAction[] = [
      {
        id: 'viewPlayers',
        label: 'View Players',
        icon: View,
        onClick: handlers.onViewPlayers,
        variant: 'secondary'
      }
    ];

    if (table.status === 'scheduled' || table.status === 'in_progress') {
      if (myPlayer?.status === 'invited') {
        guestActions.push({
          id: 'decline',
          label: 'Decline Game',
          icon: CircleOff,
          onClick: handlers.onDeclineGame,
          variant: 'danger',
          disabled: loading
        });
      }

      if (myPlayer?.status !== 'confirmed') {
        guestActions.push({
          id: 'join',
          label: 'Join Game',
          icon: CirclePlus,
          onClick: handlers.onJoinGame,
          variant: 'success',
          disabled: loading
        });
      } else {
        guestActions.push({
          id: 'goToGame',
          label: 'Enter Game',
          icon: LogIn,
          onClick: handlers.onGoToGame,
          variant: 'primary',
          disabled: loading
        });
      }
    }

    return guestActions;
  }

  // Creator actions
  if (table.status === 'scheduled') {
    if (!isEditing) {
      return [
        {
          id: 'edit',
          label: 'Edit Table',
          icon: Edit,
          onClick: () => setIsEditing(true),
          variant: 'secondary'
        },
        {
          id: 'invite',
          label: 'Generate Invite',
          icon: QrCode,
          onClick: handlers.onInvite,
          variant: 'warning',
          disabled: loading
        },
        {
          id: 'start',
          label: 'Start Game',
          icon: Play,
          onClick: handlers.onStartGame,
          variant: 'success',
          disabled: loading
        }
      ];
    } else {
      return [
        {
          id: 'cancel',
          label: 'Cancel',
          icon: CircleX,
          onClick: () => setIsEditing(false),
          variant: 'secondary',
          disabled: loading
        },
        {
          id: 'save',
          label: 'Save Changes',
          icon: Save,
          type: 'submit',
          variant: 'primary',
          disabled: loading,
          loading: loading,
          loadingText: 'Updating...'
        },
        {
          id: 'delete',
          label: 'Delete Table',
          icon: Trash2,
          onClick: handlers.onDelete,
          variant: 'danger',
          disabled: loading
        }
      ];
    }
  }

  if (table.status === 'in_progress') {
    return [
      {
        id: 'invite',
        label: 'Generate Invite',
        icon: QrCode,
        onClick: handlers.onInvite,
        variant: 'warning',
        disabled: loading
      },
      {
        id: 'goToGame',
        label: 'Enter Game',
        icon: LogIn,
        onClick: handlers.onGoToGame,
        variant: 'primary',
        disabled: loading
      }
    ];
  }

  // Default case
  return [
    {
      id: 'viewPlayers',
      label: 'View Players',
      icon: View,
      onClick: handlers.onViewPlayers,
      variant: 'secondary'
    }
  ];
};

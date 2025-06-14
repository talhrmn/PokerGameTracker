import { FormAction } from "@/features/common/types";
import { CalendarCheck, CircleX } from "lucide-react";

export const useTableCreatorActions = (
  onClose: () => void,
  loading: boolean = false
): FormAction[] => {
  return [
    {
      id: 'cancel',
      label: 'Cancel',
      icon: CircleX,
      onClick: onClose,
      variant: 'secondary',
      disabled: loading
    },
    {
      id: 'create',
      label: 'Create Table',
      icon: CalendarCheck,
      type: 'submit',
      variant: 'primary',
      disabled: loading,
      loading: loading,
      loadingText: 'Creating...'
    }
  ];
};

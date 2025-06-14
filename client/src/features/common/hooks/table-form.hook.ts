// hooks/useTableForm.ts

import { TableGameFormProps } from "@/features/common/types";
import { useState } from 'react';

export const useTableForm = (
  initialData: TableGameFormProps,
  onSubmit: (data: TableGameFormProps) => void,
  onClose: () => void
) => {
  const [formData, setFormData] = useState(initialData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const dateTime = new Date(`${formData.scheduled_date}T${formData.scheduled_time}`);
      await onSubmit({
        ...formData,
        date: dateTime.toISOString(),
      });
      onClose();
    } catch (err: unknown) {
      console.error(err);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData(initialData);
    setError("");
  };

  return {
    formData,
    loading,
    error,
    handleInputChange,
    handleSubmit,
    resetForm,
    setError
  };
};

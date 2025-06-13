"use client";

import {
	INVALID_PASSWORD_MSG,
	VALID_PASSWORD_PATTERN,
} from "@/features/auth/consts";
import { useAuth } from "@/features/auth/contexts/context";
import { useLoginMutation } from "@/features/auth/hooks/auth.queries";
import { Button, Form, Input, message } from "antd";
import { useForm } from "antd/es/form/Form";
import React, { useState } from "react";
import styles from "./form.styles.module.css";

const LoginForm: React.FC = () => {
	const { handleSuccess, handleError } = useAuth();
	const [form] = useForm();
	const [isButtonDisabled, setIsButtonDisabled] = useState(true);

	const handleFormChange = () => {
		const hasErrors = form
			.getFieldsError()
			.some(({ errors }) => errors.length > 0);
		const allFieldsTouched = form.isFieldsTouched(true);
		setIsButtonDisabled(hasErrors || !allFieldsTouched);
	};

	const loginMutation = useLoginMutation(handleSuccess, handleError);

	const handleSubmit = async () => {
		try {
			const values = await form.validateFields();
			const loginData = {
				username: values.username,
				password: values.password,
			};
			loginMutation.mutate(loginData);
		} catch (error: unknown) {
			if (error instanceof Error) {
				message.error(error.message || "Please ensure all fields are valid.");
			} else {
				message.error("An unexpected error occurred.");
			}
		}
	};

	return (
		<>
			<Form
				form={form}
				onFinish={handleSubmit}
				className={styles.form}
				layout="vertical"
				onFieldsChange={handleFormChange}
			>
				<Form.Item
					name="username"
					rules={[{ required: true, message: "Please input your username!" }]}
				>
					<Input
						id="username"
						type="username"
						className={styles.input}
						placeholder="Username"
					/>
				</Form.Item>

				<Form.Item
					name="password"
					rules={[
						{ required: true, message: "Please input your password!" },
						{
							pattern: VALID_PASSWORD_PATTERN,
							message: INVALID_PASSWORD_MSG,
						},
					]}
				>
					<Input.Password
						id="password"
						className={styles.input}
						placeholder="Password"
					/>
				</Form.Item>

				<Button
					type="primary"
					htmlType="submit"
					className={styles.button}
					disabled={isButtonDisabled}
				>
					Submit
				</Button>
			</Form>
		</>
	);
};

export default LoginForm;

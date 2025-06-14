"use client";

import {
	INVALID_PASSWORD_MSG,
	VALID_EMAIL_PATTERN,
	VALID_PASSWORD_PATTERN,
} from "@/features/auth/consts";
import { useAuth } from "@/features/auth/contexts/context";
import { useSignUpMutation } from "@/features/auth/hooks/auth.queries";
import { Button, Form, Input, message } from "antd";
import { useForm } from "antd/es/form/Form";
import { useState } from "react";
import styles from "./form.styles.module.css";

const SignUpForm: React.FC = () => {
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

	const signUpMutation = useSignUpMutation(handleSuccess, handleError);

	const handleSubmit = async () => {
		try {
			const values = await form.validateFields();
			const signUpData = { ...values };
			delete signUpData.passwordConfirmation;
			signUpMutation.mutate(signUpData);
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
						className={styles.input}
						placeholder="Username"
					/>
				</Form.Item>

				<Form.Item
					name="email"
					rules={[
						{ required: true, message: "Please input your email!" },
						{
							pattern: VALID_EMAIL_PATTERN,
							message: "Invalid email format",
						},
					]}
				>
					<Input
						id="email"
						type="email"
						className={styles.input}
						placeholder="Email"
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

				<Form.Item
					name="passwordConfirmation"
					dependencies={["password"]}
					rules={[
						{ required: true, message: "Please confirm your password!" },
						({ getFieldValue }) => ({
							validator(_, value) {
								if (!value || getFieldValue("password") === value) {
									return Promise.resolve();
								}
								return Promise.reject("Passwords do not match");
							},
						}),
					]}
				>
					<Input.Password
						id="password-confirmation"
						className={styles.input}
						placeholder="Confirm Password"
					/>
				</Form.Item>

				<Form.Item>
					<Button
						type="primary"
						htmlType="submit"
						className={styles.button}
						disabled={isButtonDisabled}
					>
						Submit
					</Button>
				</Form.Item>
			</Form>
		</>
	);
};

export default SignUpForm;

import React from "react";
import api from "../utils/api.js";
import { useAuth } from "../components/AuthContext.jsx";
import { Button, Form, Input } from "antd";

function RegisterPage() {
    const { login } = useAuth();

    const handleSubmit = async (values) => {
        try {
            await api.post("/auth/register", {
                email: values.email,
                password: values.password,
            });

            const res = await api.post("/auth/login", {
                email: values.email,
                password: values.password,
            });

            login(res.data.access_token, false);
            window.location.href = "/dashboard";
        } catch (err) {
            alert("Registration failed. Please check your data.");
        }
    };

    return (
        <div className="flex items-center justify-center bg-gray-100 h-screen">
            <Form
                name="register"
                labelCol={{ span: 8 }}
                wrapperCol={{ span: 16 }}
                style={{ maxWidth: 1000 }}
                autoComplete="off"
                onFinish={handleSubmit}
            >

                <Form.Item
                    label="Email"
                    name="email"
                    rules={[{ required: true, message: "Please input your email!" }]}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    label="Password"
                    name="password"
                    rules={[{ required: true, message: "Please input your password!" }]}
                >
                    <Input.Password />
                </Form.Item>

                <Form.Item
                    label="Confirm Password"
                    name="confirm_password"
                    dependencies={["password"]}
                    labelCol={{ span: 8, style: { paddingRight: "80px" } }}
                    rules={[
                        { required: true, message: "Please confirm your password!" },
                        ({ getFieldValue }) => ({
                            validator(_, value) {
                                if (!value || getFieldValue("password") === value) {
                                    return Promise.resolve();
                                }
                                return Promise.reject(new Error("Passwords do not match!"));
                            },
                        }),
                    ]}
                >
                    <Input.Password />
                </Form.Item>

                <Form.Item wrapperCol={{ offset: 8, span: 16 }}>
                    <Button type="primary" htmlType="submit">
                        Register
                    </Button>
                </Form.Item>
            </Form>
        </div>
    );
}

export default RegisterPage;

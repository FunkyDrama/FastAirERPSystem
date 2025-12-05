import React from "react";
import api from "../utils/api.js";
import {useAuth} from "../components/AuthContext.jsx";
import {App, Button, Card, Form, Input} from "antd";
import {Link} from "react-router-dom";

function RegisterPage() {
    const {login} = useAuth();
    const {message} = App.useApp();
    const [form] = Form.useForm();

    const handleSubmit = async (values) => {
        try {
            await api.post("/auth/register", {
                email: values.email, password: values.password,
            });

            const res = await api.post("/auth/login", {
                email: values.email, password: values.password,
            });

            login(res.data.access_token, false);
            window.location.href = "/dashboard";
        } catch (err) {
            const res = err?.response;
            if (res?.status === 422 && Array.isArray(res.data?.detail)) {
                const pwdErr = res.data.detail.find((d) => Array.isArray(d.loc) && d.loc.at(-1) === "password");
                if (pwdErr?.msg) {
                    form.setFields([{name: "password", errors: [pwdErr.msg]}]);
                    return;
                }
                const first = res.data.detail[0]?.msg || "Validation error";
                message.error(first);
                return;
            }

            if ((res?.status === 409 || res?.status === 400) && res.data?.detail) {
                message.error(res.data.detail);
                if (String(res.data.detail).toLowerCase().includes("email")) {
                    form.setFields([{name: "email", errors: [res.data.detail]}]);
                }
                return;
            }
            message.error("Registration failed. Please check your data.");
        }
    };

    return (<div className="flex items-center justify-center bg-gray-100 min-h-screen p-4">
        <Card className="w-full max-w-md shadow-lg">
            <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Create Account</h2>
                <p className="text-gray-500 text-sm mt-1">Join FastAir today</p>
            </div>

            <Form
                form={form}
                name="register"
                layout="vertical"
                autoComplete="off"
                onFinish={handleSubmit}
                size="large"
            >
                <Form.Item
                    label="Email"
                    name="email"
                    rules={[{required: true, message: "Please input your email!"}, {
                        type: "email", message: "Invalid email format!"
                    },]}
                >
                    <Input placeholder="your@email.com"/>
                </Form.Item>

                <Form.Item
                    label="Password"
                    name="password"
                    rules={[{required: true, message: "Please input your password!"}, {
                        min: 6, message: "Password must be at least 6 characters!"
                    },]}
                >
                    <Input.Password placeholder="••••••••"/>
                </Form.Item>

                <Form.Item
                    label="Confirm Password"
                    name="confirm_password"
                    dependencies={["password"]}
                    rules={[{required: true, message: "Please confirm your password!"}, ({getFieldValue}) => ({
                        validator(_, value) {
                            if (!value || getFieldValue("password") === value) {
                                return Promise.resolve();
                            }
                            return Promise.reject(new Error("Passwords do not match!"));
                        },
                    }),]}
                >
                    <Input.Password placeholder="••••••••"/>
                </Form.Item>

                <Form.Item>
                    <Button type="primary" htmlType="submit" block>
                        Register
                    </Button>
                </Form.Item>

                <div className="text-center mt-4">
                    <span className="text-gray-600">Already have an account? </span>
                    <Link to="/login" className="text-blue-600 hover:text-blue-800 font-medium">
                        Login
                    </Link>
                </div>
            </Form>
        </Card>
    </div>);
}

export default RegisterPage;
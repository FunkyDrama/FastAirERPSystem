import React from "react";
import api from "../utils/api.js";
import {useAuth} from "../components/AuthContext.jsx";
import {Button, Checkbox, Form, Input} from "antd";
import {Link} from "react-router-dom";

function LoginPage() {
    const {login} = useAuth();

    const handleSubmit = async (values) => {
        try {
            const res = await api.post("/auth/login", {
                email: values.email,
                password: values.password,
            });

            login(res.data.access_token, values.remember);
            window.location.href = "/dashboard";
        } catch {
            alert("Login failed. Please check your credentials.");
        }
    };

    const handleGoogleLogin = async () => {
        try {
            const res = await api.get("/auth/google/url");
            window.location.href = res.data.url;
        } catch {
            alert("Failed to start Google login");
        }
    };

    return (
        <div className="flex items-center justify-center bg-gray-100 h-screen">
            <Form
                name="basic"
                labelCol={{span: 8}}
                wrapperCol={{span: 16}}
                style={{maxWidth: 1000}}
                initialValues={{remember: true}}
                autoComplete="off"
                onFinish={handleSubmit}
            >
                <Form.Item
                    label="Email"
                    name="email"
                    style={{width: 400}}
                    rules={[{required: true, message: "Please input your email!"}]}
                >
                    <Input/>
                </Form.Item>

                <Form.Item
                    label="Password"
                    name="password"
                    rules={[{required: true, message: "Please input your password!"}]}
                >
                    <Input.Password/>
                </Form.Item>

                <Form.Item
                    name="remember"
                    valuePropName="checked"
                    wrapperCol={{offset: 8, span: 16}}
                >
                    <Checkbox>Remember me</Checkbox>
                </Form.Item>

                <Form.Item wrapperCol={{offset: 8, span: 16}}>
                    <Button type="primary" htmlType="submit">
                        Login
                    </Button>

                    <div className="mt-10">
                        Don't have an account? <Link to="/register">Register</Link>
                    </div>

                    <p className="mt-5 flex justify-center items-center">or</p>

                    <div className="mt-5 flex justify-center items-center">
                        <Button
                            size="middle"
                            type="default"
                            onClick={handleGoogleLogin}
                            className="flex items-center gap-2"
                        >
                            <svg
                                width="20"
                                height="20"
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 640 640"
                                fill="currentColor"
                            >
                                <path
                                    d="M564 325.8C564 467.3 467.1 568 324 568C186.8 568 76 457.2 76 320C76 182.8 186.8 72 324 72C390.8 72 447 96.5 490.3 136.9L422.8 201.8C334.5 116.6 170.3 180.6 170.3 320C170.3 406.5 239.4 476.6 324 476.6C422.2 476.6 459 406.2 464.8 369.7L324 369.7L324 284.4L560.1 284.4C562.4 297.1 564 309.3 564 325.8z"></path>
                            </svg>
                            Login with Google
                        </Button>
                    </div>
                </Form.Item>
            </Form>
        </div>
    );
}

export default LoginPage;

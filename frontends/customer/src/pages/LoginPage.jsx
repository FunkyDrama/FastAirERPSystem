import React, {useState} from "react";
import api from "../utils/api.js";
import {useAuth} from "../components/AuthContext.jsx";
import {Button, Card, Checkbox, Form, Input} from "antd";
import {Link} from "react-router-dom";
import {useNavigate} from "react-router";

function LoginPage() {
    const {login} = useAuth();
    const navigate = useNavigate();
    const [error, setError] = useState("");

    const handleSubmit = async (values) => {
        try {
            await login({
                email: values.email, password: values.password,
            });
            navigate("/dashboard");
        } catch {
            setError("Login failed. Please check your credentials.");
        }
    };

    const handleGoogleLogin = async () => {
        try {
            const res = await api.get("/auth/google/url");
            if (res.data.url) {
                window.location.href = res.data.url;
            } else {
                console.error("No URL received from server");
                alert("Failed to start Google login");
            }
        } catch (error) {
            console.error("Google login error:", error);
            alert("Failed to start Google login");
        }
    };

    return (<div className="flex items-center justify-center bg-gray-100 min-h-screen p-4">
        <Card className="w-full max-w-md shadow-lg">
            <Form
                name="basic"
                layout="vertical"
                initialValues={{remember: true}}
                autoComplete="off"
                onFinish={handleSubmit}
            >
                <Form.Item
                    label="Email"
                    name="email"
                    rules={[{required: true, message: "Please input your email!"}, {
                        type: "email", message: "Please enter a valid email!"
                    }]}
                >
                    <Input size="large" placeholder="your@email.com"/>
                </Form.Item>

                <Form.Item
                    label="Password"
                    name="password"
                    rules={[{required: true, message: "Please input your password!"}]}
                >
                    <Input.Password size="large" placeholder="••••••••"/>
                </Form.Item>

                <Form.Item name="remember" valuePropName="checked">
                    <Checkbox>Remember me</Checkbox>
                </Form.Item>

                {error && (<div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
                    {error}
                </div>)}

                <Form.Item>
                    <Button
                        type="primary"
                        htmlType="submit"
                        size="large"
                        className="w-full"
                    >
                        Login
                    </Button>
                </Form.Item>

                <div className="text-center mb-4">
                    Don't have an account?{" "}
                    <Link to="/register" className="text-blue-600 hover:text-blue-800">
                        Register
                    </Link>
                </div>

                <div className="relative my-6">
                    <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-gray-300"></div>
                    </div>
                    <div className="relative flex justify-center text-sm">
                        <span className="px-2 bg-white text-gray-500">or</span>
                    </div>
                </div>

                <Button
                    size="large"
                    onClick={handleGoogleLogin}
                    className="w-full flex items-center justify-center gap-2"
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
            </Form>
        </Card>
    </div>);
}

export default LoginPage;
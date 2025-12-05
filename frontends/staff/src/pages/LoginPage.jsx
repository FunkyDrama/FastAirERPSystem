import React, {useState} from "react";
import {useAuth} from "../components/AuthContext.jsx";
import {Alert, Button, Checkbox, Form, Input, Typography} from "antd";
import {LockOutlined, UserOutlined} from "@ant-design/icons";
import {motion} from "framer-motion";
import {useNavigate} from "react-router-dom";

const {Title, Text} = Typography;

function LoginPage() {
    const {login} = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (values) => {
        try {
            await login({
                email: values.email, password: values.password,
            });
            navigate("/");
        } catch {
            setError("Login failed. Please check your credentials.");
        }
    };

    return (<div
            className="min-h-screen flex items-center justify-center bg-cover bg-center bg-fixed relative"
            style={{backgroundImage: "url('/background.jpg')"}}
        >
            <div className="absolute inset-0 bg-gradient-to-br from-blue-900/80 to-gray-900/80"/>

            <motion.div
                initial={{opacity: 0, y: 20}}
                animate={{opacity: 1, y: 0}}
                transition={{duration: 0.6}}
                className="relative z-10 w-full max-w-md px-6"
            >
                <div className="bg-white rounded-2xl shadow-2xl p-8">
                    <div className="text-center mb-8">
                        <Title level={2} className="!mb-2 !text-gray-800">
                            Staff Portal
                        </Title>
                        <Text type="secondary" className="text-base">
                            Sign in to access FastAir staff dashboard
                        </Text>
                    </div>

                    {error && (<motion.div
                            initial={{opacity: 0, height: 0}}
                            animate={{opacity: 1, height: "auto"}}
                            className="mb-6"
                        >
                            <Alert
                                message={error}
                                type="error"
                                showIcon
                                className="rounded-lg"
                            />
                        </motion.div>)}

                    <Form
                        name="staffLogin"
                        initialValues={{remember: true}}
                        onFinish={handleSubmit}
                        size="large"
                        className="space-y-4"
                    >
                        <Form.Item
                            name="email"
                            rules={[{required: true, message: "Please input your email!"}, {
                                type: "email",
                                message: "Please enter a valid email!"
                            }]}
                        >
                            <Input
                                prefix={<UserOutlined className="text-gray-400"/>}
                                placeholder="Email address"
                                className="rounded-lg h-12"
                            />
                        </Form.Item>

                        <Form.Item
                            name="password"
                            rules={[{required: true, message: "Please input your password!"}]}
                        >
                            <Input.Password
                                prefix={<LockOutlined className="text-gray-400"/>}
                                placeholder="Password"
                                className="rounded-lg h-12"
                            />
                        </Form.Item>

                        <Form.Item>
                            <div className="flex items-center justify-between">
                                <Form.Item name="remember" valuePropName="checked" noStyle>
                                    <Checkbox className="text-gray-600">
                                        Remember me
                                    </Checkbox>
                                </Form.Item>
                            </div>
                        </Form.Item>

                        <Form.Item className="mb-0">
                            <Button
                                type="primary"
                                htmlType="submit"
                                loading={loading}
                                className="w-full h-12 rounded-lg bg-blue-600 hover:bg-blue-700 border-none text-base font-medium"
                            >
                                Sign In
                            </Button>
                        </Form.Item>
                    </Form>

                    <div className="mt-8 text-center">
                        <Text type="secondary" className="text-sm">
                            FastAir Staff Portal - Secure Access Only
                        </Text>
                    </div>
                </div>
            </motion.div>
        </div>);
}

export default LoginPage;
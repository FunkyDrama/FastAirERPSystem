import React, {useEffect, useState} from "react";
import {Button, Card, Form, Input, message, Modal, Popconfirm, Select, Space, Table, Tag, Typography} from "antd";
import {DeleteOutlined, PlusOutlined, TeamOutlined, UserOutlined} from "@ant-design/icons";
import {motion} from "framer-motion";
import api from "../utils/api.js";
import {ROLES} from "../utils/roles.js";

const {Title, Text} = Typography;
const {Option} = Select;

function SupervisorStaffPage() {
    const [loading, setLoading] = useState(false);
    const [staff, setStaff] = useState([]);
    const [modalVisible, setModalVisible] = useState(false);
    const [form] = Form.useForm();

    useEffect(() => {
        loadStaff();
    }, []);

    const loadStaff = async () => {
        setLoading(true);
        try {
            const res = await api.get("/supervisor/staff-users");
            setStaff(res.data);
        } catch (err) {
            message.error("Failed to load staff");
        } finally {
            setLoading(false);
        }
    };

    const handleCreateStaff = async (values) => {
        try {
            await api.post("/supervisor/staff-users", {
                email: values.email,
                password: values.password,
                role: values.role
            });
            message.success("Staff member created successfully");
            setModalVisible(false);
            form.resetFields();
            loadStaff();
        } catch (err) {
            message.error("Failed to create staff member");
        }
    };

    const handleDeleteStaff = async (staffId) => {
        try {
            await api.delete(`/supervisor/staff-users/${staffId}`);
            message.success("Staff member deleted successfully");
            loadStaff();
        } catch (err) {
            message.error("Failed to delete staff member");
        }
    };

    const getRoleColor = (role) => {
        switch (role) {
            case ROLES.SUPERVISOR:
                return "red";
            case ROLES.GATE:
                return "blue";
            case ROLES.CHECKIN:
                return "green";
            default:
                return "default";
        }
    };

    const columns = [
        {
            title: "Email",
            dataIndex: "email",
            key: "email",
            render: (email) => (
                <Space>
                    <UserOutlined/>
                    {email}
                </Space>
            ),
        },
        {
            title: "Role",
            dataIndex: "role",
            key: "role",
            render: (role) => (
                <Tag color={getRoleColor(role)}>
                    {role?.replace('_', ' ').toUpperCase()}
                </Tag>
            ),
        },
        {
            title: "Actions",
            key: "actions",
            render: (_, record) => (
                <Popconfirm
                    title="Delete Staff Member"
                    description="Are you sure you want to delete this staff member?"
                    onConfirm={() => handleDeleteStaff(record.user_id)}
                    okText="Yes"
                    cancelText="No"
                >
                    <Button danger size="small" icon={<DeleteOutlined/>}>
                        Delete
                    </Button>
                </Popconfirm>
            ),
        },
    ];

    return (
        <div className="min-h-screen bg-gray-100 p-6">
            <motion.div
                initial={{opacity: 0, y: 20}}
                animate={{opacity: 1, y: 0}}
                transition={{duration: 0.6}}
            >
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <Title level={2} className="!mb-2">
                            Staff Management
                        </Title>
                        <Text type="secondary" className="text-base">
                            Manage staff members and their roles
                        </Text>
                    </div>
                    <Button
                        type="primary"
                        size="large"
                        icon={<PlusOutlined/>}
                        onClick={() => setModalVisible(true)}
                        className="bg-red-600 hover:bg-red-700 border-red-600"
                    >
                        Add Staff Member
                    </Button>
                </div>

                <Card className="shadow-lg">
                    <Table
                        columns={columns}
                        dataSource={staff}
                        rowKey="user_id"
                        loading={loading}
                        pagination={{
                            pageSize: 10,
                            showSizeChanger: false,
                            showTotal: (total) => `Total ${total} staff members`,
                        }}
                    />
                </Card>

                <Modal
                    title={
                        <Space>
                            <TeamOutlined/>
                            Add New Staff Member
                        </Space>
                    }
                    open={modalVisible}
                    onCancel={() => {
                        setModalVisible(false);
                        form.resetFields();
                    }}
                    footer={null}
                    width={500}
                >
                    <Form
                        form={form}
                        layout="vertical"
                        onFinish={handleCreateStaff}
                        className="mt-6"
                    >
                        <Form.Item
                            name="email"
                            label="Email"
                            rules={[
                                {required: true, message: "Please enter email!"},
                                {type: "email", message: "Please enter valid email!"}
                            ]}
                        >
                            <Input placeholder="staff@fastair.com"/>
                        </Form.Item>

                        <Form.Item
                            name="password"
                            label="Password"
                            rules={[{required: true, message: "Please enter password!"}]}
                        >
                            <Input.Password placeholder="Password"/>
                        </Form.Item>

                        <Form.Item
                            name="role"
                            label="Role"
                            rules={[{required: true, message: "Please select role!"}]}
                        >
                            <Select placeholder="Select role">
                                <Option value={ROLES.CHECKIN}>Check-in Manager</Option>
                                <Option value={ROLES.GATE}>Gate Manager</Option>
                                <Option value={ROLES.SUPERVISOR}>Supervisor</Option>
                            </Select>
                        </Form.Item>

                        <Form.Item className="mb-0 flex justify-end">
                            <Space>
                                <Button onClick={() => {
                                    setModalVisible(false);
                                    form.resetFields();
                                }}>
                                    Cancel
                                </Button>
                                <Button type="primary" htmlType="submit" className="bg-red-600 hover:bg-red-700">
                                    Add Staff Member
                                </Button>
                            </Space>
                        </Form.Item>
                    </Form>
                </Modal>
            </motion.div>
        </div>
    );
}

export default SupervisorStaffPage;
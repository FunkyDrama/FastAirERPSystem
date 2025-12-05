import React, {useEffect, useState} from "react";
import {App, Button, Card, Form, Input, Modal, Popconfirm, Select, Space, Table, Tag, Typography} from "antd";
import {DeleteOutlined, PlusOutlined, TeamOutlined, UserOutlined} from "@ant-design/icons";
import {motion} from "framer-motion";
import api from "../utils/api.js";
import {ROLES} from "../utils/roles.js";

const {Title, Text} = Typography;
const {Option} = Select;

function SupervisorStaffPage() {
    const {message} = App.useApp();
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
                email: values.email, password: values.password, role: values.role
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

    const columns = [{
        title: "Email", dataIndex: "email", key: "email", width: 250, render: (email) => (<Space>
                <UserOutlined/>
                <span className="text-sm">{email}</span>
            </Space>),
    }, {
        title: "Role", dataIndex: "role", key: "role", width: 150, render: (role) => (<Tag color={getRoleColor(role)}>
                {role?.replace('_', ' ').toUpperCase()}
            </Tag>),
    }, {
        title: "Actions", key: "actions", width: 100, fixed: 'right', render: (_, record) => (<Popconfirm
                title="Delete Staff Member"
                description="Are you sure you want to delete this staff member?"
                onConfirm={() => handleDeleteStaff(record.user_id)}
                okText="Yes"
                cancelText="No"
            >
                <Button danger size="small" icon={<DeleteOutlined/>} block>
                    Delete
                </Button>
            </Popconfirm>),
    },];

    return (<div className="min-h-screen bg-gray-100 p-4 sm:p-6">
            <motion.div
                initial={{opacity: 0, y: 20}}
                animate={{opacity: 1, y: 0}}
                transition={{duration: 0.6}}
            >
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 sm:mb-8 gap-4">
                    <div>
                        <Title level={2} className="!mb-2 text-xl sm:text-2xl">
                            Staff Management
                        </Title>
                        <Text type="secondary" className="text-sm sm:text-base">
                            Manage staff members and their roles
                        </Text>
                    </div>
                    <Button
                        type="primary"
                        size="large"
                        icon={<PlusOutlined/>}
                        onClick={() => setModalVisible(true)}
                        className="bg-red-600 hover:bg-red-700 border-red-600 w-full sm:w-auto"
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
                        scroll={{x: 600}}
                        pagination={{
                            pageSize: 10,
                            showSizeChanger: false,
                            showTotal: (total) => `Total ${total} staff members`,
                            responsive: true,
                        }}
                    />
                </Card>

                <Modal
                    title={<Space>
                        <TeamOutlined/>
                        <span className="text-base sm:text-lg">Add New Staff Member</span>
                    </Space>}
                    open={modalVisible}
                    onCancel={() => {
                        setModalVisible(false);
                        form.resetFields();
                    }}
                    footer={null}
                    width={500}
                    className="max-w-full mx-4"
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
                            rules={[{required: true, message: "Please enter email!"}, {
                                type: "email",
                                message: "Please enter valid email!"
                            }]}
                        >
                            <Input placeholder="staff@fastair.com" size="large"/>
                        </Form.Item>

                        <Form.Item
                            name="password"
                            label="Password"
                            rules={[{required: true, message: "Please enter password!"}]}
                        >
                            <Input.Password placeholder="Password" size="large"/>
                        </Form.Item>

                        <Form.Item
                            name="role"
                            label="Role"
                            rules={[{required: true, message: "Please select role!"}]}
                        >
                            <Select placeholder="Select role" size="large">
                                <Option value={ROLES.CHECKIN}>Check-in Manager</Option>
                                <Option value={ROLES.GATE}>Gate Manager</Option>
                                <Option value={ROLES.SUPERVISOR}>Supervisor</Option>
                            </Select>
                        </Form.Item>

                        <Form.Item className="mb-0 mt-6 flex justify-end">
                            <Space>
                                <Button
                                    onClick={() => {
                                        setModalVisible(false);
                                        form.resetFields();
                                    }}
                                    size="large"
                                >
                                    Cancel
                                </Button>
                                <Button
                                    type="primary"
                                    htmlType="submit"
                                    className="bg-red-600 hover:bg-red-700"
                                    size="large"
                                >
                                    Add Staff Member
                                </Button>
                            </Space>
                        </Form.Item>
                    </Form>
                </Modal>
            </motion.div>
        </div>);
}

export default SupervisorStaffPage;
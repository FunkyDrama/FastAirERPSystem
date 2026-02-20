import React, {useEffect, useState} from "react";
import {
    Button,
    Card,
    DatePicker,
    Form,
    Input,
    message,
    Modal,
    Popconfirm,
    Select,
    Space,
    Table,
    Tag,
    Typography
} from "antd";
import {CloseCircleOutlined, PlusOutlined, RocketOutlined, SettingOutlined} from "@ant-design/icons";
import {motion} from "framer-motion";
import dayjs from "dayjs";
import api from "../utils/api.js";
import {airportLabel} from "../utils/airports";

const {Title, Text} = Typography;
const {Option} = Select;

function SupervisorFlightsPage() {
    const [loading, setLoading] = useState(false);
    const [flights, setFlights] = useState([]);
    const [airports, setAirports] = useState([]);
    const [modalVisible, setModalVisible] = useState(false);
    const [form] = Form.useForm();

    useEffect(() => {
        loadFlights();
    }, []);

    const loadFlights = async () => {
        setLoading(true);
        try {
            const res = await api.get("/supervisor/flights");
            const flightsData = res.data || [];
            setFlights(flightsData);

            const airportCodes = new Set();
            flightsData.forEach(flight => {
                if (flight.origin) airportCodes.add(flight.origin);
                if (flight.destination) airportCodes.add(flight.destination);
            });

            const uniqueAirports = Array.from(airportCodes).sort();

            if (uniqueAirports.length === 0) {
                setAirports(["KBP", "ODS", "LWO", "IEV", "DNK", "WAW", "KRK", "GDN", "BER", "MUC", "FRA", "VIE", "ZRH", "CDG", "AMS"]);
            } else {
                setAirports(uniqueAirports);
            }
        } catch (err) {
            message.error("Failed to load flights");
            setAirports(["KBP", "ODS", "LWO", "IEV", "DNK", "WAW", "KRK", "GDN", "BER", "MUC", "FRA", "VIE", "ZRH", "CDG", "AMS"]);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateFlight = async (values) => {
        try {
            const payload = {
                flight_number: values.flight_number,
                origin: values.origin,
                destination: values.destination,
                departure_time: values.departure_time.toISOString(),
                arrival_time: values.arrival_time.toISOString(),
                airplane: {
                    model: values.airplane_model, total_seats: values.total_seats
                }
            };

            await api.post("/supervisor/flights", payload);
            message.success("Flight created successfully");
            setModalVisible(false);
            form.resetFields();
            loadFlights();
        } catch (err) {
            message.error("Failed to create flight");
        }
    };

    const handleDeleteFlight = async (flightId) => {
        try {
            await api.delete(`/supervisor/flights/${flightId}`);
            message.success("Flight deleted successfully");
            loadFlights();
        } catch (err) {
            message.error("Failed to delete flight");
        }
    };

    const handleCancelFlight = async (flightId) => {
        try {
            await api.patch(`/supervisor/flights/${flightId}/cancel`);
            message.success("Flight cancelled successfully");
            loadFlights();
        } catch (err) {
            message.error("Failed to cancel flight");
        }
    };

    const columns = [{
        title: "Flight Number", dataIndex: "flight_number", key: "flight_number", width: 150, render: (text) => (<Space>
            <RocketOutlined/>
            <strong className="text-sm">{text}</strong>
        </Space>),
    }, {
        title: "Route", key: "route", width: 200, render: (_, record) => (<span className="text-sm">
                    {airportLabel(record.origin)} → {airportLabel(record.destination)}
                </span>),
    }, {
        title: "Departure",
        dataIndex: "departure_time",
        key: "departure_time",
        width: 160,
        render: (time) => <span className="text-sm">{dayjs(time).format("YYYY-MM-DD HH:mm")}</span>,
    }, {
        title: "Arrival",
        dataIndex: "arrival_time",
        key: "arrival_time",
        width: 160,
        render: (time) => <span className="text-sm">{dayjs(time).format("YYYY-MM-DD HH:mm")}</span>,
    }, {
        title: "Status", dataIndex: "status", key: "status", width: 120, render: (status) => {
            const s = status?.toLowerCase();
            const color = s === "scheduled" ? "green" : s === "canceled" ? "red" : s === "completed" ? "blue" : "default";
            return <Tag color={color}>{status?.toUpperCase()}</Tag>;
        },
    }, {
        title: "Actions", key: "actions", width: 120, fixed: 'right', render: (_, record) => {
            const isScheduled = record.status?.toLowerCase() === "scheduled";
            return (
                <Popconfirm
                    title="Cancel Flight"
                    description="Are you sure you want to cancel this flight? This action cannot be undone."
                    onConfirm={() => handleCancelFlight(record.flight_id)}
                    okText="Yes, cancel"
                    cancelText="No"
                    disabled={!isScheduled}
                >
                    <Button
                        danger
                        size="small"
                        icon={<CloseCircleOutlined/>}
                        block
                        disabled={!isScheduled}
                    >
                        Cancel
                    </Button>
                </Popconfirm>
            );
        },
    },];

    const renderAirportOption = (code) => {
        const airportCode = typeof code === 'string' ? code : code.code;
        return (<Option key={airportCode} value={airportCode}>
            {airportLabel(airportCode)}
        </Option>);
    };

    return (<div className="min-h-screen bg-gray-100 p-4 sm:p-6">
        <motion.div
            initial={{opacity: 0, y: 20}}
            animate={{opacity: 1, y: 0}}
            transition={{duration: 0.6}}
        >
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 sm:mb-8 gap-4">
                <div>
                    <Title level={2} className="!mb-2 text-xl sm:text-2xl">
                        Flight Management
                    </Title>
                    <Text type="secondary" className="text-sm sm:text-base">
                        Create and manage flight schedules
                    </Text>
                </div>
                <Button
                    type="primary"
                    size="large"
                    icon={<PlusOutlined/>}
                    onClick={() => setModalVisible(true)}
                    className="bg-red-600 hover:bg-red-700 border-red-600 w-full sm:w-auto"
                >
                    Create Flight
                </Button>
            </div>

            <Card className="shadow-lg">
                <Table
                    columns={columns}
                    dataSource={flights}
                    rowKey="flight_id"
                    loading={loading}
                    scroll={{x: 1000}}
                    pagination={{
                        pageSize: 10,
                        showSizeChanger: false,
                        showTotal: (total) => `Total ${total} flights`,
                        responsive: true,
                    }}
                />
            </Card>

            <Modal
                title={<Space>
                    <SettingOutlined/>
                    <span className="text-base sm:text-lg">Create New Flight</span>
                </Space>}
                open={modalVisible}
                onCancel={() => {
                    setModalVisible(false);
                    form.resetFields();
                }}
                footer={null}
                width={600}
                className="max-w-full mx-4"
            >
                <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleCreateFlight}
                    className="mt-6"
                >
                    <Form.Item
                        name="flight_number"
                        label="Flight Number"
                        rules={[{required: true, message: "Please enter flight number!"}]}
                    >
                        <Input placeholder="e.g., FA001" size="large"/>
                    </Form.Item>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <Form.Item
                            name="origin"
                            label="Origin"
                            rules={[{required: true, message: "Please select origin!"}, ({getFieldValue}) => ({
                                validator(_, value) {
                                    if (!value || getFieldValue('destination') !== value) {
                                        return Promise.resolve();
                                    }
                                    return Promise.reject(new Error('Origin and destination cannot be the same!'));
                                },
                            }),]}
                        >
                            <Select
                                placeholder="Select origin"
                                showSearch
                                size="large"
                                filterOption={(input, option) => option.children.toLowerCase().includes(input.toLowerCase())}
                            >
                                {airports.map(renderAirportOption)}
                            </Select>
                        </Form.Item>

                        <Form.Item
                            name="destination"
                            label="Destination"
                            rules={[{required: true, message: "Please select destination!"}, ({getFieldValue}) => ({
                                validator(_, value) {
                                    if (!value || getFieldValue('origin') !== value) {
                                        return Promise.resolve();
                                    }
                                    return Promise.reject(new Error('Destination and origin cannot be the same!'));
                                },
                            }),]}
                        >
                            <Select
                                placeholder="Select destination"
                                showSearch
                                size="large"
                                filterOption={(input, option) => option.children.toLowerCase().includes(input.toLowerCase())}
                            >
                                {airports.map(renderAirportOption)}
                            </Select>
                        </Form.Item>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <Form.Item
                            name="departure_time"
                            label="Departure Time"
                            rules={[{required: true, message: "Please select departure time!"}]}
                        >
                            <DatePicker
                                showTime
                                className="w-full"
                                format="YYYY-MM-DD HH:mm"
                                size="large"
                            />
                        </Form.Item>

                        <Form.Item
                            name="arrival_time"
                            label="Arrival Time"
                            rules={[{
                                required: true, message: "Please select arrival time!"
                            }, ({getFieldValue}) => ({
                                validator(_, value) {
                                    if (!value || !getFieldValue('departure_time')) {
                                        return Promise.resolve();
                                    }
                                    if (value.isAfter(getFieldValue('departure_time'))) {
                                        return Promise.resolve();
                                    }
                                    return Promise.reject(new Error('Arrival time must be after departure time!'));
                                },
                            }),]}
                        >
                            <DatePicker
                                showTime
                                className="w-full"
                                format="YYYY-MM-DD HH:mm"
                                size="large"
                            />
                        </Form.Item>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <Form.Item
                            name="airplane_model"
                            label="Airplane Model"
                            rules={[{required: true, message: "Please enter airplane model!"}]}
                        >
                            <Input placeholder="e.g., Boeing 737" size="large"/>
                        </Form.Item>

                        <Form.Item
                            name="total_seats"
                            label="Total Seats"
                            rules={[{required: true, message: "Please enter total seats!"}, {
                                type: 'number', min: 1, message: "Must have at least 1 seat!"
                            }]}
                            getValueFromEvent={(e) => {
                                const value = parseInt(e.target.value);
                                return isNaN(value) ? null : value;
                            }}
                        >
                            <Input type="number" placeholder="e.g., 180" size="large"/>
                        </Form.Item>
                    </div>

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
                                Create Flight
                            </Button>
                        </Space>
                    </Form.Item>
                </Form>
            </Modal>
        </motion.div>
    </div>);
}

export default SupervisorFlightsPage;
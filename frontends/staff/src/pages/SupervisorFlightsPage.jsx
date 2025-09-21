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
import {DeleteOutlined, PlusOutlined, RocketOutlined, SettingOutlined} from "@ant-design/icons";
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
                setAirports([
                    "KBP", "ODS", "LWO", "IEV", "DNK",
                    "WAW", "KRK", "GDN", "BER", "MUC",
                    "FRA", "VIE", "ZRH", "CDG", "AMS"
                ]);
            } else {
                setAirports(uniqueAirports);
            }
        } catch (err) {
            message.error("Failed to load flights");
            setAirports([
                "KBP", "ODS", "LWO", "IEV", "DNK",
                "WAW", "KRK", "GDN", "BER", "MUC",
                "FRA", "VIE", "ZRH", "CDG", "AMS"
            ]);
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
                    model: values.airplane_model,
                    total_seats: values.total_seats
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

    const columns = [
        {
            title: "Flight Number",
            dataIndex: "flight_number",
            key: "flight_number",
            render: (text) => (
                <Space>
                    <RocketOutlined/>
                    <strong>{text}</strong>
                </Space>
            ),
        },
        {
            title: "Route",
            key: "route",
            render: (_, record) => (
                <span>
                    {airportLabel(record.origin)} → {airportLabel(record.destination)}
                </span>
            ),
        },
        {
            title: "Departure",
            dataIndex: "departure_time",
            key: "departure_time",
            render: (time) => dayjs(time).format("YYYY-MM-DD HH:mm"),
        },
        {
            title: "Arrival",
            dataIndex: "arrival_time",
            key: "arrival_time",
            render: (time) => dayjs(time).format("YYYY-MM-DD HH:mm"),
        },
        {
            title: "Status",
            dataIndex: "status",
            key: "status",
            render: (status) => {
                const color = status === "SCHEDULED" ? "green" :
                    status === "CANCELED" ? "red" : "orange";
                return <Tag color={color}>{status}</Tag>;
            },
        },
        {
            title: "Actions",
            key: "actions",
            render: (_, record) => (
                <Popconfirm
                    title="Delete Flight"
                    description="Are you sure you want to delete this flight?"
                    onConfirm={() => handleDeleteFlight(record.flight_id)}
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

    const renderAirportOption = (code) => {
        const airportCode = typeof code === 'string' ? code : code.code;
        return (
            <Option key={airportCode} value={airportCode}>
                {airportLabel(airportCode)}
            </Option>
        );
    };

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
                            Flight Management
                        </Title>
                        <Text type="secondary" className="text-base">
                            Create and manage flight schedules
                        </Text>
                    </div>
                    <Button
                        type="primary"
                        size="large"
                        icon={<PlusOutlined/>}
                        onClick={() => setModalVisible(true)}
                        className="bg-red-600 hover:bg-red-700 border-red-600"
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
                        pagination={{
                            pageSize: 10,
                            showSizeChanger: false,
                            showTotal: (total) => `Total ${total} flights`,
                        }}
                    />
                </Card>

                <Modal
                    title={
                        <Space>
                            <SettingOutlined/>
                            Create New Flight
                        </Space>
                    }
                    open={modalVisible}
                    onCancel={() => {
                        setModalVisible(false);
                        form.resetFields();
                    }}
                    footer={null}
                    width={600}
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
                            <Input placeholder="e.g., FA001"/>
                        </Form.Item>

                        <div className="grid grid-cols-2 gap-4">
                            <Form.Item
                                name="origin"
                                label="Origin"
                                rules={[
                                    {required: true, message: "Please select origin!"},
                                    ({getFieldValue}) => ({
                                        validator(_, value) {
                                            if (!value || getFieldValue('destination') !== value) {
                                                return Promise.resolve();
                                            }
                                            return Promise.reject(new Error('Origin and destination cannot be the same!'));
                                        },
                                    }),
                                ]}
                            >
                                <Select
                                    placeholder="Select origin"
                                    showSearch
                                    filterOption={(input, option) =>
                                        option.children.toLowerCase().includes(input.toLowerCase())
                                    }
                                >
                                    {airports.map(renderAirportOption)}
                                </Select>
                            </Form.Item>

                            <Form.Item
                                name="destination"
                                label="Destination"
                                rules={[
                                    {required: true, message: "Please select destination!"},
                                    ({getFieldValue}) => ({
                                        validator(_, value) {
                                            if (!value || getFieldValue('origin') !== value) {
                                                return Promise.resolve();
                                            }
                                            return Promise.reject(new Error('Destination and origin cannot be the same!'));
                                        },
                                    }),
                                ]}
                            >
                                <Select
                                    placeholder="Select destination"
                                    showSearch
                                    filterOption={(input, option) =>
                                        option.children.toLowerCase().includes(input.toLowerCase())
                                    }
                                >
                                    {airports.map(renderAirportOption)}
                                </Select>
                            </Form.Item>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <Form.Item
                                name="departure_time"
                                label="Departure Time"
                                rules={[{required: true, message: "Please select departure time!"}]}
                            >
                                <DatePicker
                                    showTime
                                    className="w-full"
                                    format="YYYY-MM-DD HH:mm"
                                />
                            </Form.Item>

                            <Form.Item
                                name="arrival_time"
                                label="Arrival Time"
                                rules={[
                                    {required: true, message: "Please select arrival time!"},
                                    ({getFieldValue}) => ({
                                        validator(_, value) {
                                            if (!value || !getFieldValue('departure_time')) {
                                                return Promise.resolve();
                                            }
                                            if (value.isAfter(getFieldValue('departure_time'))) {
                                                return Promise.resolve();
                                            }
                                            return Promise.reject(new Error('Arrival time must be after departure time!'));
                                        },
                                    }),
                                ]}
                            >
                                <DatePicker
                                    showTime
                                    className="w-full"
                                    format="YYYY-MM-DD HH:mm"
                                />
                            </Form.Item>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <Form.Item
                                name="airplane_model"
                                label="Airplane Model"
                                rules={[{required: true, message: "Please enter airplane model!"}]}
                            >
                                <Input placeholder="e.g., Boeing 737"/>
                            </Form.Item>

                            <Form.Item
                                name="total_seats"
                                label="Total Seats"
                                rules={[
                                    {required: true, message: "Please enter total seats!"},
                                    {type: 'number', min: 1, message: "Must have at least 1 seat!"}
                                ]}
                                getValueFromEvent={(e) => {
                                    const value = parseInt(e.target.value);
                                    return isNaN(value) ? null : value;
                                }}
                            >
                                <Input type="number" placeholder="e.g., 180"/>
                            </Form.Item>
                        </div>

                        <Form.Item className="mb-0 flex justify-end">
                            <Space>
                                <Button onClick={() => {
                                    setModalVisible(false);
                                    form.resetFields();
                                }}>
                                    Cancel
                                </Button>
                                <Button type="primary" htmlType="submit" className="bg-red-600 hover:bg-red-700">
                                    Create Flight
                                </Button>
                            </Space>
                        </Form.Item>
                    </Form>
                </Modal>
            </motion.div>
        </div>
    );
}

export default SupervisorFlightsPage;
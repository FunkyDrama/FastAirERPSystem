import React, {useState} from "react";
import {Button, Card, Col, Input, message, Row, Space, Table, Tag, Typography} from "antd";
import {ControlOutlined, UserOutlined} from "@ant-design/icons";
import {motion} from "framer-motion";
import api from "../utils/api.js";

const {Title, Text} = Typography;
const {Search} = Input;

function GatePage() {
    const [loading, setLoading] = useState(false);
    const [passengers, setPassengers] = useState([]);
    const [flightId, setFlightId] = useState("");

    const loadPassengers = async (flightNumber) => {
        if (!flightNumber) return;
        setLoading(true);
        try {
            const res = await api.get(`/gate/flights/${flightNumber}/passengers/boarding`);
            setPassengers(res.data.passengers || []);
        } catch (err) {
            message.error("Failed to load passengers");
        } finally {
            setLoading(false);
        }
    };

    const handleBoarding = async (ticketNumber) => {
        try {
            await api.post(`/gate/boarding/${ticketNumber}`);
            message.success("Passenger boarded successfully");
            await loadPassengers(flightId);
        } catch (err) {
            message.error("Failed to board passenger");
        }
    };

    const columns = [
        {
            title: "Passenger Name",
            dataIndex: "passenger_name",
            key: "passenger_name",
            render: (text) => (
                <Space>
                    <UserOutlined/>
                    {text}
                </Space>
            ),
        },
        {
            title: "Ticket Number",
            dataIndex: "ticket_number",
            key: "ticket_number",
        },
        {
            title: "Seat",
            dataIndex: "seat_number",
            key: "seat_number",
            render: (seat) => <Tag color="blue">{seat}</Tag>,
        },
        {
            title: "Seat Type",
            dataIndex: "seat_type",
            key: "seat_type",
        },
        {
            title: "Actions",
            key: "actions",
            render: (_, record) => (
                <Button
                    type="primary"
                    size="small"
                    onClick={() => handleBoarding(record.ticket_number)}
                >
                    Board Passenger
                </Button>
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
                <Title level={2} className="!mb-8">
                    Gate Management
                </Title>

                <Row gutter={[24, 24]}>
                    <Col xs={24} lg={8}>
                        <Card className="h-full">
                            <div className="text-center">
                                <ControlOutlined className="text-4xl text-blue-500 mb-4"/>
                                <Title level={4}>Boarding Control</Title>
                                <Text type="secondary" className="block mb-6">
                                    Manage passenger boarding process
                                </Text>
                                <div className="space-y-2">
                                    <div className="bg-blue-100 p-3 rounded">
                                        <Text strong>Ready for Boarding</Text>
                                        <div className="text-2xl font-bold text-blue-600">
                                            {passengers.length}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </Card>
                    </Col>
                    
                    <Col xs={24} lg={16}>
                        <Card>
                            <Title level={4} className="!mb-4">
                                Checked-in Passengers
                            </Title>
                            <div className="mb-6">
                                <Search
                                    placeholder="Enter flight number"
                                    enterButton="Load Passengers"
                                    size="large"
                                    value={flightId}
                                    onChange={(e) => setFlightId(e.target.value)}
                                    onSearch={loadPassengers}
                                    loading={loading}
                                />
                            </div>

                            <Table
                                columns={columns}
                                dataSource={passengers}
                                rowKey="ticket_number"
                                loading={loading}
                                pagination={{
                                    pageSize: 10,
                                    showSizeChanger: false,
                                }}
                            />
                        </Card>
                    </Col>
                </Row>
            </motion.div>
        </div>
    );
}

export default GatePage;
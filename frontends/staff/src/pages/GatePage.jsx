import React, {useState} from "react";
import {App, Button, Card, Col, Input, Row, Space, Table, Tag, Typography} from "antd";
import {ControlOutlined, UserOutlined} from "@ant-design/icons";
import {motion} from "framer-motion";
import api from "../utils/api.js";

const {Title, Text} = Typography;
const {Search} = Input;

function GatePage() {
    const {message} = App.useApp();
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

    const columns = [{
        title: "Passenger Name",
        dataIndex: "passenger_name",
        key: "passenger_name",
        width: 200,
        render: (text) => (<Space>
                <UserOutlined/>
                <span className="text-sm">{text}</span>
            </Space>),
    }, {
        title: "Ticket Number",
        dataIndex: "ticket_number",
        key: "ticket_number",
        width: 150,
        render: (text) => <span className="text-sm">{text}</span>,
    }, {
        title: "Seat",
        dataIndex: "seat_number",
        key: "seat_number",
        width: 100,
        render: (seat) => <Tag color="blue">{seat}</Tag>,
    }, {
        title: "Seat Type",
        dataIndex: "seat_type",
        key: "seat_type",
        width: 120,
        render: (text) => <span className="text-sm">{text}</span>,
    }, {
        title: "Actions", key: "actions", width: 120, fixed: 'right', render: (_, record) => (<Button
                type="primary"
                size="small"
                onClick={() => handleBoarding(record.ticket_number)}
                block
            >
                Board Passenger
            </Button>),
    },];

    return (<div className="min-h-screen bg-gray-100 p-4 sm:p-6">
            <motion.div
                initial={{opacity: 0, y: 20}}
                animate={{opacity: 1, y: 0}}
                transition={{duration: 0.6}}
            >
                <Title level={2} className="!mb-6 sm:!mb-8 text-xl sm:text-2xl">
                    Gate Management
                </Title>

                <Row gutter={[16, 16]}>
                    <Col xs={24} lg={8}>
                        <Card className="h-full">
                            <div className="text-center">
                                <ControlOutlined className="text-3xl sm:text-4xl text-blue-500 mb-4"/>
                                <Title level={4} className="text-base sm:text-lg">
                                    Boarding Control
                                </Title>
                                <Text type="secondary" className="block mb-4 sm:mb-6 text-sm">
                                    Manage passenger boarding process
                                </Text>
                                <div className="space-y-2">
                                    <div className="bg-blue-100 p-3 rounded">
                                        <Text strong className="text-sm">Ready for Boarding</Text>
                                        <div className="text-xl sm:text-2xl font-bold text-blue-600">
                                            {passengers.length}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </Card>
                    </Col>

                    <Col xs={24} lg={16}>
                        <Card>
                            <Title level={4} className="!mb-4 text-base sm:text-lg">
                                Checked-in Passengers
                            </Title>
                            <div className="mb-4 sm:mb-6">
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
                                scroll={{x: 800}}
                                pagination={{
                                    pageSize: 10, showSizeChanger: false, responsive: true,
                                }}
                                locale={{
                                    emptyText: "No passengers loaded. Enter a flight number above."
                                }}
                            />
                        </Card>
                    </Col>
                </Row>
            </motion.div>
        </div>);
}

export default GatePage;
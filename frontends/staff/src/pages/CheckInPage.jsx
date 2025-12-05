import React, {useState} from "react";
import {App, Button, Card, Col, Input, Modal, Row, Space, Spin, Table, Tag, Typography} from "antd";
import {CameraOutlined, CloseOutlined, ScanOutlined, UserOutlined} from "@ant-design/icons";
import {motion} from "framer-motion";
import {Scanner} from "@yudiel/react-qr-scanner";
import api from "../utils/api.js";

const {Title, Text} = Typography;
const {Search} = Input;

function CheckInPage() {
    const {message} = App.useApp();
    const [loading, setLoading] = useState(false);
    const [passengers, setPassengers] = useState([]);
    const [flightId, setFlightId] = useState("");
    const [scanModalVisible, setScanModalVisible] = useState(false);
    const [manualInput, setManualInput] = useState(false);
    const [ticketNumber, setTicketNumber] = useState("");
    const [scanning, setScanning] = useState(false);
    const [cameraError, setCameraError] = useState(false);
    const [isPaused, setIsPaused] = useState(false);

    const loadPassengers = async (id) => {
        if (!id) return;
        setLoading(true);
        try {
            const res = await api.get(`/checkin/flights/${id}/passengers`);
            setPassengers(res.data.passengers || []);
        } catch (err) {
            message.error("Failed to load passengers");
        } finally {
            setLoading(false);
        }
    };

    const handleCheckIn = async (ticketNum) => {
        try {
            await api.post(`/checkin/${ticketNum}`);
            message.success("Passenger checked in successfully");
            await loadPassengers(flightId);
        } catch (err) {
            message.error("Failed to check in passenger");
        }
    };

    const processScanResult = async (scanData) => {
        if (!scanData || scanning) return;

        setScanning(true);
        setIsPaused(true);

        try {
            const res = await api.post("/checkin/scan", {
                booking_id: scanData.booking_id, ticket_number: scanData.ticket_number
            });
            message.success(`✅ Checked in: ${res.data.passenger_name}`);
            setScanModalVisible(false);
            setTicketNumber("");
            setManualInput(false);
            setIsPaused(false);
            await loadPassengers(flightId);
        } catch (err) {
            console.error("QR scan error:", err);
            message.error("Failed to process QR scan. Please check the ticket.");
            setIsPaused(false);
        } finally {
            setScanning(false);
        }
    };

    const handleScan = (result) => {
        if (result && result.length > 0 && !scanning) {
            const qrText = result[0].rawValue;

            try {
                const data = JSON.parse(qrText);

                if (!data.ticket_number || !data.booking_id) {
                    message.error("Invalid QR code - missing required information");
                    return;
                }

                if (data.passenger_name) {
                    message.info(`Scanning ticket for: ${data.passenger_name}`);
                }

                processScanResult(data);
            } catch (e) {
                message.error("Invalid QR code format. Please use a valid ticket QR code.");
                console.error("QR parsing error:", e);

            }
        }
    };

    const handleError = (error) => {
        if (!cameraError && error) {
            setCameraError(true);
            console.error("QR Scanner Error:", error);
            message.error("Camera access error. Please check permissions.");
        }
    };

    const handleManualSubmit = () => {
        if (ticketNumber) {
            handleCheckIn(ticketNumber);
            setScanModalVisible(false);
            setTicketNumber("");
            setManualInput(false);
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
        render: (seat) => seat ? <Tag color="blue">{seat}</Tag> : <Tag>Not Assigned</Tag>,
    }, {
        title: "Seat Type",
        dataIndex: "seat_type",
        key: "seat_type",
        width: 120,
        render: (text) => <span className="text-sm">{text}</span>,
    }, {
        title: "Status",
        dataIndex: "checked_in",
        key: "checked_in",
        width: 120,
        render: (checkedIn) => (checkedIn ? <Tag color="green">Checked In</Tag> : <Tag color="orange">Pending</Tag>),
    }, {
        title: "Actions",
        key: "actions",
        width: 120,
        fixed: 'right',
        render: (_, record) => (!record.checked_in && (<Button
                    type="primary"
                    size="small"
                    onClick={() => handleCheckIn(record.ticket_number)}
                    block
                >
                    Check In
                </Button>)),
    },];

    return (<div className="min-h-screen bg-gray-100 p-4 sm:p-6">
            <motion.div
                initial={{opacity: 0, y: 20}}
                animate={{opacity: 1, y: 0}}
                transition={{duration: 0.6}}
            >
                <Title level={2} className="!mb-6 sm:!mb-8 text-xl sm:text-2xl">
                    Check-in Management
                </Title>

                <Row gutter={[16, 16]}>
                    <Col xs={24} lg={8}>
                        <Card className="h-full">
                            <div className="text-center">
                                <ScanOutlined className="text-3xl sm:text-4xl text-green-500 mb-4"/>
                                <Title level={4} className="text-base sm:text-lg">QR Code Scanner</Title>
                                <Text type="secondary" className="block mb-4 sm:mb-6 text-sm">
                                    Scan passenger tickets for quick check-in
                                </Text>
                                <Button
                                    type="primary"
                                    size="large"
                                    icon={<ScanOutlined/>}
                                    onClick={() => {
                                        setScanModalVisible(true);
                                        setCameraError(false);
                                        setIsPaused(false);
                                    }}
                                    block
                                >
                                    Start QR Scanner
                                </Button>
                            </div>
                        </Card>
                    </Col>

                    <Col xs={24} lg={16}>
                        <Card>
                            <Title level={4} className="!mb-4 text-base sm:text-lg">
                                Flight Passengers
                            </Title>
                            <div className="mb-4 sm:mb-6">
                                <Search
                                    placeholder="Enter flight number (e.g., FA001)"
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
                                scroll={{x: 900}}
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

                <Modal
                    title={<Space>
                        <CameraOutlined/>
                        <span className="text-base sm:text-lg">QR Code Scanner</span>
                    </Space>}
                    open={scanModalVisible}
                    onCancel={() => {
                        setScanModalVisible(false);
                        setTicketNumber("");
                        setManualInput(false);
                        setCameraError(false);
                        setIsPaused(true);
                    }}
                    footer={null}
                    width={600}
                    className="max-w-full mx-4"
                    centered
                >
                    <div className="py-4">
                        {!manualInput ? (<>
                                <div className="relative bg-black rounded-lg overflow-hidden mb-4">
                                    {scanning && (<div
                                            className="absolute inset-0 bg-black/50 flex items-center justify-center z-10">
                                            <Spin size="large" tip="Processing..."/>
                                        </div>)}

                                    <Scanner
                                        onScan={handleScan}
                                        onError={handleError}
                                        paused={isPaused}
                                        styles={{
                                            container: {
                                                width: '100%', height: '300px', position: 'relative'
                                            }, video: {
                                                width: '100%', height: '100%', objectFit: 'cover'
                                            }
                                        }}
                                        components={{
                                            audio: false, finder: true, tracker: true
                                        }}
                                        options={{
                                            delayBetweenScanAttempts: 500, delayBetweenScanSuccess: 500
                                        }}
                                    />
                                </div>

                                {cameraError && (
                                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                                        <Text type="warning" className="text-sm">
                                            Camera access may be restricted. Please check your browser permissions.
                                        </Text>
                                    </div>)}

                                <div className="text-center">
                                    <Text type="secondary" className="block mb-2 text-sm">
                                        Position the QR code within the frame
                                    </Text>
                                    <Button
                                        type="link"
                                        onClick={() => setManualInput(true)}
                                        icon={<CloseOutlined/>}
                                        className="text-sm"
                                    >
                                        Enter ticket number manually
                                    </Button>
                                </div>
                            </>) : (<div>
                                <Text className="block mb-4 text-sm sm:text-base">
                                    Enter the ticket number manually:
                                </Text>
                                <div className="flex flex-col sm:flex-row gap-2">
                                    <Input
                                        placeholder="Ticket Number (e.g., TK-123456)"
                                        value={ticketNumber}
                                        onChange={(e) => setTicketNumber(e.target.value)}
                                        onPressEnter={handleManualSubmit}
                                        disabled={scanning}
                                        size="large"
                                        className="flex-1"
                                    />
                                    <Button
                                        type="primary"
                                        onClick={handleManualSubmit}
                                        loading={scanning}
                                        size="large"
                                        className="w-full sm:w-auto"
                                    >
                                        Check In
                                    </Button>
                                </div>

                                <div className="text-center mt-4">
                                    <Button
                                        type="link"
                                        onClick={() => {
                                            setManualInput(false);
                                            setTicketNumber("");
                                        }}
                                        icon={<CameraOutlined/>}
                                        className="text-sm"
                                    >
                                        Back to camera scanner
                                    </Button>
                                </div>
                            </div>)}
                    </div>
                </Modal>
            </motion.div>
        </div>);
}

export default CheckInPage;
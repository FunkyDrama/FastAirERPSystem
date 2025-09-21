import React, {useState} from "react";
import {Button, Card, Col, Input, message, Modal, Row, Space, Spin, Table, Tag, Typography} from "antd";
import {CameraOutlined, CloseOutlined, ScanOutlined, UserOutlined} from "@ant-design/icons";
import {motion} from "framer-motion";
import {Scanner} from "@yudiel/react-qr-scanner";
import api from "../utils/api.js";

const {Title, Text} = Typography;
const {Search} = Input;

function CheckInPage() {
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
                booking_id: scanData.booking_id,
                ticket_number: scanData.ticket_number
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
                return;
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
            render: (seat) => seat ? <Tag color="blue">{seat}</Tag> : <Tag>Not Assigned</Tag>,
        },
        {
            title: "Seat Type",
            dataIndex: "seat_type",
            key: "seat_type",
        },
        {
            title: "Status",
            dataIndex: "checked_in",
            key: "checked_in",
            render: (checkedIn) => (
                checkedIn ?
                    <Tag color="green">Checked In</Tag> :
                    <Tag color="orange">Pending</Tag>
            ),
        },
        {
            title: "Actions",
            key: "actions",
            render: (_, record) => (
                !record.checked_in && (
                    <Button
                        type="primary"
                        size="small"
                        onClick={() => handleCheckIn(record.ticket_number)}
                    >
                        Check In
                    </Button>
                )
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
                    Check-in Management
                </Title>

                <Row gutter={[24, 24]}>
                    <Col xs={24} lg={8}>
                        <Card className="h-full">
                            <div className="text-center">
                                <ScanOutlined className="text-4xl text-green-500 mb-4"/>
                                <Title level={4}>QR Code Scanner</Title>
                                <Text type="secondary" className="block mb-6">
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
                                    className="w-full"
                                >
                                    Start QR Scanner
                                </Button>
                            </div>
                        </Card>
                    </Col>

                    <Col xs={24} lg={16}>
                        <Card>
                            <Title level={4} className="!mb-4">
                                Flight Passengers
                            </Title>
                            <div className="mb-6">
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
                                pagination={{
                                    pageSize: 10,
                                    showSizeChanger: false,
                                }}
                                locale={{
                                    emptyText: "No passengers loaded. Enter a flight number above."
                                }}
                            />
                        </Card>
                    </Col>
                </Row>

                <Modal
                    title={
                        <Space>
                            <CameraOutlined/>
                            QR Code Scanner
                        </Space>
                    }
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
                    centered
                >
                    <div className="py-4">
                        {!manualInput ? (
                            <>
                                <div className="relative bg-black rounded-lg overflow-hidden mb-4">
                                    {scanning && (
                                        <div
                                            className="absolute inset-0 bg-black/50 flex items-center justify-center z-10">
                                            <Spin size="large" tip="Processing..."/>
                                        </div>
                                    )}

                                    <Scanner
                                        onScan={handleScan}
                                        onError={handleError}
                                        paused={isPaused}
                                        styles={{
                                            container: {
                                                width: '100%',
                                                height: '400px',
                                                position: 'relative'
                                            },
                                            video: {
                                                width: '100%',
                                                height: '100%',
                                                objectFit: 'cover'
                                            }
                                        }}
                                        components={{
                                            audio: false,
                                            finder: true,
                                            tracker: true
                                        }}
                                        options={{
                                            delayBetweenScanAttempts: 500,
                                            delayBetweenScanSuccess: 500
                                        }}
                                    />
                                </div>

                                {cameraError && (
                                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                                        <Text type="warning">
                                            Camera access may be restricted. Please check your browser permissions.
                                        </Text>
                                    </div>
                                )}

                                <div className="text-center">
                                    <Text type="secondary" className="block mb-2">
                                        Position the QR code within the frame
                                    </Text>
                                    <Button
                                        type="link"
                                        onClick={() => setManualInput(true)}
                                        icon={<CloseOutlined/>}
                                    >
                                        Enter ticket number manually
                                    </Button>
                                </div>
                            </>
                        ) : (
                            <div>
                                <Text className="block mb-4">
                                    Enter the ticket number manually:
                                </Text>
                                <Space.Compact style={{width: '100%'}} size="large">
                                    <Input
                                        placeholder="Ticket Number (e.g., TK-123456)"
                                        value={ticketNumber}
                                        onChange={(e) => setTicketNumber(e.target.value)}
                                        onPressEnter={handleManualSubmit}
                                        disabled={scanning}
                                    />
                                    <Button
                                        type="primary"
                                        onClick={handleManualSubmit}
                                        loading={scanning}
                                    >
                                        Check In
                                    </Button>
                                </Space.Compact>

                                <div className="text-center mt-4">
                                    <Button
                                        type="link"
                                        onClick={() => {
                                            setManualInput(false);
                                            setTicketNumber("");
                                        }}
                                        icon={<CameraOutlined/>}
                                    >
                                        Back to camera scanner
                                    </Button>
                                </div>
                            </div>
                        )}
                    </div>
                </Modal>
            </motion.div>
        </div>
    );
}

export default CheckInPage;
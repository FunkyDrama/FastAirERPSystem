import React, {useEffect, useState} from "react";
import {App, Card, Col, Row, Select, Statistic, Typography} from "antd";
import {DollarOutlined, RiseOutlined, SearchOutlined} from "@ant-design/icons";
import {motion} from "framer-motion";
import api from "../utils/api.js";

const {Title, Text} = Typography;
const {Option} = Select;

function SupervisorRevenuePage() {
    const {message} = App.useApp();
    const [loading, setLoading] = useState(false);
    const [totalRevenue, setTotalRevenue] = useState(0);
    const [flightRevenue, setFlightRevenue] = useState(0);
    const [selectedFlightId, setSelectedFlightId] = useState(null);
    const [flights, setFlights] = useState([]);

    useEffect(() => {
        loadTotalRevenue();
        loadFlights();
    }, []);

    const loadTotalRevenue = async () => {
        setLoading(true);
        try {
            const res = await api.get("/supervisor/revenue");
            setTotalRevenue(res.data.revenue || 0);
        } catch (err) {
            message.error("Failed to load total revenue");
        } finally {
            setLoading(false);
        }
    };

    const loadFlights = async () => {
        try {
            const res = await api.get("/supervisor/flights");
            setFlights(res.data || []);
        } catch (err) {
            message.error("Failed to load flights");
        }
    };

    const loadFlightRevenue = async (flightId) => {
        if (!flightId) return;
        setLoading(true);
        try {
            const res = await api.get(`/supervisor/revenue?flight_id=${flightId}`);
            setFlightRevenue(res.data.revenue || 0);
        } catch (err) {
            message.error("Failed to load flight revenue");
        } finally {
            setLoading(false);
        }
    };

    const handleFlightSelect = (flightId) => {
        if (!flightId) {
            setSelectedFlightId(null);
            setFlightRevenue(0);
            return;
        }

        setSelectedFlightId(flightId);
        loadFlightRevenue(flightId);
    };

    const containerVariants = {
        hidden: {opacity: 0}, visible: {
            opacity: 1, transition: {staggerChildren: 0.1}
        }
    };

    const cardVariants = {
        hidden: {opacity: 0, y: 20}, visible: {
            opacity: 1, y: 0, transition: {duration: 0.5}
        }
    };

    return (<div className="min-h-screen bg-gray-100 p-4 sm:p-6">
            <motion.div
                initial={{opacity: 0, y: 20}}
                animate={{opacity: 1, y: 0}}
                transition={{duration: 0.6}}
            >
                <div className="mb-6 sm:mb-8">
                    <Title level={2} className="!mb-2 text-xl sm:text-2xl">
                        Revenue Analytics
                    </Title>
                    <Text type="secondary" className="text-sm sm:text-base">
                        Monitor financial performance and flight revenue
                    </Text>
                </div>

                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                >
                    <Row gutter={[16, 16]}>
                        <Col xs={24} sm={12} lg={8}>
                            <motion.div variants={cardVariants}>
                                <Card className="h-full shadow-lg">
                                    <div className="text-center">
                                        <div className="mb-4">
                                            <DollarOutlined className="text-3xl sm:text-4xl text-green-500"/>
                                        </div>
                                        <Statistic
                                            title={<span className="text-sm sm:text-base">Total Revenue</span>}
                                            value={totalRevenue}
                                            precision={2}
                                            styles={{
                                                value: {
                                                    color: '#3f8600', fontSize: '1.5rem'
                                                }
                                            }}
                                            prefix="$"
                                            loading={loading}
                                        />
                                        <Text type="secondary" className="text-xs sm:text-sm">
                                            All-time revenue
                                        </Text>
                                    </div>
                                </Card>
                            </motion.div>
                        </Col>

                        <Col xs={24} sm={12} lg={8}>
                            <motion.div variants={cardVariants}>
                                <Card className="h-full shadow-lg">
                                    <div className="text-center">
                                        <div className="mb-4">
                                            <SearchOutlined className="text-3xl sm:text-4xl text-blue-500"/>
                                        </div>
                                        <Title level={4} className="!mb-4 text-base sm:text-lg">
                                            Flight Revenue
                                        </Title>
                                        <Select
                                            showSearch
                                            placeholder="Select flight"
                                            className="w-full mb-4"
                                            size="large"
                                            value={selectedFlightId}
                                            onChange={handleFlightSelect}
                                            optionFilterProp="children"
                                            allowClear
                                            filterOption={(input, option) => String(option?.children ?? '').toLowerCase().includes(input.toLowerCase())}
                                        >
                                            {flights.map(f => (<Option key={f.flight_id} value={f.flight_id}>
                                                    {f.flight_number} - {f.origin} → {f.destination}
                                                </Option>))}
                                        </Select>
                                        {!selectedFlightId && (<Text type="secondary" className="text-xs sm:text-sm">
                                                Select a flight to view its revenue
                                            </Text>)}
                                    </div>
                                </Card>
                            </motion.div>
                        </Col>

                        {selectedFlightId && (<Col xs={24} sm={12} lg={8}>
                                <motion.div variants={cardVariants}>
                                    <Card className="h-full shadow-lg">
                                        <div className="text-center">
                                            <div className="mb-4">
                                                <RiseOutlined className="text-3xl sm:text-4xl text-purple-500"/>
                                            </div>
                                            <Statistic
                                                title={<span className="text-sm sm:text-base">Flight Revenue</span>}
                                                value={flightRevenue}
                                                precision={2}
                                                styles={{
                                                    value: {
                                                        color: '#722ed1', fontSize: '1.5rem'
                                                    }
                                                }}
                                                prefix="$"
                                                loading={loading}
                                            />
                                            <Text type="secondary" className="text-xs sm:text-sm">
                                                Selected flight only
                                            </Text>
                                        </div>
                                    </Card>
                                </motion.div>
                            </Col>)}
                    </Row>

                    <Row className="mt-4 sm:mt-6">
                        <Col xs={24}>
                            <motion.div variants={cardVariants}>
                                <Card className="shadow-lg">
                                    <Title level={4} className="!mb-4 text-base sm:text-lg">
                                        Revenue Summary
                                    </Title>
                                    <Row gutter={[16, 16]}>
                                        <Col xs={12} sm={6}>
                                            <Statistic
                                                title={<span className="text-xs sm:text-sm">Total Flights</span>}
                                                value={flights.length}
                                                styles={{
                                                    value: {
                                                        color: '#1890ff', fontSize: '1.25rem'
                                                    }
                                                }}
                                            />
                                        </Col>
                                        <Col xs={12} sm={6}>
                                            <Statistic
                                                title={<span className="text-xs sm:text-sm">Average per Flight</span>}
                                                value={flights.length > 0 ? totalRevenue / flights.length : 0}
                                                precision={2}
                                                prefix="$"
                                                styles={{
                                                    value: {
                                                        color: '#52c41a', fontSize: '1.25rem'
                                                    }
                                                }}
                                            />
                                        </Col>
                                        <Col xs={12} sm={6}>
                                            <Statistic
                                                title={<span className="text-xs sm:text-sm">Active Flights</span>}
                                                value={flights.filter(f => f.status === 'SCHEDULED').length}
                                                styles={{
                                                    value: {
                                                        color: '#722ed1', fontSize: '1.25rem'
                                                    }
                                                }}
                                            />
                                        </Col>
                                        <Col xs={12} sm={6}>
                                            <Statistic
                                                title={<span className="text-xs sm:text-sm">Completed</span>}
                                                value={flights.filter(f => f.status === 'COMPLETED').length}
                                                styles={{
                                                    value: {
                                                        color: '#fa8c16', fontSize: '1.25rem'
                                                    }
                                                }}
                                            />
                                        </Col>
                                    </Row>
                                </Card>
                            </motion.div>
                        </Col>
                    </Row>
                </motion.div>
            </motion.div>
        </div>);
}

export default SupervisorRevenuePage;
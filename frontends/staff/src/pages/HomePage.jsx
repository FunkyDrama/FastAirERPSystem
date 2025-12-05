import React from "react";
import {Card, Col, Row, Typography} from "antd";
import {Link} from "react-router-dom";
import {motion} from "framer-motion";
import RoleGuard from "../components/RoleGuard.jsx";
import {ControlOutlined, ScanOutlined, SettingOutlined} from "@ant-design/icons";
import {ROLES} from "../utils/roles.js";

const {Title, Paragraph} = Typography;

function HomePage() {

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

    return (<div className="min-h-screen bg-gray-100">
            <div
                className="relative bg-cover bg-center bg-fixed"
                style={{backgroundImage: "url('/background.jpg')"}}
            >
                <div className="absolute inset-0 bg-gradient-to-br from-blue-900/80 to-gray-900/80"/>

                <div className="relative z-10 flex flex-col items-center justify-center h-80 text-center px-6">
                    <motion.div
                        initial={{opacity: 0, y: -30}}
                        animate={{opacity: 1, y: 0}}
                        transition={{duration: 0.7}}
                    >
                        <Title level={1} className="!text-white !text-5xl font-bold !mb-4">
                            Welcome to FastAir Staff Portal
                        </Title>
                    </motion.div>
                </div>
            </div>

            <div className="p-6">
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                >
                    <Row gutter={[24, 24]}>
                        <RoleGuard roles={[ROLES.CHECKIN]}>
                            <Col xs={24} sm={12} lg={8}>
                                <motion.div variants={cardVariants}>
                                    <Card
                                        hoverable
                                        className="h-full border-0 shadow-lg"
                                        styles={{body: {padding: '24px'}}}
                                    >
                                        <div className="text-center">
                                            <div className="mb-4">
                                                <ScanOutlined className="text-4xl text-green-500"/>
                                            </div>
                                            <Title level={4} className="!mb-2">
                                                Check-in Operations
                                            </Title>
                                            <Paragraph type="secondary" className="!mb-6">
                                                Scan QR codes and manage passenger check-ins
                                            </Paragraph>
                                            <Link to="/checkin">
                                                <div
                                                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg w-full transition-colors">
                                                    Start Check-in
                                                </div>
                                            </Link>
                                        </div>
                                    </Card>
                                </motion.div>
                            </Col>
                        </RoleGuard>

                        <RoleGuard roles={[ROLES.GATE]}>
                            <Col xs={24} sm={12} lg={8}>
                                <motion.div variants={cardVariants}>
                                    <Card
                                        hoverable
                                        className="h-full border-0 shadow-lg"
                                        styles={{body: {padding: '24px'}}}
                                    >
                                        <div className="text-center">
                                            <div className="mb-4">
                                                <ControlOutlined className="text-4xl text-blue-500"/>
                                            </div>
                                            <Title level={4} className="!mb-2">
                                                Gate Management
                                            </Title>
                                            <Paragraph type="secondary" className="!mb-6">
                                                Control boarding and manage flight gates
                                            </Paragraph>
                                            <Link to="/gate">
                                                <div
                                                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg w-full transition-colors">
                                                    Gate Control
                                                </div>
                                            </Link>
                                        </div>
                                    </Card>
                                </motion.div>
                            </Col>
                        </RoleGuard>

                        <RoleGuard roles={[ROLES.SUPERVISOR]}>
                            <Col xs={24} sm={12} lg={8}>
                                <motion.div variants={cardVariants}>
                                    <Card
                                        hoverable
                                        className="h-full border-0 shadow-lg"
                                        styles={{body: {padding: '24px'}}}
                                    >
                                        <div className="text-center">
                                            <div className="mb-4">
                                                <SettingOutlined className="text-4xl text-red-500"/>
                                            </div>
                                            <Title level={4} className="!mb-2">
                                                Supervisor Panel
                                            </Title>
                                            <Paragraph type="secondary" className="!mb-6">
                                                System administration and oversight
                                            </Paragraph>
                                            <div className="space-y-2">
                                                <Link to="/supervisor/flights">
                                                    <div
                                                        className="bg-red-600 hover:bg-red-700 text-white mb-4 px-6 py-3 rounded-lg w-full transition-colors">
                                                        Manage Flights
                                                    </div>
                                                </Link>
                                                <Link to="/supervisor/staff">
                                                    <div
                                                        className="bg-gray-600 hover:bg-gray-700 text-white mb-4 px-6 py-3 rounded-lg w-full transition-colors">
                                                        Manage Staff
                                                    </div>
                                                </Link>
                                                <Link to="/supervisor/revenue">
                                                    <div
                                                        className="bg-blue-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg w-full transition-colors">
                                                        Revenue Analytics
                                                    </div>
                                                </Link>
                                            </div>
                                        </div>
                                    </Card>
                                </motion.div>
                            </Col>
                        </RoleGuard>
                    </Row>
                </motion.div>
            </div>
        </div>);
}

export default HomePage;
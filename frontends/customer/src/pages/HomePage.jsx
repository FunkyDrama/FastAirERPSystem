import React from "react";
import { Typography, Button } from "antd";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

const { Title, Paragraph } = Typography;

function HomePage() {
    return (
        <div
            className="relative flex flex-col items-center justify-center h-screen text-center px-6
                       bg-cover bg-center bg-fixed"
            style={{ backgroundImage: "url('/background.jpg')" }}
        >
            <div className="absolute inset-0 bg-gradient-to-b from-black/50 to-transparent" />


            <div className="relative z-10 max-w-2xl">
                <motion.div
                    initial={{ opacity: 0, y: -30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.7 }}
                >
                    <Title level={1} className="!text-white !text-7xl font-bold">
                        Welcome to FastAir
                    </Title>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5, duration: 0.7 }}
                >
                    <Paragraph className="!text-xl !text-white !mb-12 ">
                        Find the best flights and manage your bookings with ease.
                    </Paragraph>
                </motion.div>

                <motion.div
                    className="flex gap-4 justify-center"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1, duration: 0.7 }}
                >
                    <Link to="/booking">
                        <Button type="primary" size="large">
                            Search Flights
                        </Button>
                    </Link>
                </motion.div>
            </div>
        </div>
    );
}

export default HomePage;

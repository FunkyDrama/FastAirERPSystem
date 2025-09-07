import React, { useEffect, useState } from "react";
import api from "../utils/api.js";
import { Table, Tag, Empty, Typography, Button, Modal } from "antd";
import dayjs from "dayjs";
import { airportLabel } from "../utils/airports.js";
import { useLocation } from "react-router-dom";
import PaymentButton from "../components/PaymentButton.jsx";

const { Title } = Typography;

function Dashboard() {
    const [user, setUser] = useState(null);
    const [modal, contextHolder] = Modal.useModal();
    const [loadingId, setLoadingId] = useState(null);

    useEffect(() => {
        const fetchMe = async () => {
            try {
                const res = await api.get("/me");
                setUser(res.data);
            } catch {
                console.error("Error fetching user.");
            }
        };
        fetchMe();
    }, []);

    const location = useLocation();
    useEffect(() => {
        const params = new URLSearchParams(location.search);
        if (params.get("success") || params.get("canceled")) {
            (async () => {
                try {
                    const res = await api.get("/me");
                    setUser(res.data);
                } catch {}
            })();
        }
    }, [location.search]);

    const handleCancelBooking = async (bookingId) => {
        setLoadingId(bookingId);
        try {
            await api.post(`/bookings/${bookingId}/cancel`);
            const res = await api.get("/me");
            setUser(res.data);
        } catch {
            alert("Failed to cancel booking");
        } finally {
            setLoadingId(null);
        }
    };

    const handleRefundBooking = async (bookingId) => {
        setLoadingId(bookingId);
        try {
            await api.post(`/payments/${bookingId}/refund`);
            await api.post(`/bookings/${bookingId}/cancel`);
            const res = await api.get("/me");
            setUser(res.data);
        } catch {
            alert("Failed to cancel & refund booking");
        } finally {
            setLoadingId(null);
        }
    };

    const columns = [
        {
            title: "Flight",
            dataIndex: ["flight", "flight_number"],
            key: "flight_number",
        },
        {
            title: "From",
            dataIndex: ["flight", "origin"],
            key: "origin",
            render: (code) => airportLabel(code),
        },
        {
            title: "To",
            dataIndex: ["flight", "destination"],
            key: "destination",
            render: (code) => airportLabel(code),
        },
        {
            title: "Departure",
            dataIndex: ["flight", "departure_time"],
            key: "departure_time",
            render: (text) => dayjs(text).format("YYYY-MM-DD HH:mm"),
        },
        {
            title: "Arrival",
            dataIndex: ["flight", "arrival_time"],
            key: "arrival_time",
            render: (text) => dayjs(text).format("YYYY-MM-DD HH:mm"),
        },
        {
            title: "Status",
            dataIndex: "status",
            key: "status",
            render: (status) => {
                let color = "default";
                if (status?.toLowerCase() === "paid") color = "green";
                if (status?.toLowerCase() === "reserved") color = "blue";
                if (status?.toLowerCase() === "canceled") color = "volcano";
                if (status?.toLowerCase() === "refunded") color = "purple";
                return <Tag color={color}>{status}</Tag>;
            },
        },
        {
            title: "Tickets",
            dataIndex: "tickets_count",
            key: "tickets_count",
        },
        {
            title: "Amount",
            dataIndex: "total_amount",
            key: "total_amount",
            render: (amt) => `$${amt}`,
        },
        {
            title: "Actions",
            key: "actions",
            render: (_, record) => (
                <div className="flex gap-2">
                    {record.status?.toLowerCase() !== "paid" &&
                        record.status?.toLowerCase() !== "refunded" && (
                        <PaymentButton bookingId={record.booking_id} />
                    )}

                    {record.status?.toLowerCase() === "paid" && (
                        <Button
                            danger
                            loading={loadingId === record.booking_id}
                            onClick={() => {
                                modal.confirm({
                                    title: "Cancel & Refund Booking",
                                    content:
                                        "Are you sure you want to cancel this booking and refund the payment?",
                                    okText: "Yes, cancel & refund",
                                    okType: "danger",
                                    cancelText: "No",
                                    onOk: () => handleRefundBooking(record.booking_id),
                                });
                            }}
                        >
                            Cancel & Refund
                        </Button>
                    )}

                    {record.status?.toLowerCase() !== "canceled" &&
                        record.status?.toLowerCase() !== "refunded" &&
                        record.status?.toLowerCase() !== "paid" && (
                            <Button
                                danger
                                loading={loadingId === record.booking_id}
                                onClick={() => {
                                    modal.confirm({
                                        title: "Cancel Booking",
                                        content: "Are you sure you want to cancel this booking?",
                                        okText: "Yes, cancel",
                                        okType: "danger",
                                        cancelText: "No",
                                        onOk: () => handleCancelBooking(record.booking_id),
                                    });
                                }}
                            >
                                Cancel
                            </Button>
                        )}
                </div>
            ),
        },
    ];

    return (
        <div className="relative bg-gray-100 min-h-screen p-6">
            {contextHolder}
            {user && (
                <>
                    <div className="absolute top-4 left-6 text-gray-800">
                        <p className="text-lg font-medium">
                            <b>{user.email}</b> | Balance: ${user.balance}
                        </p>
                    </div>

                    <div className="mt-16">
                        <Title level={4}>Upcoming Flights</Title>
                        {user.upcoming && user.upcoming.length > 0 ? (
                            <Table
                                columns={columns}
                                dataSource={user.upcoming.map((b) => ({
                                    key: b.booking_id,
                                    ...b,
                                }))}
                                pagination={false}
                            />
                        ) : (
                            <Empty description="No upcoming flights" />
                        )}
                    </div>
                </>
            )}
        </div>
    );
}

export default Dashboard;

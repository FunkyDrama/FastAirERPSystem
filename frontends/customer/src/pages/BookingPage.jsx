import React, {useEffect, useRef, useState} from "react";
import {App, Button, Card, Checkbox, DatePicker, Form, Input, InputNumber, Modal, Select, Spin, Table, Tag,} from "antd";
import dayjs from "dayjs";
import api from "../utils/api.js";
import {airportLabel, AIRPORTS} from "../utils/airports";
import {optionLabel} from "../utils/options";

const PAGE_SIZE = 20;

function BookingPage() {
    const {message} = App.useApp();
    const [loading, setLoading] = useState(false);
    const [flights, setFlights] = useState([]);
    const [hasMore, setHasMore] = useState(false);
    const [loadingMore, setLoadingMore] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);
    const [selectedFlight, setSelectedFlight] = useState(null);
    const [seatTypes, setSeatTypes] = useState([]);
    const [options, setOptions] = useState([]);
    const [passengerCount, setPassengerCount] = useState(1);
    const [form] = Form.useForm();
    const [searchForm] = Form.useForm();

    const sentinelRef = useRef(null);
    const searchParamsRef = useRef(null);
    const offsetRef = useRef(0);
    const hasMoreRef = useRef(false);
    const loadingMoreRef = useRef(false);
    const loadingRef = useRef(false);

    useEffect(() => {
        const loadSeatTypes = async () => {
            try {
                const res = await api.get("/flights/catalog/seat-types");
                setSeatTypes(res.data);
            } catch {
                message.error("Failed to load seat types");
            }
        };
        loadSeatTypes();
    }, []);

    // Setup IntersectionObserver once; loadMore is always called via ref
    useEffect(() => {
        const sentinel = sentinelRef.current;
        if (!sentinel) return;

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) loadMoreViaRef();
            },
            {rootMargin: "200px"},
        );
        observer.observe(sentinel);
        return () => observer.disconnect();
    }, []);

    const loadMoreViaRef = () => {
        if (!searchParamsRef.current || !hasMoreRef.current || loadingMoreRef.current || loadingRef.current) return;

        loadingMoreRef.current = true;
        setLoadingMore(true);

        api.get("/flights/search", {
            params: {...searchParamsRef.current, offset: offsetRef.current},
        }).then((res) => {
            setFlights((prev) => [...prev, ...res.data]);
            offsetRef.current += res.data.length;
            const more = res.data.length === PAGE_SIZE;
            hasMoreRef.current = more;
            setHasMore(more);
        }).catch(() => {
            message.error("Failed to load more flights");
        }).finally(() => {
            loadingMoreRef.current = false;
            setLoadingMore(false);
        });
    };

    const searchFlights = async (values) => {
        setLoading(true);
        loadingRef.current = true;

        const params = {
            origin: values.origin || undefined,
            destination: values.destination || undefined,
            date: values.date ? values.date.format("YYYY-MM-DD") : undefined,
            passengers: values.passengers || undefined,
            limit: PAGE_SIZE,
            offset: 0,
        };
        searchParamsRef.current = params;
        offsetRef.current = 0;

        try {
            const res = await api.get("/flights/search", {params});
            setFlights(res.data);
            offsetRef.current = res.data.length;
            const more = res.data.length === PAGE_SIZE;
            hasMoreRef.current = more;
            setHasMore(more);
        } catch {
            message.error("Failed to search flights");
        } finally {
            setLoading(false);
            loadingRef.current = false;
        }
    };

    const openBookingModal = async (flight) => {
        setSelectedFlight(flight);
        setPassengerCount(1);

        try {
            const res = await api.get(`/flights/options/${flight.flight_id}`);
            setOptions(res.data);
        } catch {
            setOptions([]);
        }

        setModalVisible(true);
    };

    const handleBooking = async (values) => {
        try {
            const payload = {
                flight_id: selectedFlight.flight_id,
                passengers: values.passengers.map((p) => ({
                    first_name: p.first_name, last_name: p.last_name,
                })),
                seat_type_name: values.seat_type_name,
                discount_code: values.discount_code || null,
                lock_price: true,
                options: values.options?.map((opt) => ({
                    option_id: opt, qty: 1,
                })) || [],
                per_passenger_options: true,
            };
            const bookingRes = await api.post("/bookings", payload);
            const booking = bookingRes.data;
            const paymentRes = await api.post(`/payments/${booking.booking_id}/intent`);
            const {url} = paymentRes.data;
            window.location.href = url;
        } catch (err) {
            console.error(err);
            message.error("Failed to create booking or start payment");
        }
    };

    const columns = [{
        title: "Flight", dataIndex: "flight_number", key: "flight_number", width: 120,
    }, {
        title: "From", dataIndex: "origin", key: "origin", render: (code) => airportLabel(code), width: 150,
    }, {
        title: "To", dataIndex: "destination", key: "destination", render: (code) => airportLabel(code), width: 150,
    }, {
        title: "Departure",
        dataIndex: "departure_time",
        key: "departure_time",
        render: (text) => dayjs(text).format("YYYY-MM-DD HH:mm"),
        width: 160,
    }, {
        title: "Arrival",
        dataIndex: "arrival_time",
        key: "arrival_time",
        render: (text) => dayjs(text).format("YYYY-MM-DD HH:mm"),
        width: 160,
    }, {
        title: "Status", dataIndex: "status", key: "status", width: 120, render: (status) => {
            const s = status?.toLowerCase();
            const color = s === "scheduled" ? "green" : s === "completed" ? "blue" : "volcano";
            return <Tag color={color}>{status?.toUpperCase()}</Tag>;
        },
    }, {
        title: "Action", key: "action", fixed: "right", width: 100, render: (_, record) => {
            const isScheduled = record.status?.toLowerCase() === "scheduled";
            return (
                <Button
                    type="primary"
                    size="small"
                    onClick={() => openBookingModal(record)}
                    block
                    disabled={!isScheduled}
                >
                    Book
                </Button>
            );
        },
    },];

    return (<div className="p-4 sm:p-6 lg:p-8 bg-gray-100 min-h-screen">
            <h2 className="text-xl sm:text-2xl font-semibold mb-4 sm:mb-6">
                Search Flights
            </h2>

            <Card className="mb-6">
                <Form
                    form={searchForm}
                    layout="vertical"
                    onFinish={searchFlights}
                >
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        <Form.Item
                            name="origin"
                            label="From"
                        >
                            <Select
                                placeholder="Any airport"
                                size="large"
                                showSearch
                                allowClear
                                filterOption={(input, option) => option.children
                                    .toLowerCase()
                                    .includes(input.toLowerCase())}
                            >
                                {Object.entries(AIRPORTS).map(([code]) => (<Select.Option key={code} value={code}>
                                        {airportLabel(code)}
                                    </Select.Option>))}
                            </Select>
                        </Form.Item>

                        <Form.Item
                            name="destination"
                            label="To"
                        >
                            <Select
                                placeholder="Any airport"
                                size="large"
                                showSearch
                                allowClear
                                filterOption={(input, option) => option.children
                                    .toLowerCase()
                                    .includes(input.toLowerCase())}
                            >
                                {Object.entries(AIRPORTS).map(([code]) => (<Select.Option key={code} value={code}>
                                        {airportLabel(code)}
                                    </Select.Option>))}
                            </Select>
                        </Form.Item>

                        <Form.Item name="date" label="Date">
                            <DatePicker
                                className="w-full"
                                size="large"
                                placeholder="Any date"
                            />
                        </Form.Item>

                        <Form.Item label="&nbsp;">
                            <Button
                                type="primary"
                                htmlType="submit"
                                loading={loading}
                                size="large"
                                block
                            >
                                Search Flights
                            </Button>
                        </Form.Item>
                    </div>

                    <div className="mt-2 text-sm text-gray-500">
                        💡 Leave fields empty to see all available flights
                    </div>
                </Form>
            </Card>

            <Card>
                <Table
                    rowKey="flight_id"
                    columns={columns}
                    dataSource={flights}
                    loading={loading}
                    pagination={false}
                    scroll={{x: 1000}}
                    locale={{
                        emptyText: loading ? "Searching flights..." : "No flights found. Try different search criteria or click 'Search Flights' to see all.",
                    }}
                />
                <div ref={sentinelRef}/>
                {loadingMore && (
                    <div className="flex justify-center py-4">
                        <Spin/>
                    </div>
                )}
                {!hasMore && flights.length > 0 && (
                    <div className="text-center py-3 text-gray-400 text-sm">
                        All flights loaded
                    </div>
                )}
            </Card>

            <Modal
                open={modalVisible}
                onCancel={() => {
                    setModalVisible(false);
                    form.resetFields();
                }}
                onOk={() => form.submit()}
                title={<span className="text-lg font-semibold">
                        Booking flight {selectedFlight?.flight_number}
                    </span>}
                width={600}
                className="max-w-full mx-4"
            >
                <Form form={form} layout="vertical" onFinish={handleBooking}>
                    <Form.Item label="Number of passengers">
                        <InputNumber
                            min={1}
                            max={9}
                            value={passengerCount}
                            onChange={setPassengerCount}
                            size="large"
                            className="w-full"
                        />
                    </Form.Item>

                    {Array.from({length: passengerCount}).map((_, i) => (<div
                            key={i}
                            className="border border-gray-200 rounded-lg p-4 mb-4 bg-gray-50"
                        >
                            <h4 className="font-medium mb-3 text-gray-700">
                                Passenger {i + 1}
                            </h4>
                            <Form.Item
                                name={["passengers", i, "first_name"]}
                                label="First name"
                                rules={[{required: true, message: "Enter first name"},]}
                            >
                                <Input size="large" placeholder="John"/>
                            </Form.Item>
                            <Form.Item
                                name={["passengers", i, "last_name"]}
                                label="Last name"
                                rules={[{required: true, message: "Enter last name"}]}
                            >
                                <Input size="large" placeholder="Doe"/>
                            </Form.Item>
                        </div>))}

                    <Form.Item
                        name="seat_type_name"
                        label="Seat class"
                        rules={[{required: true, message: "Select seat class"}]}
                    >
                        <Select size="large" placeholder="Select class">
                            {seatTypes.map((st) => (<Select.Option key={st.type_name} value={st.type_name}>
                                    {st.description}
                                </Select.Option>))}
                        </Select>
                    </Form.Item>

                    <Form.Item name="options" label="Extra options">
                        <Checkbox.Group className="flex flex-col gap-2">
                            {options.map((opt) => (<Checkbox key={opt.option_id} value={opt.option_id}>
                                    <span className="text-sm sm:text-base">
                                        {optionLabel(opt.name)} (+${opt.price})
                                    </span>
                                </Checkbox>))}
                        </Checkbox.Group>
                    </Form.Item>

                    <Form.Item name="discount_code" label="Discount code">
                        <Input
                            size="large"
                            placeholder="Enter discount code (optional)"
                        />
                    </Form.Item>
                </Form>
            </Modal>
        </div>);
}

export default BookingPage;
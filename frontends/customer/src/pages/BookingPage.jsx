import React, {useEffect, useState} from "react";
import {Button, Checkbox, DatePicker, Form, Input, InputNumber, message, Modal, Select, Table, Tag,} from "antd";
import dayjs from "dayjs";
import api from "../utils/api.js";
import {airportLabel, AIRPORTS} from "../utils/airports";
import {optionLabel} from "../utils/options";

function BookingPage() {
    const [loading, setLoading] = useState(false);
    const [flights, setFlights] = useState([]);
    const [modalVisible, setModalVisible] = useState(false);
    const [selectedFlight, setSelectedFlight] = useState(null);
    const [seatTypes, setSeatTypes] = useState([]);
    const [options, setOptions] = useState([]);
    const [passengerCount, setPassengerCount] = useState(1);
    const [form] = Form.useForm();

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

    const searchFlights = async (values) => {
        setLoading(true);
        try {
            const res = await api.get("/flights/search", {
                params: {
                    origin: values.origin,
                    destination: values.destination,
                    date: values.date ? values.date.format("YYYY-MM-DD") : undefined,
                    passengers: values.passengers,
                },
            });
            setFlights(res.data);
        } catch {
            message.error("Failed to search flights");
        } finally {
            setLoading(false);
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
                    first_name: p.first_name,
                    last_name: p.last_name,
                })),
                seat_type_name: values.seat_type_name,
                discount_code: values.discount_code || null,
                lock_price: true,
                options:
                    values.options?.map((opt) => ({
                        option_id: opt,
                        qty: 1,
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


    const columns = [
        {
            title: "Flight",
            dataIndex: "flight_number",
            key: "flight_number",
        },
        {
            title: "From",
            dataIndex: "origin",
            key: "origin",
            render: (code) => airportLabel(code),
        },
        {
            title: "To",
            dataIndex: "destination",
            key: "destination",
            render: (code) => airportLabel(code),
        },
        {
            title: "Departure",
            dataIndex: "departure_time",
            key: "departure_time",
            render: (text) => dayjs(text).format("YYYY-MM-DD HH:mm"),
        },
        {
            title: "Arrival",
            dataIndex: "arrival_time",
            key: "arrival_time",
            render: (text) => dayjs(text).format("YYYY-MM-DD HH:mm"),
        },
        {
            title: "Status",
            dataIndex: "status",
            key: "status",
            render: (status) => (
                <Tag color={status === "SCHEDULED"?.toLowerCase() ? "green" : "volcano"}>{status}</Tag>
            ),
        },
        {
            title: "Action",
            key: "action",
            render: (_, record) => (
                <Button type="primary" onClick={() => openBookingModal(record)}>
                    Book
                </Button>
            ),
        },
    ];

    return (
        <div className="p-6 bg-gray-100 h-screen">
            <h2 className="text-2xl font-semibold mb-6">Search Flights</h2>
            <Form
                layout="inline"
                onFinish={searchFlights}
                className="flex flex-wrap gap-4 !mb-6"
            >
                <Form.Item
                    name="origin"
                    label="From"
                >
                    <Select style={{width: 200}}>
                        {Object.entries(AIRPORTS).map(([code]) => (
                            <Select.Option key={code} value={code}>
                                {airportLabel(code)}
                            </Select.Option>
                        ))}
                    </Select>
                </Form.Item>

                <Form.Item
                    name="destination"
                    label="To"
                >
                    <Select style={{width: 200}}>
                        {Object.entries(AIRPORTS).map(([code]) => (
                            <Select.Option key={code} value={code}>
                                {airportLabel(code)}
                            </Select.Option>
                        ))}
                    </Select>
                </Form.Item>

                <Form.Item name="date" label="Date">
                    <DatePicker/>
                </Form.Item>

                <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading}>
                        Search
                    </Button>
                </Form.Item>
            </Form>

            <Table
                rowKey="flight_id"
                columns={columns}
                dataSource={flights}
                loading={loading}
                pagination={false}
            />

            <Modal
                open={modalVisible}
                onCancel={() => {
                    setModalVisible(false);
                    form.resetFields();
                }}
                onOk={() => form.submit()}
                title={`Booking flight ${selectedFlight?.flight_number}`}
            >
                <Form form={form} layout="vertical" onFinish={handleBooking}>
                    <Form.Item label="Number of passengers">
                        <InputNumber
                            min={1}
                            max={9}
                            value={passengerCount}
                            onChange={setPassengerCount}
                        />
                    </Form.Item>

                    {Array.from({length: passengerCount}).map((_, i) => (
                        <div
                            key={i}
                            className="border border-gray-200 rounded-md p-4 mb-4"
                        >
                            <h4 className="font-medium mb-2">Passenger {i + 1}</h4>
                            <Form.Item
                                name={["passengers", i, "first_name"]}
                                label="First name"
                                rules={[{required: true, message: "Please enter first name"}]}
                            >
                                <Input/>
                            </Form.Item>
                            <Form.Item
                                name={["passengers", i, "last_name"]}
                                label="Last name"
                                rules={[{required: true, message: "Please enter last name"}]}
                            >
                                <Input/>
                            </Form.Item>
                        </div>
                    ))}

                    <Form.Item
                        name="seat_type_name"
                        label="Seat class"
                        rules={[{required: true, message: "Please select seat class"}]}
                    >
                        <Select>
                            {seatTypes.map((st) => (
                                <Select.Option key={st.type_name} value={st.type_name}>
                                    {st.description}
                                </Select.Option>
                            ))}
                        </Select>
                    </Form.Item>

                    <Form.Item name="options" label="Extra options">
                        <Checkbox.Group className="flex flex-col gap-2">
                            {options.map((opt) => (
                                <Checkbox key={opt.option_id} value={opt.option_id}>
                                    {optionLabel(opt.name)} (+${opt.price})
                                </Checkbox>
                            ))}
                        </Checkbox.Group>
                    </Form.Item>

                    <Form.Item name="discount_code" label="Discount code">
                        <Input placeholder="Enter discount code (optional)"/>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
}

export default BookingPage;

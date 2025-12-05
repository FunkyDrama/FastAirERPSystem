import React from "react";
import api from "../utils/api.js";

function PaymentButton({bookingId, className = ""}) {
    const handlePay = async () => {
        try {
            const res = await api.post(`/payments/${bookingId}/intent`);
            const {url} = res.data;
            if (!url) {
                alert("No checkout URL returned from server");
                return;
            }
            window.location.href = url;
        } catch (e) {
            alert("Failed to start payment." + e.message);
        }
    };

    return (<button
        onClick={handlePay}
        className={`bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-md ${className}`}
    >
        Pay
    </button>);
}

export default PaymentButton;

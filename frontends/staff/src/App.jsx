import React from "react";
import {Route, Routes} from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Header from "./components/Header.jsx";

import HomePage from "./pages/HomePage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import CheckInPage from "./pages/CheckInPage.jsx";
import GatePage from "./pages/GatePage.jsx";
import SupervisorFlightsPage from "./pages/SupervisorFlightsPage.jsx";
import SupervisorStaffPage from "./pages/SupervisorStaffPage.jsx";
import SupervisorRevenuePage from "./pages/SupervisorRevenuePage.jsx";
import {ROLES} from "./utils/roles.js";

export default function App() {
    return (
        <div className="flex flex-col min-h-screen">
            <Header/>
            <main className="flex-1">
                <Routes>
                    <Route path="/login" element={<LoginPage/>}/>

                    <Route element={<ProtectedRoute/>}>
                        <Route path="/" element={<HomePage/>}/>
                    </Route>

                    <Route element={<ProtectedRoute roles={[ROLES.CHECKIN]}/>}>
                        <Route path="/checkin" element={<CheckInPage/>}/>
                    </Route>

                    <Route element={<ProtectedRoute roles={[ROLES.GATE]}/>}>
                        <Route path="/gate" element={<GatePage/>}/>
                    </Route>

                    <Route element={<ProtectedRoute roles={[ROLES.SUPERVISOR]}/>}>
                        <Route path="/supervisor/flights" element={<SupervisorFlightsPage/>}/>
                        <Route path="/supervisor/staff" element={<SupervisorStaffPage/>}/>
                        <Route path="/supervisor/revenue" element={<SupervisorRevenuePage/>}/>
                    </Route>
                </Routes>
            </main>
        </div>
    );
}
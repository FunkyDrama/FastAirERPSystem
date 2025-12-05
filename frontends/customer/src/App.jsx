import React from "react";
import {Route, Routes} from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import Dashboard from "./pages/Dashboard";
import BookingPage from "./pages/BookingPage";
import HomePage from "./pages/HomePage";
import Header from "./components/Header";
import ResponsiveLayout from "./components/ResponsiveLayout.jsx";
import {App as AntApp} from "antd";

function App() {
    return (<AntApp
        message={{
            maxCount: 3, duration: 3,
        }}
        notification={{
            maxCount: 3,
        }}
    >
        <ResponsiveLayout>
            <div className="flex flex-col min-h-screen">
                <Header/>
                <main className="flex-1">
                    <Routes>
                        <Route path="/" element={<HomePage/>}/>
                        <Route path="/login" element={<LoginPage/>}/>
                        <Route path="/register" element={<RegisterPage/>}/>
                        <Route element={<ProtectedRoute/>}>
                            <Route path="/dashboard" element={<Dashboard/>}/>
                            <Route path="/booking" element={<BookingPage/>}/>
                        </Route>
                    </Routes>
                </main>
            </div>
        </ResponsiveLayout>)
    </AntApp>)
}

export default App;

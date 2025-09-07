import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "./AuthContext.jsx";
import { Button } from "antd";
import { motion } from "framer-motion";

function Header() {
    const { accessToken, logout } = useAuth();
    const [hidden, setHidden] = useState(false);
    const [lastScrollY, setLastScrollY] = useState(0);

    useEffect(() => {
        const handleScroll = () => {
            if (window.scrollY > lastScrollY) {
                setHidden(true);
            } else {
                setHidden(false);
            }
            setLastScrollY(window.scrollY);
        };

        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, [lastScrollY]);

    return (
        <motion.header
            initial={{ y: -80 }}
            animate={{ y: hidden ? -80 : 0 }}
            transition={{ duration: 0.3 }}
            className="sticky top-0 z-50 flex justify-between items-center px-6 py-4 bg-gray-600 text-white shadow-md"
        >
            <Link to="/" className="flex items-center">
                <img src="/logo.png" alt="Logo" className="h-10 w-auto" />
            </Link>
            <div className="flex gap-3">
                {!accessToken ? (
                    <>
                        <Link to="/login">
                            <Button type="primary">Login</Button>
                        </Link>
                        <Link to="/register">
                            <Button>Register</Button>
                        </Link>
                    </>
                ) : (
                    <>
                        <Link to="/dashboard">
                            <Button type="primary">Dashboard</Button>
                        </Link>
                        <Link to="/booking">
                            <Button>Book a Flight</Button>
                        </Link>
                        <Button danger onClick={logout}>
                            Logout
                        </Button>
                    </>
                )}
            </div>
        </motion.header>
    );
}

export default Header;

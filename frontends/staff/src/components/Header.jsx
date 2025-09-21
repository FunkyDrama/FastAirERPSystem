import React, {useEffect, useState} from "react";
import {Link, useNavigate} from "react-router-dom";
import {useAuth} from "./AuthContext.jsx";
import {Button, Dropdown, Menu, Space, Tag} from "antd";
import {DashboardOutlined, LogoutOutlined} from "@ant-design/icons";
import {motion} from "framer-motion";
import RoleGuard from "./RoleGuard.jsx";
import {ROLES} from "../utils/roles.js";

function Header() {
    const {user, logout} = useAuth();
    const navigate = useNavigate();
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

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    return (
        <motion.header
            initial={{y: -80}}
            animate={{y: hidden ? -80 : 0}}
            transition={{duration: 0.3}}
            className="sticky top-0 z-50 bg-gray-600 text-white shadow-md"
        >
            <div className="flex justify-between items-center px-6 py-4">
                <Link to="/" className="flex items-center space-x-3">
                    <img src="/logo.png" alt="Logo" className="h-10 w-auto"/>
                    <div className="text-2xl font-bold text-white">
                        Staff
                    </div>
                </Link>

                {!user ? (
                    <Link to="/login">
                        <Button type="primary" size="large">
                            Login
                        </Button>
                    </Link>
                ) : (
                    <div className="flex items-center space-x-4">
                        <Space size="middle">
                            <Link to="/">
                                <Button type="text" icon={<DashboardOutlined/>}
                                        className="!text-white hover:text-gray-200">
                                    Dashboard
                                </Button>
                            </Link>

                            <RoleGuard roles={[ROLES.CHECKIN]}>
                                <Link to="/checkin">
                                    <Button type="text" className="!text-white hover:text-gray-200">
                                        Check-in
                                    </Button>
                                </Link>
                            </RoleGuard>

                            <RoleGuard roles={[ROLES.GATE]}>
                                <Link to="/gate">
                                    <Button type="text" className="!text-white hover:text-gray-200">
                                        Gate
                                    </Button>
                                </Link>
                            </RoleGuard>

                            < RoleGuard roles={[ROLES.SUPERVISOR]}>
                                <Dropdown
                                    overlay={
                                        <Menu>
                                            <Menu.Item key="flights">
                                                <Link to="/supervisor/flights">Manage Flights</Link>
                                            </Menu.Item>
                                            <Menu.Item key="staff">
                                                <Link to="/supervisor/staff">Manage Staff</Link>
                                            </Menu.Item>
                                            <Menu.Item key="revenue">
                                                <Link to="/supervisor/revenue">Revenue Analytics</Link>
                                            </Menu.Item>
                                        </Menu>
                                    }
                                    trigger={['hover']}
                                >
                                    <Button type="text" className="!text-white hover:text-gray-200">
                                        Supervisor
                                    </Button>
                                </Dropdown>
                            </RoleGuard>
                        </Space>

                        <div className="flex items-center space-x-3">
                            <div className="text-right hidden sm:block">
                                <Tag color={
                                    user?.role === ROLES.SUPERVISOR ? 'red' :
                                        user?.role === ROLES.GATE ? 'blue' : 'green'
                                }>
                                    {user?.role?.replace('_', ' ').toUpperCase()}
                                </Tag>
                            </div>
                            <Button
                                type="text"
                                className="!text-white hover:text-gray-200"
                                onClick={handleLogout}
                                icon={<LogoutOutlined/>}
                            >
                                Logout
                            </Button>
                        </div>
                    </div>
                )}
            </div>
        </motion.header>
    );
}

export default Header;
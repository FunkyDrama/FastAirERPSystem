import React, {useEffect, useState} from "react";
import {Link, useNavigate} from "react-router-dom";
import {useAuth} from "./AuthContext.jsx";
import {Button, Drawer, Dropdown, Space, Tag} from "antd";
import {DashboardOutlined, LogoutOutlined, MenuOutlined} from "@ant-design/icons";
import {motion} from "framer-motion";
import RoleGuard from "./RoleGuard.jsx";
import {ROLES} from "../utils/roles.js";

function Header() {
    const {user, logout} = useAuth();
    const navigate = useNavigate();
    const [hidden, setHidden] = useState(false);
    const [lastScrollY, setLastScrollY] = useState(0);
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

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

    useEffect(() => {
        const handleResize = () => {
            const mobile = window.innerWidth < 768;
            setIsMobile(mobile);

            if (!mobile && drawerOpen) {
                setDrawerOpen(false);
            }
        };

        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, [drawerOpen]);

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    const handleDrawerLogout = async () => {
        setDrawerOpen(false);
        await logout();
        navigate('/login');
    };

    return (<>
            <motion.header
                initial={{y: -80}}
                animate={{y: hidden ? -80 : 0}}
                transition={{duration: 0.3}}
                className="sticky top-0 z-50 bg-gray-600 text-white shadow-md"
            >
                <div className="flex justify-between items-center px-4 sm:px-6 py-3 sm:py-4">
                    <Link to="/" className="flex items-center space-x-2 sm:space-x-3">
                        <img src="/logo.png" alt="Logo" className="h-8 sm:h-10 w-auto"/>
                        <div className="text-xl sm:text-2xl font-bold text-white">
                            Staff
                        </div>
                    </Link>

                    {!isMobile && user && (<div className="flex items-center space-x-4">
                            <Space size="middle">
                                <Link to="/">
                                    <Button
                                        type="text"
                                        icon={<DashboardOutlined/>}
                                        className="!text-white hover:text-gray-200"
                                    >
                                        Dashboard
                                    </Button>
                                </Link>

                                <RoleGuard roles={[ROLES.CHECKIN]}>
                                    <Link to="/checkin">
                                        <Button
                                            type="text"
                                            className="!text-white hover:text-gray-200"
                                        >
                                            Check-in
                                        </Button>
                                    </Link>
                                </RoleGuard>

                                <RoleGuard roles={[ROLES.GATE]}>
                                    <Link to="/gate">
                                        <Button
                                            type="text"
                                            className="!text-white hover:text-gray-200"
                                        >
                                            Gate
                                        </Button>
                                    </Link>
                                </RoleGuard>

                                <RoleGuard roles={[ROLES.SUPERVISOR]}>
                                    <Dropdown
                                        menu={{
                                            items: [{
                                                key: 'flights',
                                                label: <Link to="/supervisor/flights">Manage Flights</Link>,
                                            }, {
                                                key: 'staff', label: <Link to="/supervisor/staff">Manage Staff</Link>,
                                            }, {
                                                key: 'revenue',
                                                label: <Link to="/supervisor/revenue">Revenue Analytics</Link>,
                                            },],
                                        }}
                                        trigger={['hover']}
                                    >
                                        <Button
                                            type="text"
                                            className="!text-white hover:text-gray-200"
                                        >
                                            Supervisor
                                        </Button>
                                    </Dropdown>
                                </RoleGuard>
                            </Space>

                            <div className="flex items-center space-x-3">
                                <div className="text-right hidden sm:block">
                                    <Tag
                                        color={user?.role === ROLES.SUPERVISOR ? 'red' : user?.role === ROLES.GATE ? 'blue' : 'green'}>
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
                        </div>)}

                    {!user ? (<Link to="/login">
                            <Button type="primary" size={isMobile ? "middle" : "large"}>
                                Login
                            </Button>
                        </Link>) : isMobile && (<Button
                            type="text"
                            size="large"
                            icon={<MenuOutlined
                                style={{
                                    color: 'white', fontSize: '24px'
                                }}
                            />}
                            onClick={() => setDrawerOpen(true)}
                        />)}
                </div>
            </motion.header>

            <Drawer
                title={<div className="flex items-center gap-2">
                    <span>Menu</span>
                </div>}
                placement="right"
                onClose={() => setDrawerOpen(false)}
                open={drawerOpen && isMobile}
                size={280}
                styles={{
                    body: {padding: '16px'}, wrapper: {position: 'absolute'}
                }}
                rootStyle={{position: 'absolute'}}
                maskClosable={true}
                destroyOnClose={true}
            >
                <div className="flex flex-col gap-3">
                    {user && (<div className="mb-4 p-3 bg-gray-100 rounded-lg text-center">
                            <Tag
                                color={user?.role === ROLES.SUPERVISOR ? 'red' : user?.role === ROLES.GATE ? 'blue' : 'green'}
                                className="text-sm"
                            >
                                {user?.role?.replace('_', ' ').toUpperCase()}
                            </Tag>
                        </div>)}

                    <Button
                        block
                        size="large"
                        icon={<DashboardOutlined/>}
                        type="primary"
                        onClick={() => {
                            setDrawerOpen(false);
                            navigate('/');
                        }}
                    >
                        Dashboard
                    </Button>

                    <RoleGuard roles={[ROLES.CHECKIN]}>
                        <Button
                            block
                            size="large"
                            onClick={() => {
                                setDrawerOpen(false);
                                navigate('/checkin');
                            }}
                        >
                            Check-in
                        </Button>
                    </RoleGuard>

                    <RoleGuard roles={[ROLES.GATE]}>
                        <Button
                            block
                            size="large"
                            onClick={() => {
                                setDrawerOpen(false);
                                navigate('/gate');
                            }}
                        >
                            Gate
                        </Button>
                    </RoleGuard>

                    <RoleGuard roles={[ROLES.SUPERVISOR]}>
                        <div className="border-t pt-3 mt-2">
                            <div className="text-sm text-gray-500 mb-2 px-2">
                                Supervisor
                            </div>
                            <Button
                                block
                                size="large"
                                className="mb-2"
                                onClick={() => {
                                    setDrawerOpen(false);
                                    navigate('/supervisor/flights');
                                }}
                            >
                                Manage Flights
                            </Button>
                            <Button
                                block
                                size="large"
                                className="mb-2"
                                onClick={() => {
                                    setDrawerOpen(false);
                                    navigate('/supervisor/staff');
                                }}
                            >
                                Manage Staff
                            </Button>
                            <Button
                                block
                                size="large"
                                onClick={() => {
                                    setDrawerOpen(false);
                                    navigate('/supervisor/revenue');
                                }}
                            >
                                Revenue Analytics
                            </Button>
                        </div>
                    </RoleGuard>

                    <Button
                        danger
                        block
                        size="large"
                        icon={<LogoutOutlined/>}
                        onClick={handleDrawerLogout}
                        className="mt-4"
                    >
                        Logout
                    </Button>
                </div>
            </Drawer>
        </>);
}

export default Header;
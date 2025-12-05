import React, {useEffect, useState} from "react";
import {Link} from "react-router-dom";
import {useAuth} from "./AuthContext.jsx";
import {Button, Drawer} from "antd";
import {MenuOutlined} from "@ant-design/icons";
import {motion} from "framer-motion";

function Header() {
    const {user, logout} = useAuth();
    const [hidden, setHidden] = useState(false);
    const [lastScrollY, setLastScrollY] = useState(0);
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

    useEffect(() => {
        const handleScroll = () => {
            if (window.scrollY > lastScrollY && window.scrollY > 50) {
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

        handleResize();

        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, [drawerOpen]);

    const handleLogout = () => {
        setDrawerOpen(false);
        logout();
    };

    return (<>
        <motion.header
            initial={{y: -80}}
            animate={{y: hidden ? -80 : 0}}
            transition={{duration: 0.3}}
            className="sticky top-0 z-50 flex justify-between items-center px-4 sm:px-6 lg:px-8 py-3 sm:py-4 bg-gray-600 text-white shadow-md"
        >
            <Link to="/" className="flex items-center">
                <img
                    src="/logo.png"
                    alt="FastAir"
                    className="h-8 sm:h-10 w-auto"
                />
            </Link>

            <div className="flex items-center">
                <nav
                    className="gap-3 items-center"
                    style={{display: isMobile ? 'none' : 'flex'}}
                >
                    {!user ? (<>
                        <Link to="/login">
                            <Button type="primary">Login</Button>
                        </Link>
                        <Link to="/register">
                            <Button>Register</Button>
                        </Link>
                    </>) : (<>
                        <Link to="/dashboard">
                            <Button type="primary">Dashboard</Button>
                        </Link>
                        <Link to="/booking">
                            <Button>Book a Flight</Button>
                        </Link>
                        <Button danger onClick={logout}>
                            Logout
                        </Button>
                    </>)}
                </nav>

                {isMobile && (<Button
                    type="text"
                    size="large"
                    icon={<MenuOutlined style={{color: 'white', fontSize: '24px'}}/>}
                    onClick={() => setDrawerOpen(true)}
                />)}
            </div>
        </motion.header>

        {isMobile && (<Drawer
            title="Menu"
            placement="right"
            onClose={() => setDrawerOpen(false)}
            open={drawerOpen}
            size={280}
            styles={{
                body: {padding: '16px'}
            }}
            maskClosable={true}
            destroyOnClose={true}
        >
            <div className="flex flex-col gap-3">
                {!user ? (<>
                    <Link to="/login" onClick={() => setDrawerOpen(false)}>
                        <Button type="primary" block size="large">
                            Login
                        </Button>
                    </Link>
                    <Link to="/register" onClick={() => setDrawerOpen(false)}>
                        <Button block size="large">
                            Register
                        </Button>
                    </Link>
                </>) : (<>
                    <Link to="/dashboard" onClick={() => setDrawerOpen(false)}>
                        <Button type="primary" block size="large">
                            Dashboard
                        </Button>
                    </Link>
                    <Link to="/booking" onClick={() => setDrawerOpen(false)}>
                        <Button block size="large">
                            Book a Flight
                        </Button>
                    </Link>
                    <Button danger block size="large" onClick={handleLogout}>
                        Logout
                    </Button>
                </>)}
            </div>
        </Drawer>)}
    </>);
}

export default Header;
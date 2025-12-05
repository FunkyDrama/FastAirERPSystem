import React from "react";
import {ConfigProvider} from "antd";

function ResponsiveLayout({children}) {
    return (<ConfigProvider
        theme={{
            token: {
                screenXS: 480, screenSM: 576, screenMD: 768, screenLG: 992, screenXL: 1200, screenXXL: 1600,
            }, components: {
                Form: {
                    labelCol: {xs: 24, sm: 8}, wrapperCol: {xs: 24, sm: 16},
                },
            },
        }}
    >
        <div className="min-h-screen w-full">
            {children}
        </div>
    </ConfigProvider>);
}

export default ResponsiveLayout;
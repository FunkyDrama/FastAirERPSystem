export const AIRPORTS = {
    KBP: "Kyiv Boryspil",
    ODS: "Odesa",
    LWO: "Lviv",
    IEV: "Kyiv Zhulyany",
    DNK: "Dnipro",
    WAW: "Warsaw",
    KRK: "Krakow",
    GDN: "Gdansk",
    BER: "Berlin",
    MUC: "Munich",
    FRA: "Frankfurt",
    VIE: "Vienna",
    ZRH: "Zurich",
    CDG: "Paris Charles de Gaulle",
    AMS: "Amsterdam",
};


export function airportLabel(code, sep = " - ") {
    return code ? `${code}${sep}${AIRPORTS[code] || "Unknown"}` : "";
}

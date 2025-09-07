export const OPTIONS = {
    BAG_10KG: "Checked bag 10kg",
    BAG_20KG: "Checked bag 20kg",
    MEAL_STD: "Meal (standard)",
    MEAL_VEG: "Meal (vegetarian)",
    SEAT_CHOICE: "Seat selection",
    PRIORITY: "Priority boarding",
};

export const optionLabel = (name) => OPTIONS[name] || name;

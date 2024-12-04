create database iot_project_water_pump;

CREATE TABLE iot_project_water_pump.water_level_data (
    time DATETIME PRIMARY KEY,
    water_level DOUBLE
);
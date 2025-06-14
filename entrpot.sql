-- dim zones
CREATE TABLE DIM_ZONE (
    id_zone INT PRIMARY KEY,
    nom_zone VARCHAR(100)
);

--  dimension temps 
CREATE TABLE DIM_TEMPS (
    id_temps INT PRIMARY KEY,
    date DATE
);

--dimension alerte
CREATE TABLE DIM_ALERTE (
    id_alerte INT PRIMARY KEY,
    type_alerte VARCHAR(100),
    id_zone INT,
    nb_alerte int,
    FOREIGN KEY (id_zone) REFERENCES DIM_ZONE(id_zone)
);

--  dimension info
CREATE TABLE DIM_info (
    id_info INT PRIMARY KEY,
    chemin_video_avant VARCHAR(255),
    chemin_video_apres VARCHAR(255),
    csv_file varchar(255),
    graphe_file varchar(255),
    id_zone INT,
    FOREIGN KEY (id_zone) REFERENCES DIM_ZONE(id_zone)
);
--table de fait--
CREATE TABLE F_ZONE (
    id_zone INT,
    id_temps INT,
    id_alerte INT,
    id_info INT,
    nbr_chariot_detected INT,

    PRIMARY KEY (id_zone, id_temps, id_alerte, id_info),

    FOREIGN KEY (id_zone) REFERENCES DIM_ZONE(id_zone),
    FOREIGN KEY (id_temps) REFERENCES DIM_TEMPS(id_temps),
    FOREIGN KEY (id_alerte) REFERENCES DIM_ALERTE(id_alerte),
    FOREIGN KEY (id_info) REFERENCES DIM_info(id_info)
);

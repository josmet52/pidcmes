-- Batch pour la création de la base de donnee amod
-- 27.11.2020 Joseph Metrailler
-- --------------------------------------------------------------
-- si elle existe, supprimer la db existante et creer la nouvelle
DROP DATABASE IF EXISTS amod;
CREATE DATABASE amod;
USE amod;
-- --------------------------------------------------------------
-- table tlog pour les donnees
CREATE TABLE tlog
(
  t0 double NOT NULL,
  id int NOT NULL AUTO_INCREMENT,
  time_stamp timestamp NOT NULL,
  PRIMARY KEY (id),
  INDEX i_date (time_stamp),
  INDEX i_id (id),
  UNIQUE(id)
);

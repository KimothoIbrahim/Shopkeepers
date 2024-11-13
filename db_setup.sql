DROP DATABASE IF EXISTS `shopping_db`;
CREATE DATABASE IF NOT EXISTS `shopping_db`;

USE `shopping_db`;

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` INT auto_increment NOT NULL,
  `username` varchar(30) NOT NULL,
  `password` varchar(60) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(`id`)
);


DROP TABLE IF EXISTS `items`;
CREATE TABLE `items` (
  `id` INT auto_increment NOT NULL,
  `name` varchar(30) NOT NULL UNIQUE,
  `price` varchar(60) NOT NULL,
  `bp` varchar(60) NOT NULL,
  `barcode` varchar(60) NOT NULL UNIQUE,
  `image` varchar(60) NOT NULL DEFAULT "default.png",
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(`id`)
);

LOCK TABLES `items` WRITE;
INSERT INTO `items` (`name`, `price`, `bp`, `barcode`) VALUES ("Supaloaf bread", "65", "60", "23456129");
UNLOCK TABLES;

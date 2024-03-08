/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
SET NAMES utf8mb4;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE='NO_AUTO_VALUE_ON_ZERO', SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table cards
# ------------------------------------------------------------

CREATE TABLE `cards` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `set_id` varchar(10) DEFAULT NULL,
  `quantity` int DEFAULT NULL,
  `foil` varchar(20) DEFAULT NULL,
  `collector_number` varchar(10) DEFAULT NULL,
  `scryfall_id` varchar(50) NOT NULL,
  `color_identity` varchar(20) DEFAULT NULL,
  `type_line` varchar(250) DEFAULT NULL,
  `cmc` int DEFAULT NULL,
  `power` varchar(10) DEFAULT NULL,
  `toughness` varchar(10) DEFAULT NULL,
  `rarity` varchar(10) DEFAULT NULL,
  `text` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table decks
# ------------------------------------------------------------

CREATE TABLE `decks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `plains` int DEFAULT NULL,
  `island` int DEFAULT NULL,
  `swamp` int DEFAULT NULL,
  `mountain` int DEFAULT NULL,
  `forest` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



# Dump of table decks_cards
# ------------------------------------------------------------

CREATE TABLE `decks_cards` (
  `id` int NOT NULL AUTO_INCREMENT,
  `deck_id` int NOT NULL,
  `card_id` int NOT NULL,
  `is_commander` int DEFAULT NULL,
  `board` char(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `deck_id` (`deck_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: medicaldb
-- ------------------------------------------------------
-- Server version	9.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `appointment`
--

DROP TABLE IF EXISTS `appointment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appointment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `start_at` datetime NOT NULL,
  `end_at` datetime NOT NULL,
  `status` enum('PENDING','CONFIRMED','RESCHEDULED','CANCELED','COMPLETED') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reason` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cancel_reason` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fee` float DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `patient_id` int NOT NULL,
  `doctor_id` int NOT NULL,
  `schedule_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  KEY `doctor_id` (`doctor_id`),
  KEY `schedule_id` (`schedule_id`),
  CONSTRAINT `appointment_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `user` (`id`),
  CONSTRAINT `appointment_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctor_profile` (`id`),
  CONSTRAINT `appointment_ibfk_3` FOREIGN KEY (`schedule_id`) REFERENCES `schedule` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appointment`
--

LOCK TABLES `appointment` WRITE;
/*!40000 ALTER TABLE `appointment` DISABLE KEYS */;
INSERT INTO `appointment` VALUES (2,'2025-09-23 08:30:00','2025-09-23 09:00:00','COMPLETED','Đau đầu quá!',NULL,10000,'2025-09-23 05:04:27',11,2,2),(3,'2025-09-25 08:15:00','2025-09-25 08:45:00','CANCELED','Bé bị đau dạ dày.','Tôi vướng lịch đột xuất vào khung giờ đó. Vui lòng hẹn lịch vào giờ / ngày khác.',10000,'2025-09-25 12:38:18',11,2,2);
/*!40000 ALTER TABLE `appointment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `doctor_profile`
--

DROP TABLE IF EXISTS `doctor_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `doctor_profile` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `academic_degree` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `license_file` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_verified` tinyint(1) DEFAULT NULL,
  `specialty_id` int NOT NULL,
  `hospital_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `specialty_id` (`specialty_id`),
  KEY `hospital_id` (`hospital_id`),
  CONSTRAINT `doctor_profile_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `doctor_profile_ibfk_2` FOREIGN KEY (`specialty_id`) REFERENCES `specialty` (`id`),
  CONSTRAINT `doctor_profile_ibfk_3` FOREIGN KEY (`hospital_id`) REFERENCES `hospital` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `doctor_profile`
--

LOCK TABLES `doctor_profile` WRITE;
/*!40000 ALTER TABLE `doctor_profile` DISABLE KEYS */;
INSERT INTO `doctor_profile` VALUES (1,5,'Bác sĩ Chuyên Khoa II','https://res.cloudinary.com/dvn6qzq9o/image/upload/v1758504894/t5cil1znrzp9vbywlah8.png',1,1,1),(2,6,'Bác sĩ Chuyên Khoa II','https://res.cloudinary.com/dvn6qzq9o/image/upload/v1758514731/nqdizsuql5krmz49xe72.png',1,2,1),(3,7,'Bác sĩ Chuyên Khoa II','https://res.cloudinary.com/dvn6qzq9o/image/upload/v1758515025/ualkkbgfypcifgg7vdf5.png',1,4,1),(6,12,'Bác sĩ Chuyên Khoa I','https://res.cloudinary.com/dvn6qzq9o/image/upload/v1758626956/g1z0fhszcl6xhnauu15x.png',1,3,4);
/*!40000 ALTER TABLE `doctor_profile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hospital`
--

DROP TABLE IF EXISTS `hospital`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hospital` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `address` varchar(300) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hospital`
--

LOCK TABLES `hospital` WRITE;
/*!40000 ALTER TABLE `hospital` DISABLE KEYS */;
INSERT INTO `hospital` VALUES (1,'Bệnh viện Nguyễn Tri Phương','TP. HCM','...'),(2,'Bệnh viện Tâm Anh','TP. HCM','...'),(3,'Bệnh viện Thống Nhất','TP. HCM','...'),(4,'Bệnh viện Nhân dân 115','TP. HCM','...'),(5,'Bệnh viện Hùng Vương','TP. HCM','...');
/*!40000 ALTER TABLE `hospital` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medical_file`
--

DROP TABLE IF EXISTS `medical_file`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medical_file` (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_profile_id` int DEFAULT NULL,
  `medical_record_id` int DEFAULT NULL,
  `file_url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `uploaded_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `patient_profile_id` (`patient_profile_id`),
  KEY `medical_record_id` (`medical_record_id`),
  CONSTRAINT `medical_file_ibfk_1` FOREIGN KEY (`patient_profile_id`) REFERENCES `patient_profile` (`id`),
  CONSTRAINT `medical_file_ibfk_2` FOREIGN KEY (`medical_record_id`) REFERENCES `medical_record` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medical_file`
--

LOCK TABLES `medical_file` WRITE;
/*!40000 ALTER TABLE `medical_file` DISABLE KEYS */;
INSERT INTO `medical_file` VALUES (1,3,NULL,'https://res.cloudinary.com/dvn6qzq9o/image/upload/v1758711105/ulfhaba4v5e2hnkhbrtp.jpg','2025-09-24 17:51:46'),(2,3,NULL,'https://res.cloudinary.com/dvn6qzq9o/image/upload/v1758711494/huprcvtkheanqrblgrzc.jpg','2025-09-24 17:58:14');
/*!40000 ALTER TABLE `medical_file` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medical_record`
--

DROP TABLE IF EXISTS `medical_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medical_record` (
  `id` int NOT NULL AUTO_INCREMENT,
  `diagnosis` text COLLATE utf8mb4_unicode_ci,
  `test_results` text COLLATE utf8mb4_unicode_ci,
  `symptoms` text COLLATE utf8mb4_unicode_ci,
  `medical_history` text COLLATE utf8mb4_unicode_ci,
  `created_date` datetime DEFAULT NULL,
  `appointment_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `appointment_id` (`appointment_id`),
  CONSTRAINT `medical_record_ibfk_1` FOREIGN KEY (`appointment_id`) REFERENCES `appointment` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medical_record`
--

LOCK TABLES `medical_record` WRITE;
/*!40000 ALTER TABLE `medical_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `medical_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification`
--

DROP TABLE IF EXISTS `notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notification` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `type` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_read` tinyint(1) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `notification_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification`
--

LOCK TABLES `notification` WRITE;
/*!40000 ALTER TABLE `notification` DISABLE KEYS */;
INSERT INTO `notification` VALUES (1,1,'NEW_DOCTOR','Bác sĩ mới đăng ký: Thôi Thắng Triệt. Vui lòng xác thực.',0,'2025-09-22 08:34:55'),(2,5,'DOCTOR_VERIFICATION','Tài khoản bác sĩ của bạn đã được quản trị viên xác thực.',0,'2025-09-22 08:38:17'),(3,1,'NEW_DOCTOR','Bác sĩ mới đăng ký: Doãn Tịnh Hán. Vui lòng xác thực.',0,'2025-09-22 11:18:51'),(4,6,'DOCTOR_VERIFICATION','Tài khoản bác sĩ của bạn đã được quản trị viên xác thực.',0,'2025-09-22 11:20:37'),(5,1,'NEW_DOCTOR','Bác sĩ mới đăng ký: Hồng Trí Tú. Vui lòng xác thực.',0,'2025-09-22 11:23:45'),(6,7,'DOCTOR_VERIFICATION','Tài khoản bác sĩ của bạn đã được quản trị viên xác thực.',0,'2025-09-22 11:24:05'),(7,1,'NEW_DOCTOR','Bác sĩ mới đăng ký: Nguyễn Vanh. Vui lòng xác thực.',0,'2025-09-22 11:27:01'),(8,1,'NEW_DOCTOR','Bác sĩ mới đăng ký: Nguyễn Vanh. Vui lòng xác thực.',0,'2025-09-22 12:11:11'),(9,7,'APPOINTMENT','Bạn có lịch hẹn mới từ bệnh nhân Nguyễn Huỳnh Thanh Trúc.',0,'2025-09-22 23:23:55'),(10,4,'APPOINTMENT','Lịch hẹn của 1 đã bị hủy. Lý do: ',0,'2025-09-22 23:54:06'),(11,6,'APPOINTMENT','Bạn có lịch hẹn mới từ bệnh nhân Nguyễn Vanh.',0,'2025-09-23 05:04:27'),(12,11,'APPOINTMENT','Lịch hẹn 2 đã được bác sĩ xác nhận.',0,'2025-09-23 05:13:20'),(13,11,'APPOINTMENT','Lịch hẹn 2 đã hoàn thành.',0,'2025-09-23 05:14:24'),(14,1,'NEW_DOCTOR','Bác sĩ mới đăng ký: Văn Tuấn Huy. Vui lòng xác thực.',0,'2025-09-23 18:29:17'),(15,12,'DOCTOR_VERIFICATION','Tài khoản bác sĩ của bạn đã được quản trị viên xác thực.',0,'2025-09-23 18:31:20'),(16,6,'RATING','Bạn nhận được đánh giá mới từ bệnh nhân Nguyễn Vanh.',0,'2025-09-25 00:05:18'),(17,6,'APPOINTMENT','Bạn có lịch hẹn mới từ bệnh nhân Nguyễn Vanh.',0,'2025-09-25 12:38:18'),(18,6,'PAYMENT','Lịch hẹn 3 đã được tạo yêu cầu thanh toán.',0,'2025-09-25 12:47:01'),(19,11,'APPOINTMENT','Lịch hẹn của 3 đã bị hủy. Lý do: Tôi vướng lịch đột xuất vào khung giờ đó. Vui lòng hẹn lịch vào giờ / ngày khác.',0,'2025-09-25 13:14:45');
/*!40000 ALTER TABLE `notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patient_profile`
--

DROP TABLE IF EXISTS `patient_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patient_profile` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `blood_type` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `insurance_number` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `emergency_contact` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `allergies` text COLLATE utf8mb4_unicode_ci,
  `chronic_diseases` text COLLATE utf8mb4_unicode_ci,
  `disease_description` text COLLATE utf8mb4_unicode_ci,
  `test_results` text COLLATE utf8mb4_unicode_ci,
  `created_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `patient_profile_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient_profile`
--

LOCK TABLES `patient_profile` WRITE;
/*!40000 ALTER TABLE `patient_profile` DISABLE KEYS */;
INSERT INTO `patient_profile` VALUES (1,4,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-09-21 18:39:07'),(2,10,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-09-22 23:16:58'),(3,11,'AB','7938324575','0779708819','Những thứ tự nhiên','Không có.','Bị hở van tim khi còn nhỏ','Máu xấu','2025-09-22 23:18:47');
/*!40000 ALTER TABLE `patient_profile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `payment_method` enum('VNPAY','MOMO') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total_price` float NOT NULL,
  `status` enum('PENDING','SUCCESS','FAILED') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `transaction_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `appointment_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `appointment_id` (`appointment_id`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`appointment_id`) REFERENCES `appointment` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
INSERT INTO `payment` VALUES (1,'VNPAY',10000,'PENDING',NULL,'2025-09-25 12:47:01',3);
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rating`
--

DROP TABLE IF EXISTS `rating`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rating` (
  `id` int NOT NULL AUTO_INCREMENT,
  `stars` int NOT NULL,
  `comment` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `doctor_reply` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `patient_id` int NOT NULL,
  `doctor_id` int NOT NULL,
  `appointment_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `appointment_id` (`appointment_id`),
  KEY `patient_id` (`patient_id`),
  KEY `doctor_id` (`doctor_id`),
  CONSTRAINT `rating_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `user` (`id`),
  CONSTRAINT `rating_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctor_profile` (`id`),
  CONSTRAINT `rating_ibfk_3` FOREIGN KEY (`appointment_id`) REFERENCES `appointment` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rating`
--

LOCK TABLES `rating` WRITE;
/*!40000 ALTER TABLE `rating` DISABLE KEYS */;
INSERT INTO `rating` VALUES (1,5,'Bác sĩ rất tận tình.','Cảm ơn rất nhiều.','2025-09-25 00:05:18',11,2,2);
/*!40000 ALTER TABLE `rating` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schedule`
--

DROP TABLE IF EXISTS `schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schedule` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `is_available` tinyint(1) DEFAULT NULL,
  `doctor_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `doctor_id` (`doctor_id`),
  CONSTRAINT `schedule_ibfk_1` FOREIGN KEY (`doctor_id`) REFERENCES `doctor_profile` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schedule`
--

LOCK TABLES `schedule` WRITE;
/*!40000 ALTER TABLE `schedule` DISABLE KEYS */;
INSERT INTO `schedule` VALUES (2,'2025-09-23','08:00:00','09:00:00',1,2),(3,'2025-09-23','08:30:00','14:30:00',1,3);
/*!40000 ALTER TABLE `schedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `specialty`
--

DROP TABLE IF EXISTS `specialty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `specialty` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `specialty`
--

LOCK TABLES `specialty` WRITE;
/*!40000 ALTER TABLE `specialty` DISABLE KEYS */;
INSERT INTO `specialty` VALUES (1,'Tiêu hóa – Gan mật – Tụy','Khoa Tiêu hóa – Gan mật – Tụy ...'),(2,'Nhi','Khoa Nhi ...'),(3,'Ngoại Tổng hợp','Khoa Ngoại Tổng hợp ...'),(4,'Tim mạch','Khoa Tim mạch ...'),(5,'Nội Tổng hợp','Khoa Nội Tổng hợp ...');
/*!40000 ALTER TABLE `specialty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `address` varchar(300) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_of_birth` date NOT NULL,
  `gender` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(250) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(300) COLLATE utf8mb4_unicode_ci NOT NULL,
  `avatar` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_role` enum('PATIENT','DOCTOR','ADMIN') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Nguyễn Vân Anh','HCM','2003-07-18','Nữ','nguyenvananh9606@gmail.com','0932694738','zennen','21232f297a57a5a743894a0e4a801fc3','https://res.cloudinary.com/dvn6qzq9o/image/upload/v1713096443/Deen-Mustachio_lxrcg7.png','ADMIN','2025-09-21 00:17:57',1),(2,'Ngô Hoài Kiều Trinh','HCM','2004-09-09','Nữ','2254052086trinh@ou.edu.vn','0359526055','tina','21232f297a57a5a743894a0e4a801fc3','https://res.cloudinary.com/dvn6qzq9o/image/upload/v1713096443/Deen-Mustachio_lxrcg7.png','ADMIN','2025-09-21 00:17:57',1),(3,'Nguyễn Thị Thùy Dương','HCM','2003-08-11','Nữ','2251012044duong@ou.edu.vn','0387499939','daisy','21232f297a57a5a743894a0e4a801fc3','https://res.cloudinary.com/dvn6qzq9o/image/upload/v1713096461/61577e5045247.595ecab320c61_gydemz.png','ADMIN','2025-09-21 00:17:57',1),(4,'Nguyễn Huỳnh Thanh Trúc','HCM','2003-03-03','Nữ','trucnguyenhuynhthanh03@gmail.com','0933959003','ttruc03','45723a2af3788c4ff17f8d1114760e62','https://res.cloudinary.com/dvn6qzq9o/image/upload/v1758454746/wd4v2uwgek0p1dkb5s6o.jpg','PATIENT','2025-09-21 18:39:07',1),(5,'Thôi Thắng Triệt','Seoul, Korea','1995-08-08','Nam','tt.triet.01@svt.com.vn','0808199501','ttriet01','5b208189fc2071dd36a877ff680b3603','https://res.cloudinary.com/dvn6qzq9o/image/upload/v1758504893/e4fgw9yoke32x3v54ubs.jpg','DOCTOR','2025-09-22 08:34:54',1),(6,'Doãn Tịnh Hán','Seoul, Korea','1995-10-04','Nam','dt.han.02@svt.com.vn','0410199502','dthan02','7761127a460aaf290ed953098284dd1a','https://res.cloudinary.com/dvn6qzq9o/image/upload/v1758514730/cvsjcstyxejujqunrlcu.jpg','DOCTOR','2025-09-22 11:18:50',1),(7,'Hồng Trí Tú','Los Angeles, USA','1995-12-30','Nam','ht.tu.03@svt.com.vn','0301219953','ht.tu','65107b72460994495cad9a62ccdc8a79','https://res.cloudinary.com/dvn6qzq9o/image/upload/v1758515025/j4ehcoys6p6ezmbqonld.jpg','DOCTOR','2025-09-22 11:23:45',1),(10,'Võ Thùy Linh','HCM','2003-05-13','Nữ','2151053035linh@ou.edu.vn','0792366301','vtlinh','892da3d819056410c05bca7747d22735','https://res.cloudinary.com/dvn6qzq9o/image/upload/v1758557816/apfkvbyadgf3ke2ioqpv.jpg','PATIENT','2025-09-22 23:16:58',1),(11,'Nguyễn Vanh','HCM','2003-06-19','Nữ','2151050020anh@ou.edu.vn','0909855744','vanh39','54c396b330398e41e59682ae0b64749a','https://res.cloudinary.com/dvn6qzq9o/image/upload/v1758557926/buhcuhzkxetugzlzbifm.png','PATIENT','2025-09-22 23:18:47',1),(12,'Văn Tuấn Huy','China','1996-06-10','Nam','vt.huy.04@svt.com.vn','0610199604','thuy04','3cf2b6b121d1726bc2cdc88c39e0b119','https://res.cloudinary.com/dvn6qzq9o/image/upload/v1758626955/nisqk0pdmswydhwctz4r.jpg','DOCTOR','2025-09-23 18:29:16',1);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-25 14:02:55

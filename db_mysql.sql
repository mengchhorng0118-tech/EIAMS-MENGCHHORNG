-- ============================================================
-- EIAMS Database — MySQL / MariaDB Import File
-- BIU SAD Y3S1IT  |  Target: inventory_system database
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ── Table: `accounts_role` ──
DROP TABLE IF EXISTS `accounts_role`;
CREATE TABLE `accounts_role` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `role_name` varchar(50) NOT NULL UNIQUE, `description` text NULL, `created_at` datetime NOT NULL, `updated_at` datetime NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `accounts_role` (`id`, `role_name`, `description`, `created_at`, `updated_at`) VALUES
(1, 'Admin', 'This is  the admin real', '2026-07-24 11:41:44.054749', '2026-07-24 11:41:44.054811'),
(2, 'Super Admin', 'Full system access. Can manage all users, settings, and data.', '2026-07-27 11:21:55.077915', '2026-07-27 11:21:55.077941'),
(3, 'Manager', 'Can manage inventory, assets, stock movements, and reports.', '2026-07-27 11:21:55.089479', '2026-07-27 11:21:55.089492'),
(4, 'Staff', 'Can view inventory, record stock movements, and view reports.', '2026-07-27 11:21:55.099046', '2026-07-27 11:21:55.099073');


-- ── Table: `accounts_user` ──
DROP TABLE IF EXISTS `accounts_user`;
CREATE TABLE `accounts_user` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `password` varchar(128) NOT NULL, `last_login` datetime NULL, `is_superuser` TINYINT(1) NOT NULL, `username` varchar(150) NOT NULL UNIQUE, `first_name` varchar(150) NOT NULL, `last_name` varchar(150) NOT NULL, `is_staff` TINYINT(1) NOT NULL, `is_active` TINYINT(1) NOT NULL, `date_joined` datetime NOT NULL, `full_name` varchar(100) NOT NULL, `gender` varchar(10) NULL, `phone` varchar(20) NULL, `email` varchar(254) NOT NULL UNIQUE, `department` varchar(100) NULL, `status` varchar(20) NOT NULL, `profile_pic` varchar(100) NULL, `role_id` bigint NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `accounts_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `full_name`, `gender`, `phone`, `email`, `department`, `status`, `profile_pic`, `role_id`) VALUES
(1, 'pbkdf2_sha256$1200000$QxN2fsYSnX4axCKdBpDKcl$BPSHfyrA5GMs+xlmcSnTWjWZ5qqw36Xley9eNNatahw=', '2026-07-29 21:24:01.690561', 1, 'chhorng', '', '', 1, 0, '2026-07-24 08:40:26.328516', 'Mengchhorng', 'Male', '0882889089', 'chhorngjayx@gmail.com', 'MANAGER', 'Active', 'profiles/photo_2026-07-30_03-52-24.jpg', 1),
(2, 'pbkdf2_sha256$1200000$MKb0qbh1Rmg7p8tS9e71Hd$uovC21Sjv5FXPhX1FoUbyBkx47hRN1a1jBm9V4M+5Ak=', '2026-08-17 19:21:22.817737', 1, 'superadmin', 'Sophea', 'Keo', 1, 1, '2026-07-27 11:21:55.111201', 'Sophea Keo', 'Male', NULL, 'superadmin@eiams.com', 'IT Department', 'Active', '', 2),
(3, 'pbkdf2_sha256$1200000$OakKZXkTYuwqyojsayEfNF$qiFx2wMyJlR+GptHeSKy6jEfPrdnvet/rfcc3oBbDoc=', '2026-08-03 16:27:58.499912', 0, 'admin', 'Dara', 'Chan', 1, 1, '2026-07-27 11:21:55.768931', 'admin', 'Male', '0963003247', 'admin@eiams.com', 'Administration', 'Active', 'profiles/perfectmen_Oc3qClc.jpg', 1),
(4, 'pbkdf2_sha256$1200000$P4LYBc8VJcXpdrWEjetwA1$ZWNUW9DHBXp0409eZOusKKgBqS+4Zw0EFX/4Jy2s4f0=', '2026-08-17 19:20:46.243925', 0, 'manager', 'Sreymom', 'Pich', 0, 1, '2026-07-27 11:21:56.460993', 'Sreymom Pich', 'Female', '0882889089', 'manager@eiams.com', 'Operations', 'Active', 'profiles/bee_v5pUuVF.jpg', 3),
(5, 'pbkdf2_sha256$1200000$RpwaHxrCezfTEYzVYo2eYD$HNteAer7Zo/FtCRbTFkaIEQpnhbFjOzV1FPUjqeWO/Q=', NULL, 0, 'staff1', 'Borey', 'Nhem', 0, 0, '2026-07-27 11:21:57.054981', 'Borey Nhem', 'Male', NULL, 'borey@eiams.com', 'Warehouse', 'Inactive', '', 4),
(6, 'pbkdf2_sha256$1200000$WN7fJVVpIpn3JhGI5u3XaG$Fxr1KHup3cL3LAH0DqhfL5aeFioKAcbqz1byWS/GxbA=', '2026-08-03 09:11:49.516387', 0, 'staff2', 'Channary', 'Sok', 0, 1, '2026-07-27 11:21:57.515920', 'Channary Sok', 'Female', '0963003247', 'channary@eiams.com', 'Warehouse', 'Active', 'profiles/bee.jpg', 4),
(7, 'pbkdf2_sha256$1200000$9u2QiEqBnsdQZRUeoPKnST$24i0w7HcgWVTj06xIbxl8qZmlshJFDW1y2JsW0bZmzM=', NULL, 0, 'staff3', 'Virak', 'Mao', 0, 0, '2026-07-27 11:21:57.965983', 'Virak Mao', 'Male', NULL, 'virak@eiams.com', 'Procurement', 'Inactive', '', 4),
(8, 'pbkdf2_sha256$1200000$oNTamXqy1YvzHnrN66oTHb$ZrgyO+d2C6OO2PXgn/iCOaq0BpzogEQvyVaJn9eCAK8=', '2026-08-17 16:28:31.334688', 1, 'mengchhorng', 'MENGCHHORNG', '', 1, 1, '2026-07-30 12:55:11.075042', 'MENGCHHORNG', 'Male', '0963003247', 'mengchhorng@eiams.com', 'Administration', 'Active', 'profiles/men.jpg', 2),
(9, 'pbkdf2_sha256$1200000$m5mmthZmfAKd2gtn5Kv2Ph$A9BWpVL74vypqRAYphln9K0x4QN4dnX1Sos+dRMhRe0=', NULL, 0, 'Sovannara', '', '', 0, 0, '2026-08-03 11:39:31.991517', 'Sovannara', 'Male', '0963003247', 'sonvannara@gmail.com', 'Operations', 'Inactive', '', 3);


-- ── Table: `accounts_user_groups` ──
DROP TABLE IF EXISTS `accounts_user_groups`;
CREATE TABLE `accounts_user_groups` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `user_id` bigint NOT NULL, `group_id` integer NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table: `accounts_user_user_permissions` ──
DROP TABLE IF EXISTS `accounts_user_user_permissions`;
CREATE TABLE `accounts_user_user_permissions` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `user_id` bigint NOT NULL, `permission_id` integer NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table: `assets_asset` ──
DROP TABLE IF EXISTS `assets_asset`;
CREATE TABLE `assets_asset` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `asset_code` varchar(50) NOT NULL UNIQUE, `asset_name` varchar(150) NOT NULL, `serial_number` varchar(100) NULL UNIQUE, `barcode` varchar(100) NULL UNIQUE, `purchase_date` date NULL, `purchase_price` decimal NOT NULL, `warranty_expiry_date` date NULL, `asset_status` varchar(30) NOT NULL, `description` text NULL, `is_active` TINYINT(1) NOT NULL, `created_at` datetime NOT NULL, `updated_at` datetime NOT NULL, `assigned_to_id` bigint NULL, `category_id` bigint NOT NULL, `location_id` bigint NULL, `supplier_id` bigint NULL, `image` varchar(100) NULL, `image_url` varchar(500) NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `assets_asset` (`id`, `asset_code`, `asset_name`, `serial_number`, `barcode`, `purchase_date`, `purchase_price`, `warranty_expiry_date`, `asset_status`, `description`, `is_active`, `created_at`, `updated_at`, `assigned_to_id`, `category_id`, `location_id`, `supplier_id`, `image`, `image_url`) VALUES
(75, 'AST-PH-001', 'Apple iPhone 12 (128GB)', 'IP12-SN-0001', 'MB-IP12-0001', '2023-06-01', 549, '2025-06-01', 'Assigned', NULL, 1, '2026-08-17 18:21:23.069176', '2026-08-17 18:21:23.069191', 9, 17, 18, 16, 'assets/images/iphone12.svg', ''),
(76, 'AST-PH-002', 'Apple iPhone 12 (128GB)', 'IP12-SN-0002', 'MB-IP12-0002', '2023-06-01', 549, '2025-06-01', 'Assigned', NULL, 1, '2026-08-17 18:21:23.077495', '2026-08-17 18:21:23.077504', 9, 17, 20, 16, 'assets/images/iphone12.svg', ''),
(77, 'AST-PH-003', 'Apple iPhone 12 (256GB)', 'IP12-SN-0003', 'MB-IP12-0003', '2023-06-01', 599, '2025-06-01', 'Available', NULL, 1, '2026-08-17 18:21:23.085152', '2026-08-17 18:21:23.085161', NULL, 17, 17, 16, 'assets/images/iphone12.svg', ''),
(78, 'AST-PH-004', 'Apple iPhone 13 (128GB)', 'IP13-SN-0001', 'MB-IP13-0001', '2023-09-20', 599, '2025-09-20', 'Assigned', NULL, 1, '2026-08-17 18:21:23.093546', '2026-08-17 18:21:23.093557', 9, 17, 18, 16, 'assets/images/iphone13.svg', ''),
(79, 'AST-PH-005', 'Apple iPhone 13 (128GB)', 'IP13-SN-0002', 'MB-IP13-0002', '2023-09-20', 599, '2025-09-20', 'Assigned', NULL, 1, '2026-08-17 18:21:23.102369', '2026-08-17 18:21:23.102379', 9, 17, 21, 16, 'assets/images/iphone13.svg', ''),
(80, 'AST-PH-006', 'Apple iPhone 13 (256GB)', 'IP13-SN-0003', 'MB-IP13-0003', '2023-09-20', 649, '2025-09-20', 'Available', NULL, 1, '2026-08-17 18:21:23.110342', '2026-08-17 18:21:23.110351', NULL, 17, 19, 16, 'assets/images/iphone13.svg', ''),
(81, 'AST-PH-007', 'Apple iPhone 14 (128GB)', 'IP14-SN-0001', 'MB-IP14-0001', '2023-12-10', 699, '2025-12-10', 'Assigned', NULL, 1, '2026-08-17 18:21:23.118444', '2026-08-17 18:21:23.118455', 9, 17, 18, 16, 'assets/images/iphone14.svg', ''),
(82, 'AST-PH-008', 'Apple iPhone 14 (128GB)', 'IP14-SN-0002', 'MB-IP14-0002', '2023-12-10', 699, '2025-12-10', 'Assigned', NULL, 1, '2026-08-17 18:21:23.128380', '2026-08-17 18:21:23.128390', 9, 17, 20, 16, 'assets/images/iphone14.svg', ''),
(83, 'AST-PH-009', 'Apple iPhone 14 (256GB)', 'IP14-SN-0003', 'MB-IP14-0003', '2023-12-10', 749, '2025-12-10', 'Available', NULL, 1, '2026-08-17 18:21:23.137597', '2026-08-17 18:21:23.137607', NULL, 17, 17, 16, 'assets/images/iphone14.svg', ''),
(84, 'AST-PH-010', 'Apple iPhone 14 (256GB)', 'IP14-SN-0004', 'MB-IP14-0004', '2023-12-10', 749, '2025-12-10', 'Under Maintenance', NULL, 1, '2026-08-17 18:21:23.146807', '2026-08-17 18:21:23.146817', NULL, 17, 19, 16, 'assets/images/iphone14.svg', ''),
(85, 'AST-PH-011', 'Apple iPhone 14 Pro (256GB)', 'IP14P-SN-0001', 'MB-IP14P-0001', '2024-01-15', 999, '2026-01-15', 'Assigned', NULL, 1, '2026-08-17 18:21:23.156350', '2026-08-17 18:21:23.156360', 9, 17, 18, 17, 'assets/images/iphone14pro.svg', ''),
(86, 'AST-PH-012', 'Apple iPhone 14 Pro (256GB)', 'IP14P-SN-0002', 'MB-IP14P-0002', '2024-01-15', 999, '2026-01-15', 'Available', NULL, 1, '2026-08-17 18:21:23.165486', '2026-08-17 18:21:23.165495', NULL, 17, 19, 17, 'assets/images/iphone14pro.svg', ''),
(87, 'AST-PH-013', 'Apple iPhone 15 (128GB)', 'IP15-SN-0001', 'MB-IP15-0001', '2024-03-15', 799, '2026-03-15', 'Assigned', NULL, 1, '2026-08-17 18:21:23.174366', '2026-08-17 18:21:23.174375', 9, 17, 18, 16, 'assets/images/iphone15.svg', ''),
(88, 'AST-PH-014', 'Apple iPhone 15 (128GB)', 'IP15-SN-0002', 'MB-IP15-0002', '2024-03-15', 799, '2026-03-15', 'Assigned', NULL, 1, '2026-08-17 18:21:23.183299', '2026-08-17 18:21:23.183308', 9, 17, 21, 16, 'assets/images/iphone15.svg', ''),
(89, 'AST-PH-015', 'Apple iPhone 15 (256GB)', 'IP15-SN-0003', 'MB-IP15-0003', '2024-03-15', 859, '2026-03-15', 'Assigned', NULL, 1, '2026-08-17 18:21:23.191744', '2026-08-17 18:21:23.191754', 9, 17, 20, 16, 'assets/images/iphone15.svg', ''),
(90, 'AST-PH-016', 'Apple iPhone 15 Pro (256GB)', 'IP15P-SN-0001', 'MB-IP15P-0001', '2024-04-01', 999, '2026-04-01', 'Assigned', NULL, 1, '2026-08-17 18:21:23.201478', '2026-08-17 18:21:23.201487', 9, 17, 18, 17, 'assets/images/iphone15pro.svg', ''),
(91, 'AST-PH-017', 'Apple iPhone 15 Pro (256GB)', 'IP15P-SN-0002', 'MB-IP15P-0002', '2024-04-01', 999, '2026-04-01', 'Available', NULL, 1, '2026-08-17 18:21:23.209710', '2026-08-17 18:21:23.209721', NULL, 17, 19, 17, 'assets/images/iphone15pro.svg', ''),
(92, 'AST-PH-018', 'Apple iPhone 15 Pro Max (512GB)', 'IP15PM-SN-0001', 'MB-IP15PM-0001', '2024-04-15', 1199, '2026-04-15', 'Assigned', NULL, 1, '2026-08-17 18:21:23.219263', '2026-08-17 18:21:23.219273', 9, 17, 18, 17, 'assets/images/iphone15pro.svg', ''),
(93, 'AST-PH-019', 'Apple iPhone 16 (128GB)', 'IP16-SN-0001', 'MB-IP16-0001', '2024-10-01', 899, '2026-10-01', 'Assigned', NULL, 1, '2026-08-17 18:21:23.227534', '2026-08-17 18:21:23.227546', 9, 17, 18, 16, 'assets/images/iphone16.svg', ''),
(94, 'AST-PH-020', 'Apple iPhone 16 (128GB)', 'IP16-SN-0002', 'MB-IP16-0002', '2024-10-01', 899, '2026-10-01', 'Assigned', NULL, 1, '2026-08-17 18:21:23.237434', '2026-08-17 18:21:23.237444', 9, 17, 20, 16, 'assets/images/iphone16.svg', ''),
(95, 'AST-PH-021', 'Apple iPhone 16 (256GB)', 'IP16-SN-0003', 'MB-IP16-0003', '2024-10-01', 959, '2026-10-01', 'Available', NULL, 1, '2026-08-17 18:21:23.245495', '2026-08-17 18:21:23.245504', NULL, 17, 17, 16, 'assets/images/iphone16.svg', ''),
(96, 'AST-PH-022', 'Apple iPhone 16 Pro (256GB)', 'IP16P-SN-0001', 'MB-IP16P-0001', '2024-10-15', 1099, '2026-10-15', 'Assigned', NULL, 1, '2026-08-17 18:21:23.253234', '2026-08-17 18:21:23.253243', 9, 17, 18, 17, 'assets/images/iphone16pro.svg', ''),
(97, 'AST-PH-023', 'Apple iPhone 16 Pro (256GB)', 'IP16P-SN-0002', 'MB-IP16P-0002', '2024-10-15', 1099, '2026-10-15', 'Available', NULL, 1, '2026-08-17 18:21:23.261326', '2026-08-17 18:21:23.261335', NULL, 17, 19, 17, 'assets/images/iphone16pro.svg', ''),
(98, 'AST-PH-024', 'Apple iPhone 16 Pro Max (512GB)', 'IP16PM-SN-0001', 'MB-IP16PM-0001', '2024-11-01', 1299, '2026-11-01', 'Assigned', NULL, 1, '2026-08-17 18:21:23.269234', '2026-08-17 18:21:23.269244', 9, 17, 18, 17, 'assets/images/iphone16pro.svg', ''),
(99, 'AST-PH-025', 'Apple iPhone 17 (256GB)', 'IP17-SN-0001', 'MB-IP17-0001', '2025-04-01', 1099, '2027-04-01', 'Assigned', NULL, 1, '2026-08-17 18:21:23.277398', '2026-08-17 18:21:23.277408', 9, 17, 18, 16, 'assets/images/iphone17.svg', ''),
(100, 'AST-PH-026', 'Apple iPhone 17 (256GB)', 'IP17-SN-0002', 'MB-IP17-0002', '2025-04-01', 1099, '2027-04-01', 'Assigned', NULL, 1, '2026-08-17 18:21:23.285447', '2026-08-17 18:21:23.285457', 9, 17, 20, 16, 'assets/images/iphone17.svg', ''),
(101, 'AST-PH-027', 'Apple iPhone 17 (512GB)', 'IP17-SN-0003', 'MB-IP17-0003', '2025-04-01', 1199, '2027-04-01', 'Available', NULL, 1, '2026-08-17 18:21:23.293246', '2026-08-17 18:21:23.293257', NULL, 17, 17, 16, 'assets/images/iphone17.svg', ''),
(102, 'AST-PH-028', 'Apple iPhone 17 Pro (256GB)', 'IP17P-SN-0001', 'MB-IP17P-0001', '2025-04-15', 1299, '2027-04-15', 'Assigned', NULL, 1, '2026-08-17 18:21:23.301341', '2026-08-17 18:21:23.301351', 9, 17, 18, 17, 'assets/images/iphone17pro.svg', ''),
(103, 'AST-PH-029', 'Apple iPhone 17 Pro (512GB)', 'IP17P-SN-0002', 'MB-IP17P-0002', '2025-04-15', 1399, '2027-04-15', 'Available', NULL, 1, '2026-08-17 18:21:23.309351', '2026-08-17 18:21:23.309363', NULL, 17, 19, 17, 'assets/images/iphone17pro.svg', ''),
(104, 'AST-PH-030', 'Apple iPhone 17 Pro Max (512GB)', 'IP17PM-SN-0001', 'MB-IP17PM-0001', '2025-05-01', 1499, '2027-05-01', 'Assigned', NULL, 1, '2026-08-17 18:21:23.318605', '2026-08-17 18:21:23.318615', 9, 17, 18, 17, 'assets/images/iphone17pro.svg', ''),
(105, 'AST-PH-031', 'Apple iPhone 17 Pro Max (512GB)', 'IP17PM-SN-0002', 'MB-IP17PM-0002', '2025-05-01', 1499, '2027-05-01', 'Available', NULL, 1, '2026-08-17 18:21:23.327238', '2026-08-17 18:21:23.327247', NULL, 17, 22, 17, 'assets/images/iphone17pro.svg', '');


-- ── Table: `assets_assetauditlog` ──
DROP TABLE IF EXISTS `assets_assetauditlog`;
CREATE TABLE `assets_assetauditlog` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `audit_date` date NOT NULL, `condition_status` varchar(50) NOT NULL, `remarks` text NULL, `created_at` datetime NOT NULL, `asset_id` bigint NOT NULL, `checked_by_id` bigint NOT NULL, `location_id` bigint NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table: `assets_assetdisposal` ──
DROP TABLE IF EXISTS `assets_assetdisposal`;
CREATE TABLE `assets_assetdisposal` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `disposal_date` date NOT NULL, `disposal_reason` text NOT NULL, `disposal_value` decimal NOT NULL, `status` varchar(30) NOT NULL, `remarks` text NULL, `approved_at` datetime NULL, `created_at` datetime NOT NULL, `approved_by_id` bigint NULL, `asset_id` bigint NOT NULL, `disposed_by_id` bigint NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table: `assets_assettransfer` ──
DROP TABLE IF EXISTS `assets_assettransfer`;
CREATE TABLE `assets_assettransfer` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `transfer_number` varchar(30) NOT NULL UNIQUE, `transfer_date` date NOT NULL, `receive_date` date NULL, `approved_at` datetime NULL, `completed_at` datetime NULL, `status` varchar(20) NOT NULL, `reason` text NOT NULL, `notes` text NULL, `rejection_reason` text NULL, `attachment` varchar(100) NULL, `created_at` datetime NOT NULL, `updated_at` datetime NOT NULL, `approved_by_id` bigint NULL, `asset_id` bigint NOT NULL, `from_location_id` bigint NOT NULL, `received_by_id` bigint NULL, `requested_by_id` bigint NOT NULL, `to_location_id` bigint NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table: `assets_maintenancerecord` ──
DROP TABLE IF EXISTS `assets_maintenancerecord`;
CREATE TABLE `assets_maintenancerecord` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `maintenance_date` date NOT NULL, `maintenance_type` varchar(50) NOT NULL, `issue_description` text NULL, `cost` decimal NOT NULL, `performed_by` varchar(100) NULL, `status` varchar(30) NOT NULL, `remarks` text NULL, `created_at` datetime NOT NULL, `updated_at` datetime NOT NULL, `asset_id` bigint NOT NULL, `created_by_id` bigint NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table: `assets_transferhistory` ──
DROP TABLE IF EXISTS `assets_transferhistory`;
CREATE TABLE `assets_transferhistory` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `old_status` varchar(20) NULL, `new_status` varchar(20) NOT NULL, `notes` text NULL, `timestamp` datetime NOT NULL, `changed_by_id` bigint NULL, `transfer_id` bigint NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table: `auth_group` ──
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `name` varchar(150) NOT NULL UNIQUE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table: `auth_group_permissions` ──
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `group_id` integer NOT NULL, `permission_id` integer NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table: `auth_permission` ──
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `content_type_id` integer NOT NULL, `codename` varchar(100) NOT NULL, `name` varchar(255) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `auth_permission` (`id`, `content_type_id`, `codename`, `name`) VALUES
(1, 1, 'add_logentry', 'Can add log entry'),
(2, 1, 'change_logentry', 'Can change log entry'),
(3, 1, 'delete_logentry', 'Can delete log entry'),
(4, 1, 'view_logentry', 'Can view log entry'),
(5, 3, 'add_permission', 'Can add permission'),
(6, 3, 'change_permission', 'Can change permission'),
(7, 3, 'delete_permission', 'Can delete permission'),
(8, 3, 'view_permission', 'Can view permission'),
(9, 2, 'add_group', 'Can add group'),
(10, 2, 'change_group', 'Can change group'),
(11, 2, 'delete_group', 'Can delete group'),
(12, 2, 'view_group', 'Can view group'),
(13, 4, 'add_contenttype', 'Can add content type'),
(14, 4, 'change_contenttype', 'Can change content type'),
(15, 4, 'delete_contenttype', 'Can delete content type'),
(16, 4, 'view_contenttype', 'Can view content type'),
(17, 5, 'add_session', 'Can add session'),
(18, 5, 'change_session', 'Can change session'),
(19, 5, 'delete_session', 'Can delete session'),
(20, 5, 'view_session', 'Can view session'),
(21, 6, 'add_role', 'Can add Role'),
(22, 6, 'change_role', 'Can change Role'),
(23, 6, 'delete_role', 'Can delete Role'),
(24, 6, 'view_role', 'Can view Role'),
(25, 7, 'add_user', 'Can add User'),
(26, 7, 'change_user', 'Can change User'),
(27, 7, 'delete_user', 'Can delete User'),
(28, 7, 'view_user', 'Can view User'),
(29, 10, 'add_location', 'Can add Location'),
(30, 10, 'change_location', 'Can change Location'),
(31, 10, 'delete_location', 'Can delete Location'),
(32, 10, 'view_location', 'Can view Location'),
(33, 9, 'add_inventoryitem', 'Can add Inventory Item'),
(34, 9, 'change_inventoryitem', 'Can change Inventory Item'),
(35, 9, 'delete_inventoryitem', 'Can delete Inventory Item'),
(36, 9, 'view_inventoryitem', 'Can view Inventory Item'),
(37, 8, 'add_category', 'Can add Category'),
(38, 8, 'change_category', 'Can change Category'),
(39, 8, 'delete_category', 'Can delete Category'),
(40, 8, 'view_category', 'Can view Category'),
(41, 11, 'add_supplier', 'Can add Supplier'),
(42, 11, 'change_supplier', 'Can change Supplier'),
(43, 11, 'delete_supplier', 'Can delete Supplier'),
(44, 11, 'view_supplier', 'Can view Supplier'),
(45, 16, 'add_maintenancerecord', 'Can add Maintenance Record'),
(46, 16, 'change_maintenancerecord', 'Can change Maintenance Record'),
(47, 16, 'delete_maintenancerecord', 'Can delete Maintenance Record'),
(48, 16, 'view_maintenancerecord', 'Can view Maintenance Record'),
(49, 12, 'add_asset', 'Can add Asset'),
(50, 12, 'change_asset', 'Can change Asset'),
(51, 12, 'delete_asset', 'Can delete Asset'),
(52, 12, 'view_asset', 'Can view Asset'),
(53, 13, 'add_assetauditlog', 'Can add Asset Audit Log'),
(54, 13, 'change_assetauditlog', 'Can change Asset Audit Log'),
(55, 13, 'delete_assetauditlog', 'Can delete Asset Audit Log'),
(56, 13, 'view_assetauditlog', 'Can view Asset Audit Log'),
(57, 14, 'add_assetdisposal', 'Can add Asset Disposal'),
(58, 14, 'change_assetdisposal', 'Can change Asset Disposal'),
(59, 14, 'delete_assetdisposal', 'Can delete Asset Disposal'),
(60, 14, 'view_assetdisposal', 'Can view Asset Disposal'),
(61, 15, 'add_assettransfer', 'Can add Asset Transfer'),
(62, 15, 'change_assettransfer', 'Can change Asset Transfer'),
(63, 15, 'delete_assettransfer', 'Can delete Asset Transfer'),
(64, 15, 'view_assettransfer', 'Can view Asset Transfer'),
(65, 18, 'add_stockmovement', 'Can add Stock Movement'),
(66, 18, 'change_stockmovement', 'Can change Stock Movement'),
(67, 18, 'delete_stockmovement', 'Can delete Stock Movement'),
(68, 18, 'view_stockmovement', 'Can view Stock Movement'),
(69, 17, 'add_lowstockalert', 'Can add Low Stock Alert'),
(70, 17, 'change_lowstockalert', 'Can change Low Stock Alert'),
(71, 17, 'delete_lowstockalert', 'Can delete Low Stock Alert'),
(72, 17, 'view_lowstockalert', 'Can view Low Stock Alert'),
(73, 19, 'add_notification', 'Can add Notification'),
(74, 19, 'change_notification', 'Can change Notification'),
(75, 19, 'delete_notification', 'Can delete Notification'),
(76, 19, 'view_notification', 'Can view Notification'),
(77, 15, 'can_approve_transfer', 'Can approve / reject asset transfers'),
(78, 15, 'can_complete_transfer', 'Can mark transfer as completed'),
(79, 20, 'add_transferhistory', 'Can add Transfer History'),
(80, 20, 'change_transferhistory', 'Can change Transfer History'),
(81, 20, 'delete_transferhistory', 'Can delete Transfer History'),
(82, 20, 'view_transferhistory', 'Can view Transfer History');


-- ── Table: `django_admin_log` ──
DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `object_id` text NULL, `object_repr` varchar(200) NOT NULL, `action_flag` smallint unsigned NOT NULL CHECK (`action_flag` >= 0), `change_message` text NOT NULL, `content_type_id` integer NULL, `user_id` bigint NOT NULL, `action_time` datetime NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `django_admin_log` (`id`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`, `action_time`) VALUES
(1, '1', 'Admin', 1, '[{"added": {}}]', 6, 1, '2026-07-24 11:41:44.059666'),
(2, '1', 'Cambodia (Inventory)', 1, '[{"added": {}}]', 8, 1, '2026-07-24 11:42:46.607624'),
(3, '1', 'mengchhorng', 1, '[{"added": {}}]', 11, 1, '2026-07-24 11:43:14.333819'),
(4, '1', 'jomjav (Branch)', 1, '[{"added": {}}]', 10, 1, '2026-07-24 11:43:42.690496'),
(5, '2', 'LOW STOCK: Floor Cleaner 5L | Current: 10 | Min: 10', 1, '[{"added": {}}]', 17, 1, '2026-07-29 16:07:25.479620'),
(6, '2', 'LOW STOCK: Floor Cleaner 5L | Current: 10 | Min: 10', 2, '[]', 17, 1, '2026-07-29 16:07:28.780032'),
(7, '16', 'Stock IN | INV-0011 | Qty: 10 | 2026-07-29', 1, '[{"added": {}}]', 18, 1, '2026-07-29 16:08:58.026712'),
(8, '16', 'Stock IN | INV-0001 | Qty: 10 | 2026-07-29', 2, '[{"changed": {"fields": ["Inventory Item"]}}]', 18, 1, '2026-07-29 16:10:15.527991'),
(9, '17', 'Stock IN | INV-0019 | Qty: 10 | 2026-07-29', 1, '[{"added": {}}]', 18, 1, '2026-07-29 16:14:31.334525'),
(10, '18', 'Stock OUT | INV-0019 | Qty: 12 | 2026-07-29', 1, '[{"added": {}}]', 18, 1, '2026-07-29 16:17:01.122274'),
(11, '21', '#22 - BROSJM', 1, '[{"added": {}}]', 9, 1, '2026-07-29 16:19:09.737953'),
(12, '21', '#22 - BROSJM', 2, '[]', 9, 1, '2026-07-29 16:19:33.127227'),
(13, '9', 'TATA (Tata)', 1, '[{"added": {}}]', 7, 8, '2026-08-03 11:39:32.484722'),
(14, '1', 'Audit: AST-0006 | Good | 2026-08-03', 1, '[{"added": {}}]', 13, 8, '2026-08-03 11:39:56.647469');


-- ── Table: `django_content_type` ──
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `app_label` varchar(100) NOT NULL, `model` varchar(100) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(2, 'auth', 'group'),
(3, 'auth', 'permission'),
(4, 'contenttypes', 'contenttype'),
(5, 'sessions', 'session'),
(6, 'accounts', 'role'),
(7, 'accounts', 'user'),
(8, 'inventory', 'category'),
(9, 'inventory', 'inventoryitem'),
(10, 'inventory', 'location'),
(11, 'inventory', 'supplier'),
(12, 'assets', 'asset'),
(13, 'assets', 'assetauditlog'),
(14, 'assets', 'assetdisposal'),
(15, 'assets', 'assettransfer'),
(16, 'assets', 'maintenancerecord'),
(17, 'stock', 'lowstockalert'),
(18, 'stock', 'stockmovement'),
(19, 'notifications', 'notification'),
(20, 'assets', 'transferhistory');


-- ── Table: `django_migrations` ──
DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `app` varchar(255) NOT NULL, `name` varchar(255) NOT NULL, `applied` datetime NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-07-24 08:39:21.585830'),
(2, 'contenttypes', '0002_remove_content_type_name', '2026-07-24 08:39:21.864486'),
(3, 'auth', '0001_initial', '2026-07-24 08:39:21.944882'),
(4, 'auth', '0002_alter_permission_name_max_length', '2026-07-24 08:39:21.961857'),
(5, 'auth', '0003_alter_user_email_max_length', '2026-07-24 08:39:21.979312'),
(6, 'auth', '0004_alter_user_username_opts', '2026-07-24 08:39:21.992503'),
(7, 'auth', '0005_alter_user_last_login_null', '2026-07-24 08:39:22.004273'),
(8, 'auth', '0006_require_contenttypes_0002', '2026-07-24 08:39:22.014174'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2026-07-24 08:39:22.025574'),
(10, 'auth', '0008_alter_user_username_max_length', '2026-07-24 08:39:22.038620'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2026-07-24 08:39:22.050454'),
(12, 'auth', '0010_alter_group_name_max_length', '2026-07-24 08:39:22.064497'),
(13, 'auth', '0011_update_proxy_permissions', '2026-07-24 08:39:22.076124'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2026-07-24 08:39:22.088050'),
(15, 'accounts', '0001_initial', '2026-07-24 08:39:22.111036'),
(16, 'admin', '0001_initial', '2026-07-24 08:39:22.132851'),
(17, 'admin', '0002_logentry_remove_auto_add', '2026-07-24 08:39:22.149148'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2026-07-24 08:39:22.161787'),
(19, 'sessions', '0001_initial', '2026-07-24 08:39:22.180883'),
(20, 'inventory', '0001_initial', '2026-07-24 08:51:57.668416'),
(22, 'notifications', '0001_initial', '2026-07-24 08:56:49.428295'),
(23, 'stock', '0001_initial', '2026-07-24 08:56:49.464096'),
(25, 'inventory', '0002_add_item_name_km', '2026-07-29 16:48:14.460010'),
(26, 'assets', '0001_initial', '2026-08-03 09:42:18.811214'),
(27, 'assets', '0002_asset_image_asset_image_url', '2026-08-17 15:34:20.914686'),
(28, 'inventory', '0003_inventoryitem_image_inventoryitem_image_url', '2026-08-17 15:34:20.933738');


-- ── Table: `django_session` ──
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (`session_key` varchar(40) NOT NULL PRIMARY KEY, `session_data` text NOT NULL, `expire_date` datetime NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('jiv152v11k3ag7ay7rie9fvoycdlkjf6', '.eJxVjEEOwiAUBe_C2hAoFKRL956BfOAjqAEDbaIx3t2QdKHbN_PmTSxsa7Jbx2ZzIAvh5PC7OfA3LAOEK5RLpb6WtWVHh0J32um5BryfdvcvkKCn8Q7RTGC8n44zmyTy4KX2CqUWs-NaCSUMAyGjQq0dM2CUVOgC6MiFETiiHXvPtVh8PnJ7kYV9voY8PvA:1wnBeo:YZOKIVDg6OD7kgtIHJsafQADl6vmrU2ciIRQRbuiJRc', '2026-07-24 10:53:26.029029'),
('7d8yqgdoq6xonah3vevjs7qokck6g2mu', '.eJxVjEEOwiAUBe_C2hAoFKRL956BfOAjqAEDbaIx3t2QdKHbN_PmTSxsa7Jbx2ZzIAvh5PC7OfA3LAOEK5RLpb6WtWVHh0J32um5BryfdvcvkKCn8Q7RTGC8n44zmyTy4KX2CqUWs-NaCSUMAyGjQq0dM2CUVOgC6MiFETiiHXvPtVh8PnJ7kYV9voY8PvA:1wnCWP:NZYYkDUrlu_9bEaiGh1nziPGZfrGl7PqAl9Ht8rDcsM', '2026-07-24 11:48:49.151612'),
('hk3787pw4zgwefsejrujs3msc50p3pgl', '.eJxVjEEOwiAUBe_C2hAoFKRL956BfOAjqAEDbaIx3t2QdKHbN_PmTSxsa7Jbx2ZzIAvh5PC7OfA3LAOEK5RLpb6WtWVHh0J32um5BryfdvcvkKCn8Q7RTGC8n44zmyTy4KX2CqUWs-NaCSUMAyGjQq0dM2CUVOgC6MiFETiiHXvPtVh8PnJ7kYV9voY8PvA:1wnEQA:-nj9IvuaE5niO2NM0TpRsD5b0D-ANdGZ-j51llqU9DQ', '2026-07-24 13:50:30.652960'),
('nmbupvf7c525c5cenp43ngkxcqriw240', '.eJxVjEEOwiAUBe_C2hAoFKRL956BfOAjqAEDbaIx3t2QdKHbN_PmTSxsa7Jbx2ZzIAvh5PC7OfA3LAOEK5RLpb6WtWVHh0J32um5BryfdvcvkKCn8Q7RTGC8n44zmyTy4KX2CqUWs-NaCSUMAyGjQq0dM2CUVOgC6MiFETiiHXvPtVh8PnJ7kYV9voY8PvA:1woJB3:f6ShpXFNN6rREvrC0YdQY4eZyLweDuCgONSswIHbyuk', '2026-07-27 13:07:21.590297'),
('84vmzszud14y1yicm3m0lml9mvx03m4j', '.eJxVjEEOwiAUBe_C2hAoFKRL956BfOAjqAEDbaIx3t2QdKHbN_PmTSxsa7Jbx2ZzIAvh5PC7OfA3LAOEK5RLpb6WtWVHh0J32um5BryfdvcvkKCn8Q7RTGC8n44zmyTy4KX2CqUWs-NaCSUMAyGjQq0dM2CUVOgC6MiFETiiHXvPtVh8PnJ7kYV9voY8PvA:1woKT9:Ivw70cn1szDBEqTMlLUx9tFrEgnuD4Om0SstZDqvxg0', '2026-07-27 14:30:07.085443'),
('2opcy4m7wy1thwphvassieo977swpleu', '.eJxVjEEOwiAQRe_C2hDrUEq6dO8ZyMwwtagBA21SY7y71nSh2__ef0_lcZ5GP1cpPgbVq4Pa_W6EfJW0gnDBdM6ac5pKJL0qeqNVn3KQ23Fz_wIj1vHzbgNYywyNaSwaFiYm5yw2XTvw4ASIHBC3hKsQnEgQMAOw6TrD8I1WqTXm5GW5x_JQ_f71BskIQFw:1woKUZ:iihPhd_DVGrpjr2HBsf1yPdyK7595tgxiaJfkESYpCw', '2026-07-27 14:31:35.532767'),
('2i7bpwshm2w7zhl0g4hfarjxjk6fqsro', '.eJxVjEEOwiAUBe_C2hAoFKRL956BfOAjqAEDbaIx3t2QdKHbN_PmTSxsa7Jbx2ZzIAvh5PC7OfA3LAOEK5RLpb6WtWVHh0J32um5BryfdvcvkKCn8Q7RTGC8n44zmyTy4KX2CqUWs-NaCSUMAyGjQq0dM2CUVOgC6MiFETiiHXvPtVh8PnJ7kYV9voY8PvA:1woL10:FuqTDwvkXk-KYV9ac-j5f8aQ6rS2p74t5p3K9kj8kso', '2026-07-27 15:05:06.234721'),
('2wbtdt2vdfuefwz50qbzhxgn9skwo07c', '.eJxVjEEOwiAUBe_C2hAoFKRL956BfOAjqAEDbaIx3t2QdKHbN_PmTSxsa7Jbx2ZzIAvh5PC7OfA3LAOEK5RLpb6WtWVHh0J32um5BryfdvcvkKCn8Q7RTGC8n44zmyTy4KX2CqUWs-NaCSUMAyGjQq0dM2CUVOgC6MiFETiiHXvPtVh8PnJ7kYV9voY8PvA:1woL3U:N4qBl_0RYxZ0G4OsTgA4RtzlWXfBN_UIcf_DSy3w_uE', '2026-07-27 15:07:40.139437'),
('zmwkqno9qzu4jlvezpa13tw36x2m5w48', '.eJxVjEEOwiAUBe_C2hAoFKRL956BfOAjqAEDbaIx3t2QdKHbN_PmTSxsa7Jbx2ZzIAvh5PC7OfA3LAOEK5RLpb6WtWVHh0J32um5BryfdvcvkKCn8Q7RTGC8n44zmyTy4KX2CqUWs-NaCSUMAyGjQq0dM2CUVOgC6MiFETiiHXvPtVh8PnJ7kYV9voY8PvA:1woLFs:bqNNGWwP1qApdflCEGw5mDnf0nI7OQCN1NL8vqDZCCc', '2026-07-27 15:20:28.218393'),
('gl33qetz6taxa4no1642pf0a9we3u1er', '.eJxVjEEOwiAUBe_C2hAoFKRL956BfOAjqAEDbaIx3t2QdKHbN_PmTSxsa7Jbx2ZzIAvh5PC7OfA3LAOEK5RLpb6WtWVHh0J32um5BryfdvcvkKCn8Q7RTGC8n44zmyTy4KX2CqUWs-NaCSUMAyGjQq0dM2CUVOgC6MiFETiiHXvPtVh8PnJ7kYV9voY8PvA:1wp29u:ASmoxVyg0FDZ-qYw3J2-OH4jJubLdYhudoHozoudpWk', '2026-07-29 13:09:10.217866'),
('ghxbmevy18182358qdobd1tc9cgs83e7', '.eJxVjEEOwiAUBe_C2hAoFKRL956BfOAjqAEDbaIx3t2QdKHbN_PmTSxsa7Jbx2ZzIAvh5PC7OfA3LAOEK5RLpb6WtWVHh0J32um5BryfdvcvkKCn8Q7RTGC8n44zmyTy4KX2CqUWs-NaCSUMAyGjQq0dM2CUVOgC6MiFETiiHXvPtVh8PnJ7kYV9voY8PvA:1wp8yk:xAxjLkjNt67c1FU79xhileshidOtsNb0myX4vUcKd0M', '2026-07-29 20:26:06.646177'),
('xr1r4wq22vhx44u771ne53dq4d6uw0rw', '.eJxVjDsOwjAQBe_iGlnxd9eU9Jwh2vU6JIAcKU4qxN0hUgpo38y8l-ppW8d-a2XpJ1Fn5dTpd2PKj1J3IHeqt1nnua7LxHpX9EGbvs5SnpfD_TsYqY3fuoAAZ0tJLEHyoSAE9IK-c0CYjWEbB7ZoOULCLgzFdQOQccEgRBH1_gDcoDda:1wpCXi:7-ZO4eg43E03ukdPeORALmxktSxVjW_XniznJPxS1UM', '2026-07-30 00:14:26.070336'),
('tyaik74wmmr42zpj8rdrg648uqqpk4jc', '.eJxVjMsOwiAQRf-FtSE8Sod26d5vIANMLWqgKW2iMf671nSh23vOPU_mcF1Gt1aaXYqsZ5odfjeP4Up5A_GC-Vx4KHmZk-ebwnda-alEuh139y8wYh0_b4IIPijsokLoGkMWjG2ibYQGtEFKr9rBK6t8C50VZiAtBkCpjbTQxm-0Uq2pZEf3Kc0P1ovXG3n-Ppc:1wpCQv:mVpDQzfLnyxvJQmxnzLsM8z8eiYDmRDIBVMpfp9NJFA', '2026-07-30 00:07:25.786721'),
('siqnb6p69s2s2zoed0sdvwe738jflgg8', '.eJxVjMsOwiAQRf-FtSE8Sod26d5vIANMLWqgKW2iMf671nSh23vOPU_mcF1Gt1aaXYqsZ5odfjeP4Up5A_GC-Vx4KHmZk-ebwnda-alEuh139y8wYh0_b4IIPijsokLoGkMWjG2ibYQGtEFKr9rBK6t8C50VZiAtBkCpjbTQxm-0Uq2pZEf3Kc0P1ovXG3n-Ppc:1wpQF4:8DLqARQy_vWItPU1ShaB38B_JSunJiN0kZPmamoeEBw', '2026-07-30 14:52:06.870662'),
('jnjvynh7998g7xhzxwshpljahxl95q8b', '.eJxVjM0OgjAQhN-lZ9MU-kPh6N1naLa7q1RNaygkGuO7CwkHPc7MN99bBFjmMSyVp5BIDMKLw28XAW-ct4GukC9FYsnzlKLcELmvVZ4K8f24s3-CEeq4vnvrnccGUSPY3lhjFLno_DnaMzagHfGalTHaN0SOYyToiLWntgXo1CatXGsqOfDzkaaXGNTnC6YAP9E:1wpQN3:HMiC_KFdxSjlD8rGk80c5y-J1ffTaPqX-jqIbyjCF9Y', '2026-07-30 15:00:21.696911'),
('mbeefrrqly9utuaxdruqvbaev88osrdy', '.eJxVjM0OgjAQhN-lZ9MU-kPh6N1naLa7q1RNaygkGuO7CwkHPc7MN99bBFjmMSyVp5BIDMKLw28XAW-ct4GukC9FYsnzlKLcELmvVZ4K8f24s3-CEeq4vnvrnccGUSPY3lhjFLno_DnaMzagHfGalTHaN0SOYyToiLWntgXo1CatXGsqOfDzkaaXGNTnC6YAP9E:1wqotf:gNUHQMhKvr1_oenn9P2KtcpGNbYmGNuUX-BESYue3aA', '2026-08-03 11:23:47.855778'),
('6z8ijs9h194gpv2cilqniyixmslk9o3d', '.eJxVjEEOwiAQRe_C2pApHaC6dO8ZCDCDRQ2Y0iYa4921SRe6_e_99xLOL_PolsaTyyQOAsXudws-XrmsgC6-nKuMtcxTDnJV5EabPFXi23Fz_wKjb-P3Dah1IEBvfOiUifuebOdtGnowYAHSkEzCntnYqIh07JRGUgnRGqWVXaONW8u1OH7c8_QUB3h_AGW9Pkk:1wqonG:UCyHb6n9eRnAT_NEum_qyhqMWxjEljRXcwZnVoSOL8E', '2026-08-03 11:17:10.060494'),
('6acg6djv2m19uked4b44707jlxen8784', '.eJxVjEEOwiAQRe_C2pApHaC6dO8ZCDCDRQ2Y0iYa4921SRe6_e_99xLOL_PolsaTyyQOAsXudws-XrmsgC6-nKuMtcxTDnJV5EabPFXi23Fz_wKjb-P3Dah1IEBvfOiUifuebOdtGnowYAHSkEzCntnYqIh07JRGUgnRGqWVXaONW8u1OH7c8_QUB3h_AGW9Pkk:1wqp5G:lyZ-bssP4BgrnSQHeuRp6ELFi_iENZWolSjW8P4wk7E', '2026-08-03 11:35:46.977022'),
('wfwncs9es66c31owz9844pk3n70hywdp', '.eJxVjM0OgjAQhN-lZ9MU-kPh6N1naLa7q1RNaygkGuO7CwkHPc7MN99bBFjmMSyVp5BIDMKLw28XAW-ct4GukC9FYsnzlKLcELmvVZ4K8f24s3-CEeq4vnvrnccGUSPY3lhjFLno_DnaMzagHfGalTHaN0SOYyToiLWntgXo1CatXGsqOfDzkaaXGNTnC6YAP9E:1wqpZK:qbwNTUmD8DIyFQrS8pKubqjrWV9yJkM4ymDT-eICCx4', '2026-08-03 12:06:50.258802'),
('87vzmojv7wqc7s7ng24curs8oqse0ei4', '.eJxVjMsOwiAURP-FtSFQHqUu3fcbyH1QqRpISrsy_rtt0oUuZ86ZeYsI25rj1tISZxZXEcTlt0OgZyoH4AeUe5VUy7rMKA9FnrTJsXJ63U737yBDy_t6cMEH0kSGwA3WWavYow8Tuok0GM9pz8paEzSzT4gMPScTuOsAeiU-X_AaOJQ:1wqqYd:JT8Wo7y2MqJWwOZnyn7F5HMnvAlLiEJUe3-al02u5go', '2026-08-03 13:10:11.562558'),
('jwc0c6wl9v1ia4m5ufctrbzs1myiv7es', '.eJxVjM0OgjAQhN-lZ9MU-kPh6N1naLa7q1RNaygkGuO7CwkHPc7MN99bBFjmMSyVp5BIDMKLw28XAW-ct4GukC9FYsnzlKLcELmvVZ4K8f24s3-CEeq4vnvrnccGUSPY3lhjFLno_DnaMzagHfGalTHaN0SOYyToiLWntgXo1CatXGsqOfDzkaaXGNTnC6YAP9E:1wqqyW:OLTDINbJ4GxehXBIWYEFmqQvQK3R5G2nX4GVTjDE-Xo', '2026-08-03 13:36:56.649925'),
('h84c50qv3dv11yj7t9g2ovlsfyi2bgq9', '.eJxVjM0OgjAQhN-lZ9MU-kPh6N1naLa7q1RNaygkGuO7CwkHPc7MN99bBFjmMSyVp5BIDMKLw28XAW-ct4GukC9FYsnzlKLcELmvVZ4K8f24s3-CEeq4vnvrnccGUSPY3lhjFLno_DnaMzagHfGalTHaN0SOYyToiLWntgXo1CatXGsqOfDzkaaXGNTnC6YAP9E:1wqs1S:O-JrZiVw9uuJoE9A4OZHFd_UlZOHpTCIhNeh1B3x36M', '2026-08-03 14:44:02.194122'),
('tpph5zd5cca13k1989gi74veld0bs818', '.eJxVjMsOgjAURP-la9OUvigs3fsNzW3vRaqmJRQSjfHfhYSFLmfmzHkzD-sy-rXS7BOynjl2-u0CxDvlfcAb5GvhseRlToHvCD_Wyi8F6XE-2D_BCHXc3p1x1sUmRhXBdNpoLdAG64ZghtiAskhbFlor1yBaCgGhRVIOpQRoxS6tVGsq2dNzSvOL9dJ0Ugjx-QInmUED:1wquBq:337Gy2abfuX4ut5WnqtojD0Td2M8oV8c1VttyPPN9T8', '2026-09-02 15:02:54.131139'),
('j1j5etdywndnuccpc4ni6v2snz4vxx0l', '.eJxVjM0OgjAQhN-lZ9MU-kPh6N1naLa7q1RNaygkGuO7CwkHPc7MN99bBFjmMSyVp5BIDMKLw28XAW-ct4GukC9FYsnzlKLcELmvVZ4K8f24s3-CEeq4vnvrnccGUSPY3lhjFLno_DnaMzagHfGalTHaN0SOYyToiLWntgXo1CatXGsqOfDzkaaXGNTnC6YAP9E:1wquyR:esYuv02lKRTkwI7T3JxDxqFmY52e_D3KSjqEKc4S93Q', '2026-08-03 17:53:07.445290'),
('iyfi0ahyyhaz7jed0d3xozzjahy3hhq0', '.eJxVjM0OgjAQhN-lZ9MU-kPh6N1naLa7q1RNaygkGuO7CwkHPc7MN99bBFjmMSyVp5BIDMKLw28XAW-ct4GukC9FYsnzlKLcELmvVZ4K8f24s3-CEeq4vnvrnccGUSPY3lhjFLno_DnaMzagHfGalTHaN0SOYyToiLWntgXo1CatXGsqOfDzkaaXGNTnC6YAP9E:1wqw4h:rI3oobJkGgTax0Zp61x3Rxg3lzwI_MRdy6pjYg8woaY', '2026-08-03 19:03:39.725923'),
('h7k45xwc5eo6xmeuvt91u5sveeyrvauq', '.eJxVjM0OgjAQhN-lZ9MU-kPh6N1naLa7q1RNaygkGuO7CwkHPc7MN99bBFjmMSyVp5BIDMKLw28XAW-ct4GukC9FYsnzlKLcELmvVZ4K8f24s3-CEeq4vnvrnccGUSPY3lhjFLno_DnaMzagHfGalTHaN0SOYyToiLWntgXo1CatXGsqOfDzkaaXGNTnC6YAP9E:1wqvAw:jHnKMeffzCcpoP9Z1zXxjXpT6-X9Vp1jc6bLA3PJRNQ', '2026-08-03 18:06:02.780141'),
('dnfoj096mts3v3peinjy10rewt6o4bt8', '.eJxVjMsOwiAQRf-FtSE8Sod26d5vIANMLWqgKW2iMf671nSh23vOPU_mcF1Gt1aaXYqsZ5odfjeP4Up5A_GC-Vx4KHmZk-ebwnda-alEuh139y8wYh0_b4IIPijsokLoGkMWjG2ibYQGtEFKr9rBK6t8C50VZiAtBkCpjbTQxm-0Uq2pZEf3Kc0P1ovXG3n-Ppc:1wqvWK:e6j4Q8V_tP3AUccS5i2DaXnXtzc51aLX5L6I4f1dNo8', '2026-08-03 18:28:08.547669'),
('8tryzqyub7t588jjavdznltli9gtwh3j', '.eJxVjM0OgjAQhN-lZ9MU-kPh6N1naLa7q1RNaygkGuO7CwkHPc7MN99bBFjmMSyVp5BIDMKLw28XAW-ct4GukC9FYsnzlKLcELmvVZ4K8f24s3-CEeq4vnvrnccGUSPY3lhjFLno_DnaMzagHfGalTHaN0SOYyToiLWntgXo1CatXGsqOfDzkaaXGNTnC6YAP9E:1wqwUK:bq5K4-ZUsxtWB8a5BEjLC6_kJDIdLD2-7lPiBIu8P-M', '2026-08-03 19:30:08.238367'),
('mj61sag2romwfh6p6itwo6u1cnhbtb1e', '.eJxVjM0OgjAQhN-lZ9MU-kPh6N1naLa7q1RNaygkGuO7CwkHPc7MN99bBFjmMSyVp5BIDMKLw28XAW-ct4GukC9FYsnzlKLcELmvVZ4K8f24s3-CEeq4vnvrnccGUSPY3lhjFLno_DnaMzagHfGalTHaN0SOYyToiLWntgXo1CatXGsqOfDzkaaXGNTnC6YAP9E:1wqxNU:RxAWjmtkipIhsRY6V6SHgO84wKAOcIXPoS7s1sny5Nw', '2026-08-03 20:27:08.730402'),
('q4r8mllzjpj31e024m55oftfa8zkrhfq', '.eJxVjM0OgjAQhN-lZ9MU-kPh6N1naLa7q1RNaygkGuO7CwkHPc7MN99bBFjmMSyVp5BIDMKLw28XAW-ct4GukC9FYsnzlKLcELmvVZ4K8f24s3-CEeq4vnvrnccGUSPY3lhjFLno_DnaMzagHfGalTHaN0SOYyToiLWntgXo1CatXGsqOfDzkaaXGNTnC6YAP9E:1wrHPz:OVFMmoRLQKTHBoUKj1QWQJax6fJPnQGbW3pVbI0xxfU', '2026-08-04 17:51:03.900776'),
('9zph0pea11b0secpfg17dfityemz60rv', '.eJxVjM0OgjAQhN-lZ9MU-kPh6N1naLa7q1RNaygkGuO7CwkHPc7MN99bBFjmMSyVp5BIDMKLw28XAW-ct4GukC9FYsnzlKLcELmvVZ4K8f24s3-CEeq4vnvrnccGUSPY3lhjFLno_DnaMzagHfGalTHaN0SOYyToiLWntgXo1CatXGsqOfDzkaaXGNTnC6YAP9E:1wtPrQ:3-D9cwmu1jAfDNum3vDmCp6Qij-CKmOcZKlJ7YR_RGI', '2026-08-10 15:16:12.467642'),
('hcbg50roo6nqxk2ixuvc3t82v4afk9zf', '.eJxVjM0OgjAQhN-lZ9MU-kPh6N1naLa7q1RNaygkGuO7CwkHPc7MN99bBFjmMSyVp5BIDMKLw28XAW-ct4GukC9FYsnzlKLcELmvVZ4K8f24s3-CEeq4vnvrnccGUSPY3lhjFLno_DnaMzagHfGalTHaN0SOYyToiLWntgXo1CatXGsqOfDzkaaXGNTnC6YAP9E:1wtSDK:Q1EKUOsCWw_Sw6a2Wru2knM7j12_EflWwX9x4hrj398', '2026-08-10 17:46:58.061322'),
('9849fl6uwojkqdoiyjqbuar37lbgdwmm', '.eJxVjM0OgjAQhN-lZ9MU-kPh6N1naLa7q1RNaygkGuO7CwkHPc7MN99bBFjmMSyVp5BIDMKLw28XAW-ct4GukC9FYsnzlKLcELmvVZ4K8f24s3-CEeq4vnvrnccGUSPY3lhjFLno_DnaMzagHfGalTHaN0SOYyToiLWntgXo1CatXGsqOfDzkaaXGNTnC6YAP9E:1wvxPB:y6c52MBeFWSVTSdnEp6e1SrvTkdx15R1_00FEgnUzxk', '2026-08-17 15:29:33.761431'),
('8imql9k8lnu61n22xvahqls5wudczdjx', '.eJxVjEEOwiAQRe_C2hDrUEq6dO8ZyMwwtagBA21SY7y71nSh2__ef0_lcZ5GP1cpPgbVq4Pa_W6EfJW0gnDBdM6ac5pKJL0qeqNVn3KQ23Fz_wIj1vHzbgNYywyNaSwaFiYm5yw2XTvw4ASIHBC3hKsQnEgQMAOw6TrD8I1WqTXm5GW5x_JQ_f71BskIQFw:1ww2y7:JYQ1u2s6KEjnv1BpUwDW3HQ0Ztpo0OhQNazbWmYI3qo', '2026-08-17 21:25:59.581999');


-- ── Table: `inventory_category` ──
DROP TABLE IF EXISTS `inventory_category`;
CREATE TABLE `inventory_category` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `category_name` varchar(100) NOT NULL, `category_type` varchar(50) NOT NULL, `description` text NULL, `status` varchar(20) NOT NULL, `created_at` datetime NOT NULL, `updated_at` datetime NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `inventory_category` (`id`, `category_name`, `category_type`, `description`, `status`, `created_at`, `updated_at`) VALUES
(16, 'Mobile Phones', 'Inventory', 'iPhone stock units issued to staff', 'Active', '2026-08-17 18:21:22.551271', '2026-08-17 18:21:22.551311'),
(17, 'Mobile Devices', 'Asset', 'Company-owned iPhones tracked individually', 'Active', '2026-08-17 18:21:22.570972', '2026-08-17 18:21:22.571029');


-- ── Table: `inventory_inventoryitem` ──
DROP TABLE IF EXISTS `inventory_inventoryitem`;
CREATE TABLE `inventory_inventoryitem` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `item_code` varchar(50) NOT NULL UNIQUE, `barcode` varchar(100) NULL UNIQUE, `item_name` varchar(150) NOT NULL, `unit` varchar(50) NOT NULL, `purchase_price` decimal NOT NULL, `current_qty` integer NOT NULL, `min_qty` integer NOT NULL, `description` text NULL, `status` varchar(20) NOT NULL, `created_at` datetime NOT NULL, `updated_at` datetime NOT NULL, `category_id` bigint NOT NULL, `supplier_id` bigint NULL, `item_name_km` varchar(200) NULL, `image` varchar(100) NULL, `image_url` varchar(500) NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `inventory_inventoryitem` (`id`, `item_code`, `barcode`, `item_name`, `unit`, `purchase_price`, `current_qty`, `min_qty`, `description`, `status`, `created_at`, `updated_at`, `category_id`, `supplier_id`, `item_name_km`, `image`, `image_url`) VALUES
(58, 'INV-PH-001', 'PH-IP12-128', 'Apple iPhone 12 (128GB)', 'pcs', 549, 10, 3, 'iPhone 12 | 6.1" OLED | A14 Bionic | 12MP dual cam | 5G | 128GB', 'Active', '2026-08-17 18:21:22.882824', '2026-08-17 18:21:22.882853', 16, 16, NULL, 'inventory/items/iphone12.svg', ''),
(59, 'INV-PH-002', 'PH-IP12-256', 'Apple iPhone 12 (256GB)', 'pcs', 599, 6, 2, 'iPhone 12 | 6.1" OLED | A14 Bionic | 12MP dual cam | 5G | 256GB', 'Active', '2026-08-17 18:21:22.899113', '2026-08-17 18:21:22.899135', 16, 16, NULL, 'inventory/items/iphone12.svg', ''),
(60, 'INV-PH-003', 'PH-IP13-128', 'Apple iPhone 13 (128GB)', 'pcs', 599, 10, 3, 'iPhone 13 | 6.1" OLED | A15 Bionic | 12MP dual cam | Cinematic | 5G | 128GB', 'Active', '2026-08-17 18:21:22.910173', '2026-08-17 18:21:22.910192', 16, 16, NULL, 'inventory/items/iphone13.svg', ''),
(61, 'INV-PH-004', 'PH-IP13-256', 'Apple iPhone 13 (256GB)', 'pcs', 649, 6, 2, 'iPhone 13 | 6.1" OLED | A15 Bionic | 12MP dual cam | 5G | 256GB', 'Active', '2026-08-17 18:21:22.920594', '2026-08-17 18:21:22.920613', 16, 16, NULL, 'inventory/items/iphone13.svg', ''),
(62, 'INV-PH-005', 'PH-IP14-128', 'Apple iPhone 14 (128GB)', 'pcs', 699, 8, 3, 'iPhone 14 | 6.1" OLED | A15 Bionic | 12MP dual cam | Crash Detection | 5G | 128GB', 'Active', '2026-08-17 18:21:22.930379', '2026-08-17 18:21:22.930397', 16, 16, NULL, 'inventory/items/iphone14.svg', ''),
(63, 'INV-PH-006', 'PH-IP14-256', 'Apple iPhone 14 (256GB)', 'pcs', 749, 6, 2, 'iPhone 14 | 6.1" OLED | A15 Bionic | 12MP dual cam | 5G | 256GB', 'Active', '2026-08-17 18:21:22.940466', '2026-08-17 18:21:22.940483', 16, 16, NULL, 'inventory/items/iphone14.svg', ''),
(64, 'INV-PH-007', 'PH-IP14P-256', 'Apple iPhone 14 Pro (256GB)', 'pcs', 999, 4, 2, 'iPhone 14 Pro | 6.1" Super Retina XDR | A16 Bionic | 48MP triple cam | Dynamic Island | 5G | 256GB', 'Active', '2026-08-17 18:21:22.949359', '2026-08-17 18:21:22.949376', 16, 17, NULL, 'inventory/items/iphone14pro.svg', ''),
(65, 'INV-PH-008', 'PH-IP15-128', 'Apple iPhone 15 (128GB)', 'pcs', 799, 8, 3, 'iPhone 15 | 6.1" OLED | A16 Bionic | 48MP cam | Dynamic Island | USB-C | 5G | 128GB', 'Active', '2026-08-17 18:21:22.958366', '2026-08-17 18:21:22.958382', 16, 16, NULL, 'inventory/items/iphone15.svg', ''),
(66, 'INV-PH-009', 'PH-IP15-256', 'Apple iPhone 15 (256GB)', 'pcs', 859, 6, 2, 'iPhone 15 | 6.1" OLED | A16 Bionic | 48MP cam | USB-C | 5G | 256GB', 'Active', '2026-08-17 18:21:22.967286', '2026-08-17 18:21:22.967302', 16, 16, NULL, 'inventory/items/iphone15.svg', ''),
(67, 'INV-PH-010', 'PH-IP15P-256', 'Apple iPhone 15 Pro (256GB)', 'pcs', 999, 5, 2, 'iPhone 15 Pro | 6.1" Super Retina XDR | A17 Pro | 48MP triple cam | Titanium | USB-C | 5G', 'Active', '2026-08-17 18:21:22.976168', '2026-08-17 18:21:22.976185', 16, 17, NULL, 'inventory/items/iphone15pro.svg', ''),
(68, 'INV-PH-011', 'PH-IP15PM-512', 'Apple iPhone 15 Pro Max (512GB)', 'pcs', 1199, 3, 1, 'iPhone 15 Pro Max | 6.7" | A17 Pro | Periscope 5x zoom | Titanium | USB-C | 5G | 512GB', 'Active', '2026-08-17 18:21:22.985345', '2026-08-17 18:21:22.985361', 16, 17, NULL, 'inventory/items/iphone15pro.svg', ''),
(69, 'INV-PH-012', 'PH-IP16-128', 'Apple iPhone 16 (128GB)', 'pcs', 899, 6, 2, 'iPhone 16 | 6.1" OLED | A18 | 48MP cam | Camera Control | Apple Intelligence | USB-C | 5G', 'Active', '2026-08-17 18:21:22.994087', '2026-08-17 18:21:22.994102', 16, 16, NULL, 'inventory/items/iphone16.svg', ''),
(70, 'INV-PH-013', 'PH-IP16-256', 'Apple iPhone 16 (256GB)', 'pcs', 959, 5, 2, 'iPhone 16 | 6.1" OLED | A18 | 48MP cam | Apple Intelligence | USB-C | 5G | 256GB', 'Active', '2026-08-17 18:21:23.002179', '2026-08-17 18:21:23.002194', 16, 16, NULL, 'inventory/items/iphone16.svg', ''),
(71, 'INV-PH-014', 'PH-IP16P-256', 'Apple iPhone 16 Pro (256GB)', 'pcs', 1099, 4, 2, 'iPhone 16 Pro | 6.3" Super Retina XDR | A18 Pro | 48MP triple cam | Apple Intelligence | USB-C | 5G', 'Active', '2026-08-17 18:21:23.010073', '2026-08-17 18:21:23.010088', 16, 17, NULL, 'inventory/items/iphone16pro.svg', ''),
(72, 'INV-PH-015', 'PH-IP16PM-512', 'Apple iPhone 16 Pro Max (512GB)', 'pcs', 1299, 3, 1, 'iPhone 16 Pro Max | 6.9" | A18 Pro | Periscope 5x zoom | Apple Intelligence | USB-C | 5G | 512GB', 'Active', '2026-08-17 18:21:23.018135', '2026-08-17 18:21:23.018148', 16, 17, NULL, 'inventory/items/iphone16pro.svg', ''),
(73, 'INV-PH-016', 'PH-IP17-256', 'Apple iPhone 17 (256GB)', 'pcs', 1099, 5, 2, 'iPhone 17 | 6.3" OLED | A19 | 48MP triple cam | Apple Intelligence | USB-C | 5G | 256GB', 'Active', '2026-08-17 18:21:23.025871', '2026-08-17 18:21:23.025885', 16, 16, NULL, 'inventory/items/iphone17.svg', ''),
(74, 'INV-PH-017', 'PH-IP17-512', 'Apple iPhone 17 (512GB)', 'pcs', 1199, 4, 2, 'iPhone 17 | 6.3" OLED | A19 | 48MP triple cam | Apple Intelligence | USB-C | 5G | 512GB', 'Active', '2026-08-17 18:21:23.034098', '2026-08-17 18:21:23.034112', 16, 16, NULL, 'inventory/items/iphone17.svg', ''),
(75, 'INV-PH-018', 'PH-IP17P-256', 'Apple iPhone 17 Pro (256GB)', 'pcs', 1299, 3, 2, 'iPhone 17 Pro | 6.3" Super Retina XDR | A19 Pro | Periscope triple cam | Apple Intelligence | USB-C | 5G', 'Active', '2026-08-17 18:21:23.042195', '2026-08-17 18:21:23.042209', 16, 17, NULL, 'inventory/items/iphone17pro.svg', ''),
(76, 'INV-PH-019', 'PH-IP17P-512', 'Apple iPhone 17 Pro (512GB)', 'pcs', 1399, 3, 1, 'iPhone 17 Pro | 6.3" Super Retina XDR | A19 Pro | 512GB | Apple Intelligence | USB-C | 5G', 'Active', '2026-08-17 18:21:23.049867', '2026-08-17 18:21:23.049879', 16, 17, NULL, 'inventory/items/iphone17pro.svg', ''),
(77, 'INV-PH-020', 'PH-IP17PM-512', 'Apple iPhone 17 Pro Max (512GB)', 'pcs', 1499, 3, 1, 'iPhone 17 Pro Max | 6.9" Super Retina XDR | A19 Pro | Periscope zoom | Apple Intelligence | 512GB', 'Active', '2026-08-17 18:21:23.058285', '2026-08-17 18:21:23.058302', 16, 17, NULL, 'inventory/items/iphone17pro.svg', '');


-- ── Table: `inventory_location` ──
DROP TABLE IF EXISTS `inventory_location`;
CREATE TABLE `inventory_location` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `location_name` varchar(150) NOT NULL UNIQUE, `location_type` varchar(50) NOT NULL, `address` text NULL, `description` text NULL, `status` varchar(20) NOT NULL, `created_at` datetime NOT NULL, `updated_at` datetime NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `inventory_location` (`id`, `location_name`, `location_type`, `address`, `description`, `status`, `created_at`, `updated_at`) VALUES
(17, 'Main Warehouse', 'Warehouse', 'Building A, Ground Floor, Phnom Penh', NULL, 'Active', '2026-08-17 18:21:22.589622', '2026-08-17 18:21:22.589674'),
(18, 'Head Office', 'Office', 'Floor 5, Tower Block, Phnom Penh', NULL, 'Active', '2026-08-17 18:21:22.606435', '2026-08-17 18:21:22.606496'),
(19, 'IT Storage Room', 'Office', 'Building B, Room 102, Phnom Penh', NULL, 'Active', '2026-08-17 18:21:22.629461', '2026-08-17 18:21:22.629544'),
(20, 'Finance Department', 'Department', 'Floor 3, Tower Block, Phnom Penh', NULL, 'Active', '2026-08-17 18:21:22.668700', '2026-08-17 18:21:22.668903'),
(21, 'HR Department', 'Department', 'Floor 4, Tower Block, Phnom Penh', NULL, 'Active', '2026-08-17 18:21:22.717173', '2026-08-17 18:21:22.717379'),
(22, 'Branch - Siem Reap', 'Branch', 'National Road 6, Siem Reap Province', NULL, 'Active', '2026-08-17 18:21:22.776916', '2026-08-17 18:21:22.777139'),
(23, 'Branch - Sihanoukville', 'Branch', 'Ekareach Street, Sihanoukville', NULL, 'Active', '2026-08-17 18:21:22.806611', '2026-08-17 18:21:22.806683');


-- ── Table: `inventory_supplier` ──
DROP TABLE IF EXISTS `inventory_supplier`;
CREATE TABLE `inventory_supplier` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `supplier_name` varchar(150) NOT NULL, `contact_person` varchar(100) NULL, `phone` varchar(20) NULL, `email` varchar(254) NULL, `address` text NULL, `status` varchar(20) NOT NULL, `created_at` datetime NOT NULL, `updated_at` datetime NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `inventory_supplier` (`id`, `supplier_name`, `contact_person`, `phone`, `email`, `address`, `status`, `created_at`, `updated_at`) VALUES
(16, 'Apple Cambodia', 'Kevin Chan', '+855 23 888 777', 'sales@apple-kh.com', 'Preah Monivong Blvd, Phnom Penh', 'Active', '2026-08-17 18:21:22.826591', '2026-08-17 18:21:22.826750'),
(17, 'iStore Phnom Penh', 'Sina Rith', '+855 12 999 888', 'info@istore.kh', 'Street 51, BKK1, Phnom Penh', 'Active', '2026-08-17 18:21:22.848499', '2026-08-17 18:21:22.848550'),
(18, 'TechWorld Cambodia', 'Sok Visal', '+855 23 456 789', 'info@techworld.kh', 'Mao Tse Toung Blvd, Phnom Penh', 'Active', '2026-08-17 18:21:22.865257', '2026-08-17 18:21:22.865294');


-- ── Table: `notifications_notification` ──
DROP TABLE IF EXISTS `notifications_notification`;
CREATE TABLE `notifications_notification` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `title` varchar(200) NOT NULL, `message` text NOT NULL, `notif_type` varchar(20) NOT NULL, `is_read` TINYINT(1) NOT NULL, `link` varchar(200) NULL, `created_at` datetime NOT NULL, `user_id` bigint NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `notifications_notification` (`id`, `title`, `message`, `notif_type`, `is_read`, `link`, `created_at`, `user_id`) VALUES
(30, 'New Stock Received', '15 units iPhone 12 (128GB) received from Apple Cambodia.', 'info', 0, '/inventory/items/', '2026-08-17 18:21:23.622695', 1),
(31, 'Low Stock — iPhone 17 Pro Max', 'iPhone 17 Pro Max (512GB) is below minimum qty (3 remaining, min 1).', 'warning', 0, '/stock/alerts/', '2026-08-17 18:21:23.638048', 1),
(32, 'Asset Assigned', 'iPhone 16 Pro (IP16P-SN-0001) assigned to Manager.', 'info', 0, '/assets/', '2026-08-17 18:21:23.654855', 1),
(33, 'Damaged Unit Reported', 'iPhone 14 (256GB) — IP14-SN-0004 moved to Under Maintenance.', 'warning', 0, '/assets/maintenance/', '2026-08-17 18:21:23.674048', 1),
(34, 'Stock OUT Recorded', '5x iPhone 12 (128GB) issued to staff via REQ-PH-001.', 'info', 0, '/stock/', '2026-08-17 18:21:23.703634', 9),
(35, 'New iPhone 17 Arrived', '6 units iPhone 17 (256GB) ready for issue in warehouse.', 'success', 0, '/inventory/items/', '2026-08-17 18:21:23.771094', 9),
(36, 'Low Stock — iPhone 16 Pro Max', 'iPhone 16 Pro Max (512GB) low — 3 units remaining (min 1).', 'warning', 0, '/stock/alerts/', '2026-08-17 18:21:23.855358', 9);


-- ── Table: `stock_lowstockalert` ──
DROP TABLE IF EXISTS `stock_lowstockalert`;
CREATE TABLE `stock_lowstockalert` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `current_qty` integer NOT NULL, `min_qty` integer NOT NULL, `alert_date` datetime NOT NULL, `status` varchar(20) NOT NULL, `resolved_at` datetime NULL, `item_id` bigint NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Table: `stock_stockmovement` ──
DROP TABLE IF EXISTS `stock_stockmovement`;
CREATE TABLE `stock_stockmovement` (`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, `movement_type` varchar(20) NOT NULL, `quantity` integer NOT NULL, `movement_date` datetime NOT NULL, `reference_no` varchar(100) NULL, `reason` varchar(150) NULL, `remarks` text NULL, `qty_after` integer NULL, `created_at` datetime NOT NULL, `created_by_id` bigint NOT NULL, `item_id` bigint NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `stock_stockmovement` (`id`, `movement_type`, `quantity`, `movement_date`, `reference_no`, `reason`, `remarks`, `qty_after`, `created_at`, `created_by_id`, `item_id`) VALUES
(76, 'Stock IN', 15, '2026-06-18 18:21:23.337122', 'PO-PH-2025-001', 'Purchase', NULL, 25, '2026-08-17 18:21:23.337670', 1, 58),
(77, 'Stock IN', 10, '2026-06-18 18:21:23.345848', 'PO-PH-2025-002', 'Purchase', NULL, 16, '2026-08-17 18:21:23.346310', 9, 59),
(78, 'Stock IN', 15, '2026-06-23 18:21:23.353840', 'PO-PH-2025-003', 'Purchase', NULL, 25, '2026-08-17 18:21:23.354356', 5, 60),
(79, 'Stock IN', 10, '2026-06-23 18:21:23.361756', 'PO-PH-2025-004', 'Purchase', NULL, 16, '2026-08-17 18:21:23.362215', 1, 61),
(80, 'Stock IN', 12, '2026-06-28 18:21:23.370039', 'PO-PH-2025-005', 'Purchase', NULL, 20, '2026-08-17 18:21:23.370515', 9, 62),
(81, 'Stock IN', 8, '2026-06-28 18:21:23.377709', 'PO-PH-2025-006', 'Purchase', NULL, 14, '2026-08-17 18:21:23.378179', 5, 63),
(82, 'Stock IN', 6, '2026-07-03 18:21:23.385866', 'PO-PH-2025-007', 'Purchase', NULL, 10, '2026-08-17 18:21:23.386451', 1, 64),
(83, 'Stock IN', 12, '2026-07-08 18:21:23.393731', 'PO-PH-2025-008', 'Purchase', NULL, 20, '2026-08-17 18:21:23.394200', 9, 65),
(84, 'Stock IN', 8, '2026-07-08 18:21:23.403082', 'PO-PH-2025-009', 'Purchase', NULL, 14, '2026-08-17 18:21:23.403601', 5, 66),
(85, 'Stock IN', 6, '2026-07-13 18:21:23.411901', 'PO-PH-2025-010', 'Purchase', NULL, 11, '2026-08-17 18:21:23.412623', 1, 67),
(86, 'Stock IN', 4, '2026-07-13 18:21:23.421034', 'PO-PH-2025-011', 'Purchase', NULL, 7, '2026-08-17 18:21:23.421588', 9, 68),
(87, 'Stock IN', 8, '2026-07-18 18:21:23.429951', 'PO-PH-2025-012', 'Purchase', NULL, 14, '2026-08-17 18:21:23.430488', 5, 69),
(88, 'Stock IN', 6, '2026-07-18 18:21:23.438972', 'PO-PH-2025-013', 'Purchase', NULL, 11, '2026-08-17 18:21:23.439567', 1, 70),
(89, 'Stock IN', 5, '2026-07-23 18:21:23.448016', 'PO-PH-2025-014', 'Purchase', NULL, 9, '2026-08-17 18:21:23.448594', 9, 71),
(90, 'Stock IN', 4, '2026-07-23 18:21:23.457083', 'PO-PH-2025-015', 'Purchase', NULL, 7, '2026-08-17 18:21:23.457789', 5, 72),
(91, 'Stock IN', 6, '2026-07-28 18:21:23.466037', 'PO-PH-2025-016', 'Purchase', NULL, 11, '2026-08-17 18:21:23.466638', 1, 73),
(92, 'Stock IN', 5, '2026-07-28 18:21:23.475000', 'PO-PH-2025-017', 'Purchase', NULL, 9, '2026-08-17 18:21:23.475929', 9, 74),
(93, 'Stock IN', 4, '2026-08-02 18:21:23.485244', 'PO-PH-2025-018', 'Purchase', NULL, 7, '2026-08-17 18:21:23.485907', 5, 75),
(94, 'Stock IN', 4, '2026-08-02 18:21:23.496239', 'PO-PH-2025-019', 'Purchase', NULL, 7, '2026-08-17 18:21:23.496950', 1, 76),
(95, 'Stock IN', 4, '2026-08-07 18:21:23.507009', 'PO-PH-2025-020', 'Purchase', NULL, 7, '2026-08-17 18:21:23.507726', 9, 77),
(96, 'Stock OUT', 5, '2026-07-03 18:21:23.517640', 'REQ-PH-001', 'Usage', NULL, 5, '2026-08-17 18:21:23.518613', 5, 58),
(97, 'Stock OUT', 5, '2026-07-08 18:21:23.528251', 'REQ-PH-002', 'Usage', NULL, 5, '2026-08-17 18:21:23.528996', 1, 60),
(98, 'Stock OUT', 4, '2026-07-13 18:21:23.539728', 'REQ-PH-003', 'Usage', NULL, 4, '2026-08-17 18:21:23.540555', 9, 62),
(99, 'Stock OUT', 4, '2026-07-18 18:21:23.551709', 'REQ-PH-004', 'Usage', NULL, 4, '2026-08-17 18:21:23.552673', 5, 65),
(100, 'Stock OUT', 2, '2026-07-28 18:21:23.563713', 'REQ-PH-005', 'Usage', NULL, 4, '2026-08-17 18:21:23.564664', 1, 69),
(101, 'Stock OUT', 1, '2026-08-03 18:21:23.575765', 'REQ-PH-006', 'Usage', NULL, 4, '2026-08-17 18:21:23.576812', 9, 73),
(102, 'Stock OUT', 2, '2026-08-07 18:21:23.589172', 'DMG-PH-001', 'Damage', NULL, 4, '2026-08-17 18:21:23.590455', 5, 63),
(103, 'Stock OUT', 1, '2026-08-10 18:21:23.602744', 'DMG-PH-002', 'Damage', NULL, 4, '2026-08-17 18:21:23.604190', 1, 67);


SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- Import complete. All EIAMS tables and data loaded.
-- ============================================================
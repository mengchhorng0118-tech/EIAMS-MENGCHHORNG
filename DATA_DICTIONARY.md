# Data Dictionary — EIAMS
## Enterprise Inventory & Asset Management System
**Course:** System Analysis & Design (SAD) — BIU Y3S1IT  
**Version:** 1.0.0

---

## Summary of Tables

| Table                | Purpose                              |
| -------------------- | ------------------------------------ |
| roles                | កំណត់តួនាទី Admin / Staff / Manager  |
| users                | គណនី Login របស់អ្នកប្រើប្រាស់        |
| categories           | ប្រភេទ Inventory និង Asset           |
| locations            | ទីតាំង Asset / Stock                 |
| suppliers            | អ្នកផ្គត់ផ្គង់                       |
| inventory_items      | ទំនិញស្តុក                           |
| assets               | ទ្រព្យសម្បត្តិ                       |
| stock_movements      | ចលនាស្តុក                            |
| asset_transfers      | ការផ្ទេរ Asset                       |
| maintenance_records  | កំណត់ត្រាជួសជុល                      |
| asset_disposals      | ការបោះចោល Asset                      |
| asset_audit_logs     | ការត្រួតពិនិត្យ Asset                |
| low_stock_alerts     | ជូនដំណឹងស្តុកទាប                     |
| notifications        | ការជូនដំណឹង                          |
| reports              | របាយការណ៍                            |

---

## 1. Table: roles
| Field Name  | Data Type | Size | Key | Description             |
| ----------- | --------- | ---: | --- | ----------------------- |
| role_id     | INT       |   11 | PK  | លេខសម្គាល់តួនាទី        |
| role_name   | VARCHAR   |   50 |     | Super Admin / Admin / Manager / Staff |
| description | TEXT      |      |     | ព័ត៌មានលម្អិតតួនាទី     |
| created_at  | DATETIME  |      |     | ថ្ងៃបង្កើត               |
| updated_at  | DATETIME  |      |     | ថ្ងៃកែប្រែចុងក្រោយ       |

---

## 2. Table: users

| Field Name  | Data Type | Size | Key    | Description              |
| ----------- | --------- | ---: | ------ | ------------------------ |
| user_id     | INT       |   11 | PK     | លេខសម្គាល់អ្នកប្រើប្រាស់ |
| role_id     | INT       |   11 | FK     | ភ្ជាប់ទៅ Table roles     |
| full_name   | VARCHAR   |  100 |        | ឈ្មោះពេញ                 |
| gender      | VARCHAR   |   10 |        | Male / Female / Other    |
| phone       | VARCHAR   |   20 |        | លេខទូរស័ព្ទ              |
| email       | VARCHAR   |  254 | UNIQUE | អ៊ីមែល                   |
| username    | VARCHAR   |  150 | UNIQUE | ឈ្មោះ Login              |
| password    | VARCHAR   |  128 |        | លេខសម្ងាត់ (hashed)      |
| department  | VARCHAR   |  100 |        | ផ្នែកការងារ              |
| status      | VARCHAR   |   20 |        | Active / Inactive        |
| profile_pic | VARCHAR   |  100 |        | រូបភាពប្រូហ្វាល          |
| created_at  | DATETIME  |      |        | ថ្ងៃបង្កើត               |

---

## 3. Table: categories

| Field Name    | Data Type | Size | Key | Description                 |
| ------------- | --------- | ---: | --- | --------------------------- |
| category_id   | INT       |   11 | PK  | លេខសម្គាល់ប្រភេទទំនិញ/Asset |
| category_name | VARCHAR   |  100 |     | ឈ្មោះប្រភេទ                 |
| category_type | VARCHAR   |   50 |     | Inventory / Asset           |
| description   | TEXT      |      |     | ព័ត៌មានបន្ថែម               |
| status        | VARCHAR   |   20 |     | Active / Inactive           |
| created_at    | DATETIME  |      |     | ថ្ងៃបង្កើត                  |
| updated_at    | DATETIME  |      |     | ថ្ងៃកែប្រែចុងក្រោយ          |

---

## 4. Table: locations

| Field Name    | Data Type | Size | Key | Description                     |
| ------------- | --------- | ---: | --- | ------------------------------- |
| location_id   | INT       |   11 | PK  | លេខសម្គាល់ទីតាំង                |
| location_name | VARCHAR   |  150 |     | ឈ្មោះទីតាំង                     |
| location_type | VARCHAR   |   50 |     | Warehouse / Office / Department |
| address       | TEXT      |      |     | អាសយដ្ឋាន                       |
| description   | TEXT      |      |     | ព័ត៌មានបន្ថែម                   |
| status        | VARCHAR   |   20 |     | Active / Inactive               |
| created_at    | DATETIME  |      |     | ថ្ងៃបង្កើត                      |
| updated_at    | DATETIME  |      |     | ថ្ងៃកែប្រែចុងក្រោយ              |

---

## 5. Table: suppliers

| Field Name     | Data Type | Size | Key | Description         |
| -------------- | --------- | ---: | --- | ------------------- |
| supplier_id    | INT       |   11 | PK  | លេខសម្គាល់ Supplier |
| supplier_name  | VARCHAR   |  150 |     | ឈ្មោះអ្នកផ្គត់ផ្គង់ |
| contact_person | VARCHAR   |  100 |     | អ្នកទំនាក់ទំនង      |
| phone          | VARCHAR   |   20 |     | លេខទូរស័ព្ទ         |
| email          | VARCHAR   |  254 |     | អ៊ីមែល              |
| address        | TEXT      |      |     | អាសយដ្ឋាន           |
| status         | VARCHAR   |   20 |     | Active / Inactive   |
| created_at     | DATETIME  |      |     | ថ្ងៃបង្កើត          |
| updated_at     | DATETIME  |      |     | ថ្ងៃកែប្រែចុងក្រោយ  |

---

## 6. Table: inventory_items

| Field Name     | Data Type | Size | Key    | Description               |
| -------------- | --------- | ---: | ------ | ------------------------- |
| item_id        | INT       |   11 | PK     | លេខសម្គាល់ទំនិញ           |
| category_id    | INT       |   11 | FK     | ភ្ជាប់ទៅ Table categories |
| supplier_id    | INT       |   11 | FK     | ភ្ជាប់ទៅ Table suppliers  |
| item_code      | VARCHAR   |   50 | UNIQUE | លេខកូដទំនិញ               |
| barcode        | VARCHAR   |  100 | UNIQUE | Barcode / QR Code         |
| item_name      | VARCHAR   |  150 |        | ឈ្មោះទំនិញ                |
| item_name_km   | VARCHAR   |  200 |        | ឈ្មោះទំនិញ (ខ្មែរ)        |
| unit           | VARCHAR   |   50 |        | ឯកតា pcs / box / kg       |
| purchase_price | DECIMAL   | 10,2 |        | តម្លៃទិញ                  |
| current_qty    | INT       |   11 |        | ចំនួនស្តុកបច្ចុប្បន្ន     |
| min_qty        | INT       |   11 |        | ចំនួនស្តុកអប្បបរមា        |
| description    | TEXT      |      |        | ព័ត៌មានលម្អិត             |
| status         | VARCHAR   |   20 |        | Active / Inactive         |
| created_at     | DATETIME  |      |        | ថ្ងៃបង្កើត                |
| updated_at     | DATETIME  |      |        | ថ្ងៃកែប្រែចុងក្រោយ        |

---

## 7. Table: assets

| Field Name           | Data Type | Size | Key    | Description                                          |
| -------------------- | --------- | ---: | ------ | ---------------------------------------------------- |
| asset_id             | INT       |   11 | PK     | លេខសម្គាល់ Asset                                    |
| category_id          | INT       |   11 | FK     | ភ្ជាប់ទៅ Table categories                            |
| supplier_id          | INT       |   11 | FK     | ភ្ជាប់ទៅ Table suppliers                             |
| location_id          | INT       |   11 | FK     | ទីតាំងបច្ចុប្បន្ន → Table locations                  |
| assigned_to          | INT       |   11 | FK     | User ដែលកំពុងប្រើ → Table users                      |
| asset_code           | VARCHAR   |   50 | UNIQUE | លេខកូដ Asset (AST-0001)                              |
| asset_name           | VARCHAR   |  150 |        | ឈ្មោះ Asset                                          |
| serial_number        | VARCHAR   |  100 | UNIQUE | លេខ Serial                                           |
| barcode              | VARCHAR   |  100 | UNIQUE | Barcode / QR Code                                    |
| purchase_date        | DATE      |      |        | ថ្ងៃទិញ                                              |
| purchase_price       | DECIMAL   | 10,2 |        | តម្លៃទិញ (USD)                                       |
| warranty_expiry_date | DATE      |      |        | ថ្ងៃផុតកំណត់ធានា                                     |
| asset_status         | VARCHAR   |   30 |        | Available / Assigned / Under Maintenance / Disposed  |
| description          | TEXT      |      |        | ព័ត៌មានលម្អិត                                        |
| is_active            | TINYINT   |    1 |        | 1 = Active, 0 = Deleted                              |
| created_at           | DATETIME  |      |        | ថ្ងៃបង្កើត                                           |
| updated_at           | DATETIME  |      |        | ថ្ងៃកែប្រែចុងក្រោយ                                   |

---

## 8. Table: stock_movements

| Field Name    | Data Type | Size | Key | Description                            |
| ------------- | --------- | ---: | --- | -------------------------------------- |
| movement_id   | INT       |   11 | PK  | លេខសម្គាល់ចលនាស្តុក                    |
| item_id       | INT       |   11 | FK  | ភ្ជាប់ទៅ Table inventory_items         |
| movement_type | VARCHAR   |   20 |     | IN / OUT / ADJUST                      |
| quantity      | INT       |   11 |     | ចំនួនចលនា                              |
| movement_date | TIMESTAMP |      |     | ថ្ងៃចលនា                               |
| reference_no  | VARCHAR   |  100 |     | លេខយោង                                 |
| reason        | VARCHAR   |  150 |     | Purchase / Usage / Damage / Adjustment |
| created_by    | INT       |   11 | FK  | User ដែលបញ្ចូល                         |
| remarks       | TEXT      |      |     | កំណត់ចំណាំ                             |

---

## 9. Table: asset_transfers

| Field Name       | Data Type | Size | Key | Description              |
| ---------------- | --------- | ---: | --- | ------------------------ |
| transfer_id      | INT       |   11 | PK  | លេខសម្គាល់ការផ្ទេរ Asset |
| asset_id         | INT       |   11 | FK  | Asset ដែលផ្ទេរ           |
| from_location_id | INT       |   11 | FK  | ទីតាំងចាស់               |
| to_location_id   | INT       |   11 | FK  | ទីតាំងថ្មី               |
| from_user_id     | INT       |   11 | FK  | អ្នកប្រើចាស់             |
| to_user_id       | INT       |   11 | FK  | អ្នកប្រើថ្មី             |
| transfer_date    | DATE      |      |     | ថ្ងៃផ្ទេរ                |
| transferred_by   | INT       |   11 | FK  | User ដែលធ្វើការផ្ទេរ     |
| remarks          | TEXT      |      |     | កំណត់ចំណាំ               |

---

## 10. Table: maintenance_records

| Field Name        | Data Type | Size | Key | Description            |
| ----------------- | --------- | ---: | --- | ---------------------- |
| maintenance_id    | INT       |   11 | PK  | លេខសម្គាល់ Maintenance |
| asset_id          | INT       |   11 | FK  | Asset ដែលជួសជុល        |
| maintenance_date  | DATE      |      |     | ថ្ងៃជួសជុល             |
| maintenance_type  | VARCHAR   |   50 |     | Preventive / Repair    |
| issue_description | TEXT      |      |     | បញ្ហាដែលកើតឡើង         |
| cost              | DECIMAL   | 10,2 |     | ថ្លៃជួសជុល             |
| performed_by      | VARCHAR   |  100 |     | អ្នក/ក្រុមហ៊ុនជួសជុល   |
| status            | VARCHAR   |   30 |     | Pending / Completed    |
| remarks           | TEXT      |      |     | កំណត់ចំណាំ             |

---

## 11. Table: asset_disposals

| Field Name      | Data Type | Size | Key | Description               |
| --------------- | --------- | ---: | --- | ------------------------- |
| disposal_id     | INT       |   11 | PK  | លេខសម្គាល់ការបោះចោល Asset |
| asset_id        | INT       |   11 | FK  | Asset ដែលបោះចោល           |
| disposal_date   | DATE      |      |     | ថ្ងៃបោះចោល                |
| disposal_reason | TEXT      |      |     | មូលហេតុបោះចោល             |
| disposal_value  | DECIMAL   | 10,2 |     | តម្លៃនៅសល់/តម្លៃលក់ចេញ    |
| approved_by     | INT       |   11 | FK  | Manager ដែលអនុម័ត         |
| disposed_by     | INT       |   11 | FK  | User ដែលបោះចោល            |
| remarks         | TEXT      |      |     | កំណត់ចំណាំ                |

---

## 12. Table: asset_audit_logs

| Field Name       | Data Type | Size | Key | Description              |
| ---------------- | --------- | ---: | --- | ------------------------ |
| audit_id         | INT       |   11 | PK  | លេខសម្គាល់ Audit Asset   |
| asset_id         | INT       |   11 | FK  | Asset ដែលបាន Audit       |
| location_id      | INT       |   11 | FK  | ទីតាំងពេល Audit          |
| audit_date       | DATE      |      |     | ថ្ងៃត្រួតពិនិត្យ         |
| condition_status | VARCHAR   |   50 |     | Good / Damaged / Missing |
| checked_by       | INT       |   11 | FK  | User ដែលត្រួតពិនិត្យ     |
| remarks          | TEXT      |      |     | កំណត់ចំណាំ               |

---

## 13. Table: low_stock_alerts

| Field Name  | Data Type | Size | Key | Description                    |
| ----------- | --------- | ---: | --- | ------------------------------ |
| alert_id    | INT       |   11 | PK  | លេខសម្គាល់ការជូនដំណឹងស្តុកទាប  |
| item_id     | INT       |   11 | FK  | ទំនិញដែលស្តុកទាប               |
| current_qty | INT       |   11 |     | ចំនួនស្តុកបច្ចុប្បន្ន           |
| min_qty     | INT       |   11 |     | ចំនួនស្តុកអប្បបរមា              |
| alert_date  | TIMESTAMP |      |     | ថ្ងៃជូនដំណឹង                   |
| status      | VARCHAR   |   20 |     | New / Resolved                 |

---

## 14. Table: notifications

| Field Name        | Data Type | Size | Key | Description                                   |
| ----------------- | --------- | ---: | --- | --------------------------------------------- |
| notification_id   | INT       |   11 | PK  | លេខសម្គាល់ Notification                       |
| user_id           | INT       |   11 | FK  | អ្នកទទួល Notification                         |
| title             | VARCHAR   |  150 |     | ចំណងជើង                                       |
| message           | TEXT      |      |     | ខ្លឹមសារ                                      |
| notification_type | VARCHAR   |   50 |     | Low Stock / Transfer / Maintenance / Disposal |
| is_read           | BOOLEAN   |      |     | បានអានឬនៅ                                     |
| created_at        | TIMESTAMP |      |     | ថ្ងៃបង្កើត                                    |

---

## 15. Table: reports

| Field Name   | Data Type | Size | Key | Description                                |
| ------------ | --------- | ---: | --- | ------------------------------------------ |
| report_id    | INT       |   11 | PK  | លេខសម្គាល់ Report                          |
| report_type  | VARCHAR   |   50 |     | Inventory / Asset / Maintenance / Disposal |
| report_date  | DATE      |      |     | កាលបរិច្ឆេទ Report                         |
| generated_by | INT       |   11 | FK  | User ដែលបង្កើត                             |
| file_path    | VARCHAR   |  255 |     | ទីតាំង File Report                         |
| created_at   | TIMESTAMP |      |     | ថ្ងៃបង្កើត                                 |

---

## Relationships

| Table A           | Cardinality | Table B               |
| ----------------- | ----------- | --------------------- |
| roles             | 1 ↔ many    | users                 |
| categories        | 1 ↔ many    | inventory_items       |
| categories        | 1 ↔ many    | assets                |
| suppliers         | 1 ↔ many    | inventory_items       |
| suppliers         | 1 ↔ many    | assets                |
| locations         | 1 ↔ many    | assets                |
| inventory_items   | 1 ↔ many    | stock_movements       |
| inventory_items   | 1 ↔ many    | low_stock_alerts      |
| assets            | 1 ↔ many    | asset_transfers       |
| assets            | 1 ↔ many    | maintenance_records   |
| assets            | 1 ↔ 1       | asset_disposals       |
| assets            | 1 ↔ many    | asset_audit_logs      |
| users             | 1 ↔ many    | stock_movements       |
| users             | 1 ↔ many    | asset_transfers       |
| users             | 1 ↔ many    | asset_disposals       |
| users             | 1 ↔ many    | asset_audit_logs      |
| users             | 1 ↔ many    | notifications         |
| users             | 1 ↔ many    | reports               |

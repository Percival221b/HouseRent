CREATE DATABASE IF NOT EXISTS house_rent
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE house_rent;

CREATE TABLE IF NOT EXISTS users (
  id BIGINT NOT NULL AUTO_INCREMENT,
  username VARCHAR(80) NOT NULL,
  email VARCHAR(120) NULL,
  phone VARCHAR(30) NULL,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('tenant', 'landlord', 'admin', 'system_admin') NOT NULL DEFAULT 'tenant',
  real_name VARCHAR(80) NULL,
  avatar_url VARCHAR(255) NULL,
  id_card_number VARCHAR(30) NULL,
  status ENUM('active', 'disabled', 'pending') NOT NULL DEFAULT 'active',
  two_factor_enabled BOOLEAN NOT NULL DEFAULT FALSE,
  login_fail_count INT NOT NULL DEFAULT 0,
  locked_until DATETIME NULL,
  last_login_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_username (username),
  UNIQUE KEY uq_users_email (email),
  UNIQUE KEY uq_users_phone (phone),
  KEY idx_users_role (role),
  KEY idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS verification_codes (
  id BIGINT NOT NULL AUTO_INCREMENT,
  target VARCHAR(120) NOT NULL,
  code VARCHAR(10) NOT NULL,
  code_type VARCHAR(20) NOT NULL DEFAULT 'register',
  expires_at DATETIME NOT NULL,
  used BOOLEAN NOT NULL DEFAULT FALSE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_verification_codes_target (target),
  KEY idx_verification_codes_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS login_logs (
  id BIGINT NOT NULL AUTO_INCREMENT,
  user_id BIGINT NULL,
  ip_address VARCHAR(45) NULL,
  device_info VARCHAR(255) NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'success',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_login_logs_user_id (user_id),
  KEY idx_login_logs_created_at (created_at),
  CONSTRAINT fk_login_logs_user
    FOREIGN KEY (user_id) REFERENCES users (id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS houses (
  id BIGINT NOT NULL AUTO_INCREMENT,
  landlord_id BIGINT NOT NULL,
  title VARCHAR(120) NOT NULL,
  address VARCHAR(255) NOT NULL,
  district VARCHAR(80) NULL,
  business_area VARCHAR(120) NULL,
  community VARCHAR(120) NULL,
  layout VARCHAR(50) NULL,
  house_type VARCHAR(50) NULL,
  floor INT NULL,
  total_floor INT NULL,
  orientation VARCHAR(30) NULL,
  area DECIMAL(10, 2) NULL,
  rent DECIMAL(10, 2) NOT NULL,
  deposit DECIMAL(10, 2) NULL,
  decoration VARCHAR(50) NULL,
  facilities JSON NULL,
  status ENUM('vacant', 'rented', 'maintenance', 'offline') NOT NULL DEFAULT 'vacant',
  description TEXT NULL,
  video_url VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_houses_landlord_id (landlord_id),
  KEY idx_houses_district (district),
  KEY idx_houses_layout (layout),
  KEY idx_houses_rent (rent),
  KEY idx_houses_status (status),
  CONSTRAINT fk_houses_landlord
    FOREIGN KEY (landlord_id) REFERENCES users (id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS house_images (
  id BIGINT NOT NULL AUTO_INCREMENT,
  house_id BIGINT NOT NULL,
  file_path VARCHAR(255) NOT NULL,
  caption VARCHAR(120) NULL,
  sort_order INT NOT NULL DEFAULT 0,
  is_cover BOOLEAN NOT NULL DEFAULT FALSE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_house_images_house_id (house_id),
  CONSTRAINT fk_house_images_house
    FOREIGN KEY (house_id) REFERENCES houses (id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS appointments (
  id BIGINT NOT NULL AUTO_INCREMENT,
  house_id BIGINT NOT NULL,
  tenant_id BIGINT NOT NULL,
  landlord_id BIGINT NOT NULL,
  appointment_time DATETIME NOT NULL,
  status ENUM('pending', 'approved', 'rejected', 'cancelled', 'completed') NOT NULL DEFAULT 'pending',
  remark TEXT NULL,
  reply TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_appointments_house_id (house_id),
  KEY idx_appointments_tenant_id (tenant_id),
  KEY idx_appointments_landlord_id (landlord_id),
  KEY idx_appointments_status (status),
  CONSTRAINT fk_appointments_house
    FOREIGN KEY (house_id) REFERENCES houses (id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_appointments_tenant
    FOREIGN KEY (tenant_id) REFERENCES users (id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_appointments_landlord
    FOREIGN KEY (landlord_id) REFERENCES users (id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS messages (
  id BIGINT NOT NULL AUTO_INCREMENT,
  sender_id BIGINT NOT NULL,
  receiver_id BIGINT NOT NULL,
  house_id BIGINT NULL,
  content TEXT NOT NULL,
  message_type ENUM('text', 'system', 'auto_reply') NOT NULL DEFAULT 'text',
  is_read BOOLEAN NOT NULL DEFAULT FALSE,
  read_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_messages_sender_id (sender_id),
  KEY idx_messages_receiver_id (receiver_id),
  KEY idx_messages_house_id (house_id),
  CONSTRAINT fk_messages_sender
    FOREIGN KEY (sender_id) REFERENCES users (id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_messages_receiver
    FOREIGN KEY (receiver_id) REFERENCES users (id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_messages_house
    FOREIGN KEY (house_id) REFERENCES houses (id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS contracts (
  id BIGINT NOT NULL AUTO_INCREMENT,
  contract_no VARCHAR(40) NOT NULL,
  house_id BIGINT NOT NULL,
  tenant_id BIGINT NOT NULL,
  landlord_id BIGINT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  monthly_rent DECIMAL(10, 2) NOT NULL,
  deposit DECIMAL(10, 2) NULL,
  status ENUM('draft', 'pending_signed', 'active', 'ended', 'cancelled') NOT NULL DEFAULT 'draft',
  content TEXT NULL,
  signed_by_landlord_at DATETIME NULL,
  signed_by_tenant_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_contracts_contract_no (contract_no),
  KEY idx_contracts_house_id (house_id),
  KEY idx_contracts_tenant_id (tenant_id),
  KEY idx_contracts_landlord_id (landlord_id),
  KEY idx_contracts_status (status),
  CONSTRAINT fk_contracts_house
    FOREIGN KEY (house_id) REFERENCES houses (id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_contracts_tenant
    FOREIGN KEY (tenant_id) REFERENCES users (id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_contracts_landlord
    FOREIGN KEY (landlord_id) REFERENCES users (id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS payments (
  id BIGINT NOT NULL AUTO_INCREMENT,
  contract_id BIGINT NOT NULL,
  payer_id BIGINT NOT NULL,
  amount DECIMAL(10, 2) NOT NULL,
  payment_type ENUM('rent', 'deposit', 'other') NOT NULL DEFAULT 'rent',
  payment_method ENUM('mock', 'cash', 'alipay', 'wechat', 'bank_card') NOT NULL DEFAULT 'mock',
  status ENUM('pending', 'paid', 'overdue', 'refunded', 'cancelled') NOT NULL DEFAULT 'pending',
  due_date DATE NULL,
  paid_at DATETIME NULL,
  transaction_no VARCHAR(80) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_payments_contract_id (contract_id),
  KEY idx_payments_payer_id (payer_id),
  KEY idx_payments_status (status),
  KEY idx_payments_due_date (due_date),
  CONSTRAINT fk_payments_contract
    FOREIGN KEY (contract_id) REFERENCES contracts (id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_payments_payer
    FOREIGN KEY (payer_id) REFERENCES users (id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS repair_requests (
  id BIGINT NOT NULL AUTO_INCREMENT,
  house_id BIGINT NOT NULL,
  tenant_id BIGINT NOT NULL,
  handler_id BIGINT NULL,
  title VARCHAR(120) NOT NULL,
  description TEXT NOT NULL,
  status ENUM('pending', 'processing', 'finished', 'rejected') NOT NULL DEFAULT 'pending',
  result TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  handled_at DATETIME NULL,
  PRIMARY KEY (id),
  KEY idx_repair_requests_house_id (house_id),
  KEY idx_repair_requests_tenant_id (tenant_id),
  KEY idx_repair_requests_handler_id (handler_id),
  KEY idx_repair_requests_status (status),
  CONSTRAINT fk_repair_requests_house
    FOREIGN KEY (house_id) REFERENCES houses (id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_repair_requests_tenant
    FOREIGN KEY (tenant_id) REFERENCES users (id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_repair_requests_handler
    FOREIGN KEY (handler_id) REFERENCES users (id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS complaints (
  id BIGINT NOT NULL AUTO_INCREMENT,
  house_id BIGINT NULL,
  tenant_id BIGINT NOT NULL,
  target_user_id BIGINT NULL,
  handler_id BIGINT NULL,
  title VARCHAR(120) NOT NULL,
  content TEXT NOT NULL,
  status ENUM('pending', 'processing', 'resolved', 'rejected') NOT NULL DEFAULT 'pending',
  result TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  handled_at DATETIME NULL,
  PRIMARY KEY (id),
  KEY idx_complaints_house_id (house_id),
  KEY idx_complaints_tenant_id (tenant_id),
  KEY idx_complaints_target_user_id (target_user_id),
  KEY idx_complaints_handler_id (handler_id),
  KEY idx_complaints_status (status),
  CONSTRAINT fk_complaints_house
    FOREIGN KEY (house_id) REFERENCES houses (id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_complaints_tenant
    FOREIGN KEY (tenant_id) REFERENCES users (id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_complaints_target_user
    FOREIGN KEY (target_user_id) REFERENCES users (id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_complaints_handler
    FOREIGN KEY (handler_id) REFERENCES users (id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS news (
  id BIGINT NOT NULL AUTO_INCREMENT,
  author_id BIGINT NOT NULL,
  title VARCHAR(150) NOT NULL,
  category VARCHAR(50) NULL,
  content TEXT NOT NULL,
  is_published BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_news_author_id (author_id),
  KEY idx_news_is_published (is_published),
  CONSTRAINT fk_news_author
    FOREIGN KEY (author_id) REFERENCES users (id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS system_logs (
  id BIGINT NOT NULL AUTO_INCREMENT,
  user_id BIGINT NULL,
  action VARCHAR(120) NOT NULL,
  detail TEXT NULL,
  ip_address VARCHAR(45) NULL,
  user_agent VARCHAR(255) NULL,
  method VARCHAR(10) NULL,
  path VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_system_logs_user_id (user_id),
  KEY idx_system_logs_action (action),
  KEY idx_system_logs_created_at (created_at),
  CONSTRAINT fk_system_logs_user
    FOREIGN KEY (user_id) REFERENCES users (id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

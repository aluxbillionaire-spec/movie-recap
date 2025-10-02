CREATE TABLE `users` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `email_verified_at` TIMESTAMP NULL,
    `password` VARCHAR(255) NOT NULL,
    `remember_token` VARCHAR(100) NULL,
    `created_at` TIMESTAMP NULL,
    `updated_at` TIMESTAMP NULL
);

CREATE TABLE `password_reset_tokens` (
    `email` VARCHAR(255) NOT NULL PRIMARY KEY,
    `token` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP NULL
);

CREATE TABLE `sessions` (
    `id` VARCHAR(255) NOT NULL PRIMARY KEY,
    `user_id` BIGINT UNSIGNED NULL,
    `ip_address` VARCHAR(45) NULL,
    `user_agent` TEXT NULL,
    `payload` LONGTEXT NOT NULL,
    `last_activity` INTEGER NOT NULL,
    INDEX `sessions_user_id_index` (`user_id`),
    INDEX `sessions_last_activity_index` (`last_activity`)
);

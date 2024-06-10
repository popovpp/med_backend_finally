CREATE TABLE `users_payments` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`client_user_payment_id` INT,
	`payment_system_id` INT NOT NULL,
	`payment_date` TIME NOT NULL,
	`user_id` INT NOT NULL,
	`amount_to_pay` float4 NOT NULL,
	`paid_amount` float4 NOT NULL DEFAULT '0',
	`payment_status` INT NOT NULL,
	`payment_transaction_id` INT NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `payments_systems` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`client_payment_system_id` INT,
	`name` varchar(200) NOT NULL UNIQUE,
	`description` varchar(500) NOT NULL,
	`is_active` INT NOT NULL DEFAULT true,
	PRIMARY KEY (`id`)
);

CREATE TABLE `users_purchases` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`client_user_purchases-id` INT,
	`user_payment_id` INT NOT NULL,
	`service_id` INT NOT NULL,
	`price_id` float4 NOT NULL,
	`discount` INT(0) NOT NULL,
	`amount` float4 NOT NULL,
	`service_was_used` bool NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `prices` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`client_price_id` INT,
	`price_name_id` INT NOT NULL,
	`service_id` INT NOT NULL,
	`price_period_id` INT NOT NULL,
	`price_type_id` INT NOT NULL,
	`price` float4 NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `services` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`client_service_id` INT,
	`service_type_id` INT NOT NULL,
	`name` varchar(100) NOT NULL,
	`comment` varchar(500),
	`description` TEXT,
	`applied_method` varchar(500),
	`preparation_rules` TEXT,
	`is_active` bool,
	PRIMARY KEY (`id`)
);

ALTER TABLE `users_payments` ADD CONSTRAINT `users_payments_fk0` FOREIGN KEY (`payment_system_id`) REFERENCES `payments_systems`(`id`);

ALTER TABLE `users_payments` ADD CONSTRAINT `users_payments_fk1` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`);

ALTER TABLE `users_purchases` ADD CONSTRAINT `users_purchases_fk0` FOREIGN KEY (`user_payment_id`) REFERENCES `users_payments`(`id`);

ALTER TABLE `users_purchases` ADD CONSTRAINT `users_purchases_fk1` FOREIGN KEY (`service_id`) REFERENCES `services`(`id`);

ALTER TABLE `users_purchases` ADD CONSTRAINT `users_purchases_fk2` FOREIGN KEY (`price_id`) REFERENCES `prices`(`id`);

ALTER TABLE `prices` ADD CONSTRAINT `prices_fk0` FOREIGN KEY (`price_name_id`) REFERENCES `prices_names`(`id`);

ALTER TABLE `prices` ADD CONSTRAINT `prices_fk1` FOREIGN KEY (`service_id`) REFERENCES `services`(`id`);

ALTER TABLE `prices` ADD CONSTRAINT `prices_fk2` FOREIGN KEY (`price_period_id`) REFERENCES `prices_periods`(`id`);

ALTER TABLE `prices` ADD CONSTRAINT `prices_fk3` FOREIGN KEY (`price_type_id`) REFERENCES `prices_types`(`id`);

ALTER TABLE `services` ADD CONSTRAINT `services_fk0` FOREIGN KEY (`service_type_id`) REFERENCES `services_types`(`id`);







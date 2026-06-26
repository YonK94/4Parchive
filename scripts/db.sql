-- CREATE TABLE part_list
CREATE TABLE `part_list` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`part_name` VARCHAR(128) NOT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`product_name` VARCHAR(128) NULL DEFAULT 'RING' COLLATE 'utf8mb4_uca1400_ai_ci',
	`description` VARCHAR(128) NULL DEFAULT NULL COLLATE 'utf8mb4_uca1400_ai_ci',

	PRIMARY KEY (`id`),
	UNIQUE KEY `idx_part_name` (`part_name`)
);

-- CREATE TABLE measurement
CREATE TABLE `measurement` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`lot_no` CHAR(13) NOT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`part_id` INT NOT NULL,
	`process` VARCHAR(32) NOT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`measured_datetime` DATETIME NOT NULL,
	`worked_machine` VARCHAR(32) NOT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`dim_name` VARCHAR(64) NOT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`dim` FLOAT NULL DEFAULT NULL,
	`dim_basic` FLOAT NULL DEFAULT NULL,
	`tol_upper` FLOAT NULL DEFAULT NULL,
	`tol_lower` FLOAT NULL DEFAULT NULL,
	`is_pass` TINYINT NULL DEFAULT NULL,
	`serial_no` VARCHAR(32) NULL DEFAULT NULL COLLATE 'utf8mb4_uca1400_ai_ci',
	`worker` VARCHAR(32) NULL DEFAULT NULL COLLATE 'utf8mb4_uca1400_ai_ci',

	PRIMARY KEY (`id`, `lot_no`),
	CONSTRAINT `check_lot_no_format` CHECK (`lot_no` LIKE 'KK2%')
)

PARTITION BY RANGE COLUMNS(lot_no) (
    PARTITION p_past VALUES LESS THAN ('KK2026'),
    PARTITION p2026 VALUES LESS THAN ('KK2027'),
    PARTITION p2027 VALUES LESS THAN ('KK2028'),
    PARTITION p2028 VALUES LESS THAN ('KK2029'),
    PARTITION p2029 VALUES LESS THAN ('KK2030'),
    PARTITION p2030 VALUES LESS THAN ('KK2031'),
    PARTITION p_future VALUES LESS THAN (MAXVALUE)
);

CREATE INDEX idx_lot_process ON measurement (lot_no, process);
CREATE INDEX idx_part_process ON measurement (part_id, process);
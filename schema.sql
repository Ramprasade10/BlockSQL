CREATE TABLE IF NOT EXISTS `teacher_details` (
	`teacher_id`	VARCHAR ( 10 ),
	`teacher_name`	VARCHAR ( 30 ) NOT NULL,
	`pwd`	VARCHAR ( 100 ) NOT NULL,
	`designation`	VARCHAR ( 30 ) NOT NULL,
	`doj`	DATE NOT NULL,
	`branch`	VARCHAR ( 45 ) NOT NULL,
	`phone_no`	INTEGER ( 10 ) NOT NULL UNIQUE,
	`email`	VARCHAR ( 30 ) NOT NULL UNIQUE,
	PRIMARY KEY(`teacher_id`)
);
CREATE TABLE IF NOT EXISTS `student_details` (
	`sgpa1`	float ( 4 , 2 ),
	`sgpa2`	float ( 4 , 2 ),
	`sgpa3`	float ( 4 , 2 ),
	`sgpa4`	float ( 4 , 2 ),
	`sgpa5`	float ( 4 , 2 ),
	`sgpa6`	float ( 4 , 2 ),
	`sgpa7`	float ( 4 , 2 ),
	`sgpa8`	float ( 4 , 2 ),
	`cgpa`	float ( 4 , 2 ),
	`usn`	VARCHAR ( 10 ) NOT NULL,
	`student_name`	VARCHAR ( 30 ) NOT NULL,
	`pwd`	VARCHAR ( 100 ) NOT NULL,
	`sem`	INTEGER ( 1 ) NOT NULL,
	`section`	VARCHAR ( 1 ) NOT NULL,
	`branch`	VARCHAR ( 45 ) NOT NULL,
	`email`	VARCHAR ( 30 ) NOT NULL,
	`phone_no`	INTEGER ( 10 ) NOT NULL,
	`year_start`	DATE NOT NULL,
	`year_end`	DATE NOT NULL,
	`fathers_name`	VARCHAR ( 50 ) NOT NULL,
	`counselor_teacher_id`	VARCHAR ( 10 ) NOT NULL,
	`time_stamp`	timestamp NOT NULL,
	`prev_block_hash`	VARCHAR ( 100 ) NOT NULL,
	`block_hash`	VARCHAR ( 100 ) NOT NULL,
	FOREIGN KEY(`counselor_teacher_id`) REFERENCES `teacher_details`(`teacher_id`)
);
CREATE TABLE IF NOT EXISTS `marks` (
	`result_year`	varchar ( 10 ) NOT NULL,
	`result_type`	varchar ( 7 ) NOT NULL,
	`branch`	varchar ( 3 ),
	`sem`	INTEGER ( 1 ) NOT NULL,
	`section`	varchar ( 1 ),
	`usn`	varchar ( 10 ) NOT NULL,
	`course_code`	varchar ( 6 ) NOT NULL,
	`grade`	VARCHAR ( 2 ),
	`grade_point`	float ( 4 , 2 ),
	`credits`	float ( 2 , 1 ),
	`int1`	INTEGER ( 2 ),
	`int2`	INTEGER ( 2 ),
	`int3`	INTEGER ( 2 ),
	`cie`	INTEGER ( 2 ),
	`see`	INTEGER ( 3 ),
	`total_marks`	INTEGER ( 3 ),
	`time_stamp`	timestamp NOT NULL,
	`prev_block_hash`	VARCHAR ( 100 ) NOT NULL,
	`block_hash`	VARCHAR ( 100 ) NOT NULL
);
CREATE TABLE IF NOT EXISTS `login_ledger` (
	`usn`	varchar ( 10 ) NOT NULL,
	`user_type`	varchar ( 10 ) NOT NULL,
	`log_in`	TIMESTAMP NOT NULL,
	`log_out`	TIMESTAMP
);
CREATE TABLE IF NOT EXISTS `database_admin` (
	`admin_name`	VARCHAR ( 30 ) NOT NULL,
	`admin_id`	VARCHAR ( 10 ),
	`pwd`	VARCHAR ( 100 ) NOT NULL,
	`email`	varchar ( 100 ) NOT NULL UNIQUE,
	PRIMARY KEY(`admin_id`)
);
CREATE TABLE IF NOT EXISTS `course` (
	`course_code`	varchar ( 6 ),
	`course_name`	varchar ( 30 ) NOT NULL,
	`credits`	float ( 2 , 1 ) NOT NULL,
	PRIMARY KEY(`course_code`)
);
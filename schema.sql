-- Active: 1773861604957@@regs26-sharma.ca1y0o4q8i1b.us-east-1.rds.amazonaws.com@3306@university

-- USE DATABASE university;

CREATE DATABASE IF NOT EXISTS university
    DEFAULT CHARACTER SET = 'utf8mb4';
USE university;

SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  uid          int(8) NOT NULL,
  username     varchar(20) NOT NULL,
  password     varchar(255) NOT NULL,
  role         varchar(10) NOT NULL,
  fname        varchar(20) NOT NULL,
  lname        varchar(20) NOT NULL,
  email        varchar(50),
  address      varchar(50),
  PRIMARY KEY (uid)
);

DROP TABLE IF EXISTS students;
CREATE TABLE students (
  uid               int(8) NOT NULL,
  program           varchar(10),
  advisor_id        int(8),
  graduation_status varchar(30),
  enrollment_year   varchar(4),
  registration_hold BOOLEAN DEFAULT TRUE,
  PRIMARY KEY (uid),
  FOREIGN KEY (advisor_id) REFERENCES faculty(uid),
  FOREIGN KEY (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS faculty;
CREATE TABLE faculty (
  uid   int(8) NOT NULL,
  cac BOOLEAN,
  reviewer BOOLEAN,
  advisor BOOLEAN,
  PRIMARY KEY (uid),
  FOREIGN KEY (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS secretary;
CREATE TABLE secretary (
  uid   int(8) NOT NULL,
  PRIMARY KEY (uid),
  FOREIGN KEY (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS alumni;
CREATE TABLE alumni (
  uid               int(8) NOT NULL,
  degree            varchar(20),
  graduation_year   int(4),
  graduation_semester varchar(10),
  PRIMARY KEY (uid),
  FOREIGN KEY (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS applicant;
CREATE TABLE applicant (
  uid               int(8) NOT NULL,
  ssn CHAR(11) NOT NULL UNIQUE,  -- Format: XXX-XX-XXXX
  degree            varchar(20),
  gre_verbal        INTEGER,
  gre_quant INTEGER,  -- GRE quantitative score
  gre_year INTEGER,  -- Year the GRE exam was taken
  work_experience TEXT,  -- Prior work experience
  areas_of_interest TEXT,  -- Areas of interest
  transcript_received BOOLEAN DEFAULT FALSE,
  transcript_method VARCHAR(10) DEFAULT NULL,
  transcript_path VARCHAR(255) DEFAULT NULL,
  deposit_submitted BOOLEAN DEFAULT FALSE,
  year_applied int(4),
  semester_applied varchar(10),
  status VARCHAR(50) DEFAULT 'incomplete',  -- e.g., 'incomplete', 'under review', 'admitted', 'rejected'
  PRIMARY KEY (uid),
  FOREIGN KEY (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS prior_degree;
CREATE TABLE prior_degree (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  uid           int(8) NOT NULL,
  degree_type   varchar(20),
  year          int(4),
  gpa           decimal(3,2),
  university    varchar(100),
  FOREIGN KEY (uid) REFERENCES applicant(uid)
);

DROP TABLE IF EXISTS gre_subject;
CREATE TABLE gre_subject (
  id      INT AUTO_INCREMENT PRIMARY KEY,
  uid     int(8) NOT NULL,
  subject varchar(50),
  score   int(4),
  year    int(4),
  FOREIGN KEY (uid) REFERENCES applicant(uid)
);

DROP TABLE IF EXISTS recommendation_letter;
CREATE TABLE recommendation_letter (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  uid              int(8) NOT NULL,
  writer_name      varchar(100),
  writer_email     varchar(100),
  writer_title     varchar(100),
  institution_name varchar(100),
  letter_content   TEXT,
  is_submitted     BOOLEAN DEFAULT FALSE,
  submission_date  DATETIME,
  rating           int(1),
  is_generic       CHAR(1),
  is_credible      CHAR(1),
  FOREIGN KEY (uid) REFERENCES applicant(uid)
);

DROP TABLE IF EXISTS app_review;
CREATE TABLE app_review (
  id                  INT AUTO_INCREMENT PRIMARY KEY,
  uid                 int(8) NOT NULL,
  reviewer_uid        int(8) NOT NULL,
  rating              int(1),
  deficiency_courses  TEXT,
  reject_reasons      varchar(50),
  comment             TEXT,
  recommended_advisor int(8),
  FOREIGN KEY (uid) REFERENCES applicant(uid),
  FOREIGN KEY (reviewer_uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
  course_number   int(4) NOT NULL,
  title           varchar(50) NOT NULL,
  credits         int(2),
  department      varchar(10),
  PRIMARY KEY (course_number, department)
);

DROP TABLE IF EXISTS prereqs;
CREATE TABLE prereqs (
  coursenumber int(4),
  dptname varchar(10),
  prereqnum int(4),
  prereqdpt varchar(10),
  primary key(coursenumber, dptname, prereqnum, prereqdpt),
  foreign key (coursenumber, dptname) references courses(course_number, department),
  foreign key (prereqnum, prereqdpt) references courses(course_number,department)
);


DROP TABLE IF EXISTS enrollment;
CREATE TABLE enrollment (
  uid           int(8) NOT NULL,
  course_number int(4) NOT NULL,
  department    varchar(10) NOT NULL DEFAULT 'CSCI',
  semester      varchar(10),
  year          int(4),
  grade         varchar(2),
  credit_hours  int(2),
  sectionnum    int(2),
  prof_added    BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (uid, course_number, department, semester, year, sectionnum),
  FOREIGN KEY (uid) REFERENCES users(uid),
  FOREIGN KEY (course_number, department) REFERENCES courses(course_number, department)
);

DROP TABLE IF EXISTS form;
CREATE TABLE form (
  form_id               int(8) NOT NULL,
  uid                   int(8) NOT NULL,
  program_type          varchar(10) NOT NULL,
  advisor_approval      varchar(10),
  thesis                text,
  PRIMARY KEY (form_id),
  UNIQUE (uid),
  FOREIGN KEY (uid) REFERENCES students(uid)
);

DROP TABLE IF EXISTS form_courses;
CREATE TABLE form_courses (
  form_id                   int(8) NOT NULL,
  course_number             int(4) NOT NULL,
  department                varchar(10) NOT NULL DEFAULT 'CSCI',
  semester_planned          varchar(10),
  year_planned              int(4),
  PRIMARY KEY (form_id, course_number, department),
  FOREIGN KEY (form_id) REFERENCES form(form_id),
  FOREIGN KEY (course_number, department) REFERENCES courses(course_number, department)
);

DROP TABLE IF EXISTS programs;
CREATE TABLE programs (
  program_name              varchar(10) NOT NULL,
  core_courses              varchar(100),
  min_gpa                   decimal(2,1),
  credits_required          int(2),
  credits_required_cs       int(2),
  max_outside_courses       int(2),
  max_grades_below_B        int(2),
  pass_thesis_defense      varchar(10),
  PRIMARY KEY (program_name)
);

DROP TABLE IF EXISTS future_phds;
CREATE TABLE future_phds (
  program_name           varchar(30) NOT NULL,
  PRIMARY KEY (program_name)
);

DROP TABLE IF EXISTS courses_offered;
CREATE TABLE courses_offered (
  departmentname varchar(10),
  coursenumber int(4),
  roomno varchar(4),
  day varchar(1),
  time varchar(9),
  sectionnum varchar(2),
  instructorid int(8),
  buildingname varchar(10),
  semester varchar(6),
  year varchar(4),
  capacity int(2),
  primary key (departmentname, coursenumber, semester, sectionnum, year),
  foreign key (coursenumber, departmentname) references courses(course_number, department),
  foreign key (instructorid) references users(uid)
);

SET FOREIGN_KEY_CHECKS=1;

-- inserting future_phds
INSERT INTO future_phds (program_name) VALUES ("Cybersecurity");
INSERT INTO future_phds (program_name) VALUES ("Machine Learning");
INSERT INTO future_phds (program_name) VALUES ("Cloud Computing");
INSERT INTO future_phds (program_name) VALUES ("AI");


-- inserting programs 
INSERT INTO programs (program_name, core_courses, min_gpa, credits_required, credits_required_cs, max_outside_courses, max_grades_below_B, pass_thesis_defense) VALUES ('MS', 'CSCI 6212, CSCI 6221, CSCI 6461', 3.0, 30, NULL, 2, 2, NULL); 
INSERT INTO programs (program_name, core_courses, min_gpa, credits_required, credits_required_cs, max_outside_courses, max_grades_below_B, pass_thesis_defense) VALUES ('PhD', NULL, 3.5, 36, 30, NULL, 1, 'required'); 


-- ADS
-- inserting users from the sample data
INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (55555555,'55555555', 'pass', 'student','Paul', 'McCartney', 'paulmccarney@gmail.com', 'Brooklyn');
INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (66666666, '66666666', 'pass', 'student','George', 'Harrison', 'georgeharrison@gmail.com', 'Manhattan');
INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (87654321, '87654321', 'pass','student','Ringo', 'Starr', 'ringostarr@gmail.com', 'Paris');
INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (12121212, '12121212', 'pass','faculty','Gabe', 'Parmer', 'gabeparmer@gmail.com', 'Balitmore');
INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (21212121, '21212121', 'pass','faculty','Bhagirath', 'Narahari', 'bhagirathnarahari@gmail.com', 'Boston');
INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (11111112, '11111112', 'pass','faculty','Tim', 'Wood', 'timwood@gmail.com', 'Aldie');
INSERT INTO users(uid, username, password, role, fname, lname, email, address) VALUES (11111113, '11111113', 'pass','faculty','Rachelle', 'Heller', 'rheller@gmail.com', 'Aldie');

INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (31313131, '31313131', 'pass','secretary','Bob', 'Smith', 'bobsmith@gmail.com', 'Lawrenceville');
INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (77777777, '77777777', 'pass','alumni','Eric', 'Clapton', 'ericclapton@gmail.com', 'Richmond');
INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (41414141, '41414141', 'pass','admin','Ava', 'White', 'avawhite@gmail.com', 'Andover');

-- inserting faculty/advisor from the sample data
INSERT INTO faculty(uid, cac, reviewer, advisor) VALUES (12121212, true, false, true);
INSERT INTO faculty(uid, cac, reviewer, advisor) VALUES (21212121, false, true, true);
INSERT INTO faculty(uid, cac, reviewer, advisor) VALUES (11111112, false, true, true);
INSERT INTO faculty(uid, cac, reviewer, advisor) VALUES (11111113, false, true, true);


-- inserting students from the sample data
INSERT INTO students (uid, program, advisor_id, graduation_status, enrollment_year, registration_hold) VALUES(55555555, 'MS', 21212121, 'active', 2023, TRUE);
INSERT INTO students (uid, program, advisor_id, graduation_status, enrollment_year, registration_hold) VALUES(66666666, 'MS', 12121212, 'active', 2024, TRUE);
INSERT INTO students (uid, program, advisor_id, graduation_status, enrollment_year, registration_hold) VALUES(87654321, 'PhD', 12121212, 'active', 2023, TRUE);

-- inserting alumni from the sample data  
INSERT INTO alumni (uid, degree, graduation_year, graduation_semester) VALUES (77777777, 'MS', 2014, 'Fall');

-- inserting grad secretary from the sample data  
INSERT INTO secretary (uid) VALUES (31313131);

-- inserting courses
INSERT INTO courses (course_number, title, credits, department) VALUES (6221, 'SW Paradigms', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6461, 'Computer Architecture', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6212, 'Algorithms', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6220, 'Machine Learning', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6232, 'Networks 1', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6233, 'Networks 2', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6241, 'Database 1', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6242, 'Database 2', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6246, 'Compilers', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6260, 'Multimedia', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6251, 'Cloud Computing', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6254, 'SW Engineering', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6262, 'Graphics 1', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6283, 'Security 1', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6284, 'Cryptography', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6286, 'Network Security', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6325, 'Algorithms 2', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6339, 'Embedded Systems', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6384, 'Cryptography 2', 3, 'CSCI');
INSERT INTO courses (course_number, title, credits, department) VALUES (6241, 'Communication Theory', 3, 'ECE');
INSERT INTO courses (course_number, title, credits, department) VALUES (6242, 'Information Theory', 2, 'ECE');
INSERT INTO courses (course_number, title, credits, department) VALUES (6210, 'Logic', 2, 'MATH');


-- inserting courses for Paul 
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (55555555, 6221, 'CSCI', 'Fall', 2022, 'A', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (55555555, 6212, 'CSCI', 'Fall', 2022, 'A', 3, 11, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (55555555, 6461, 'CSCI', 'Spring', 2023, 'A', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (55555555, 6232, 'CSCI', 'Spring', 2023, 'A', 3, 11, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (55555555, 6233, 'CSCI', 'Fall', 2023, 'A', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (55555555, 6241, 'CSCI', 'Fall', 2023, 'B', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (55555555, 6246, 'CSCI', 'Spring', 2024, 'B', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (55555555, 6262, 'CSCI', 'Spring', 2024, 'B', 3, 10,true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (55555555, 6283, 'CSCI', 'Fall', 2024, 'B', 3, 11, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (55555555, 6242, 'CSCI', 'Fall', 2024, 'B', 3, 10, true);

-- inserting courses for George 
-- George's Fall 2022 6242 is ECE (Information Theory, 2 credits) not CSCI (Database 2, 3 credits)
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (66666666, 6242, 'ECE', 'Fall', 2022, 'C', 2, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (66666666, 6221, 'CSCI', 'Fall', 2022, 'B', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (66666666, 6461, 'CSCI', 'Fall', 2022, 'B', 3, 11, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (66666666, 6212, 'CSCI', 'Spring', 2023, 'B', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (66666666, 6232, 'CSCI', 'Spring', 2023, 'B', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (66666666, 6233, 'CSCI', 'Fall', 2023, 'B', 3, 11, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (66666666, 6241, 'CSCI', 'Fall', 2023, 'B', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (66666666, 6242, 'CSCI', 'Spring', 2024, 'B', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (66666666, 6283, 'CSCI', 'Spring', 2024, 'B', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (66666666, 6284, 'CSCI', 'Fall', 2024, 'B', 3, 10, true);

-- inserting courses for Ringo
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (87654321, 6221, 'CSCI', 'Fall', 2022, 'A', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (87654321, 6212, 'CSCI', 'Fall', 2022, 'A', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (87654321, 6461, 'CSCI', 'Spring', 2023, 'A', 3, 11, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (87654321, 6232, 'CSCI', 'Spring', 2023, 'A', 3, 11, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (87654321, 6233, 'CSCI', 'Fall', 2023, 'A', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (87654321, 6241, 'CSCI', 'Fall', 2023, 'A', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (87654321, 6242, 'CSCI', 'Spring', 2024, 'A', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (87654321, 6246, 'CSCI', 'Spring', 2024, 'A', 3, 11, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (87654321, 6262, 'CSCI', 'Fall', 2024, 'A', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (87654321, 6283, 'CSCI', 'Fall', 2024, 'A', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (87654321, 6284, 'CSCI', 'Spring', 2025, 'A', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (87654321, 6286, 'CSCI', 'Spring', 2025, 'A', 3, 11, true);

-- inserting courses for Eric
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (77777777, 6221, 'CSCI', 'Fall', 2010, 'B', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (77777777, 6212, 'CSCI', 'Fall', 2010, 'B', 3, 11, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (77777777, 6461, 'CSCI', 'Spring', 2011, 'B', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (77777777, 6232, 'CSCI', 'Spring', 2011, 'B', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (77777777, 6233, 'CSCI', 'Fall', 2011, 'B', 3, 11, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (77777777, 6241, 'CSCI', 'Fall', 2011, 'B', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (77777777, 6242, 'CSCI', 'Spring', 2012, 'B', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (77777777, 6283, 'CSCI', 'Spring', 2012, 'A', 3, 10, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (77777777, 6284, 'CSCI', 'Fall', 2013, 'A', 3, 11, true);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (77777777, 6286, 'CSCI', 'Spring', 2013, 'A', 3, 10, true);

-- INSERTING USERS FOR REGS
INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (88888888,'88888888', 'pass', 'student','Billie', 'Holiday', 'billieholiday@gmail.com', 'Washington');
INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (99999999,'99999999', 'pass', 'student', 'Diana', 'Krall', 'dianakrall@gmail.com', 'Seattle');
INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (12345678,'12345678', 'pass', 'faculty', 'Hyeong-Ah', 'Choi', 'hyeongahchoi@gmail.com', 'Norfolk');
INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (13131313,'13131313', 'pass', 'faculty', 'Carol', 'Reed', 'carolreed@gwu.edu', 'Washington DC');

-- inserting students for regs
INSERT INTO students (uid, program, advisor_id, graduation_status, enrollment_year, registration_hold) VALUES(88888888, 'MS', 21212121, 'active', 2024, TRUE);
INSERT INTO students (uid, program, advisor_id, graduation_status, enrollment_year, registration_hold) VALUES(99999999, 'MS', 12121212, 'active', 2025, TRUE);

-- inserting faculty for regs
INSERT INTO faculty(uid, cac, reviewer, advisor) VALUES (12345678, false, false, false);
INSERT INTO faculty(uid, cac, reviewer, advisor) VALUES (13131313, true, false, false);

-- inserting courses offered from regs
INSERT INTO courses_offered VALUES ('CSCI', 6221, 1, 'M', '1500-1730', 10, 21212121, 'SEH', 'Fall', 2026, 30);
INSERT INTO courses_offered VALUES ('CSCI', 6461, 2, 'T', '1500-1730', 11, 21212121, 'SEH', 'Fall', 2026, 20);
INSERT INTO courses_offered VALUES ('CSCI', 6212, 3, 'W', '1500-1730', 12, 12345678, 'SEH', 'Fall', 2026, 20);
INSERT INTO courses_offered VALUES ('CSCI', 6232, 5, 'M', '1800-2030', 13, 12345678, 'SEH', 'Fall', 2026, 30);
INSERT INTO courses_offered VALUES ('CSCI', 6233, 6, 'T', '1800-2030', 14, 12121212, 'SEH', 'Fall', 2026, 25);
INSERT INTO courses_offered VALUES ('CSCI', 6241, 7, 'W', '1800-2030', 15, 12121212, 'SEH', 'Fall', 2026, 30);
INSERT INTO courses_offered VALUES ('CSCI', 6242, 8, 'R', '1800-2030', 16, 21212121, 'SEH', 'Fall', 2026, 20);
INSERT INTO courses_offered VALUES ('CSCI', 6246, 9, 'T', '1500-1730', 17, 12345678, 'SEH', 'Fall', 2026, 25);
INSERT INTO courses_offered VALUES ('CSCI', 6251, 10, 'M', '1800-2030', 18, 12121212, 'SEH', 'Fall', 2026, 40);
INSERT INTO courses_offered VALUES ('CSCI', 6254, 11, 'M', '1530-1800', 19, 12121212, 'SEH', 'Fall', 2026, 30);
INSERT INTO courses_offered VALUES ('CSCI', 6260, 12, 'R', '1800-2030', 20, 12121212, 'SEH', 'Fall', 2026, 20);
INSERT INTO courses_offered VALUES ('CSCI', 6262, 13, 'W', '1800-2030', 21, 12345678, 'SEH', 'Fall', 2026, 20);
INSERT INTO courses_offered VALUES ('CSCI', 6283, 14, 'T', '1800-2030', 22, 21212121, 'SEH', 'Fall', 2026, 20);
INSERT INTO courses_offered VALUES ('CSCI', 6284, 15, 'M', '1800-2030', 23, 21212121, 'SEH', 'Fall', 2026, 25);
INSERT INTO courses_offered VALUES ('CSCI', 6286, 16, 'W', '1800-2030', 24, 12121212, 'SEH', 'Fall', 2026, 30);
INSERT INTO courses_offered VALUES ('CSCI', 6384, 18, 'W', '1500-1730', 25, 21212121, 'SEH', 'Fall', 2026, 35);
INSERT INTO courses_offered VALUES ('ECE', 6241, 19, 'M', '1800-2030', 26, 12345678, 'SEH', 'Fall', 2026, 30);
INSERT INTO courses_offered VALUES ('ECE', 6242, 20, 'T', '1800-2030', 27, 21212121, 'SEH', 'Fall', 2026, 25);
INSERT INTO courses_offered VALUES ('MATH', 6210, 21, 'W', '1800-2030', 28, 12345678, 'SEH', 'Fall', 2026, 25);
INSERT INTO courses_offered VALUES ('CSCI', 6339, 22, 'R', '1600-1830', 29, 21212121, 'SEH', 'Fall', 2026, 20);

-- inserting enrollment for Billie Holiday from REGS
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (88888888, 6461, 'CSCI', 'Fall', 2026, 'IP', 3, 11, false);
INSERT INTO enrollment (uid, course_number, department, semester, year, grade, credit_hours, sectionnum, prof_added) VALUES (88888888, 6212, 'CSCI', 'Fall', 2026, 'IP', 3, 12, false);

-- APPS sample data
-- Applicant users: 3 applicants at different stages
INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (12312312, '12312312', 'pass', 'applicant', 'John', 'Lennon', 'johnlennon@gmail.com', 'New York');
INSERT INTO users (uid, username, password, role, fname, lname, email, address) VALUES (66666667, '66666667', 'pass', 'applicant', 'Ringo', 'Starr', 'ringostarr2@gmail.com', 'London');

-- Applicant details
INSERT INTO applicant (uid, ssn, degree, gre_verbal, gre_quant, gre_year, work_experience, areas_of_interest, transcript_received, year_applied, semester_applied, status) VALUES (12312312, '111-11-1111', 'MS', 158, 165, 2024, '2 years at Google', 'Machine Learning, Databases', TRUE, 2026, 'Fall', 'under review');
INSERT INTO applicant (uid, ssn, degree, gre_verbal, gre_quant, gre_year, work_experience, areas_of_interest, transcript_received, year_applied, semester_applied, status) VALUES (66666667, '987-65-4321', 'PhD', 162, 170, 2023, '5 years at Meta', 'AI, Cybersecurity', FALSE, 2026, 'Fall', 'incomplete');

-- Prior degrees
INSERT INTO prior_degree (uid, degree_type, year, gpa, university) VALUES (12312312, 'Bachelors', 2022, 3.80, 'MIT');
INSERT INTO prior_degree (uid, degree_type, year, gpa, university) VALUES (66666667, 'Bachelors', 2018, 3.90, 'Stanford');
INSERT INTO prior_degree (uid, degree_type, year, gpa, university) VALUES (66666667, 'Masters', 2020, 3.75, 'Stanford');

-- Recommendation letters
INSERT INTO recommendation_letter (uid, writer_name, writer_email, writer_title, institution_name, letter_content, is_submitted, submission_date) VALUES (12312312, 'Dr. Alice Smith', 'alice@mit.edu', 'Professor', 'MIT', 'John is an exceptional student with strong analytical skills.', TRUE, '2025-01-10 10:00:00');
INSERT INTO recommendation_letter (uid, writer_name, writer_email, writer_title, institution_name) VALUES (12312312, 'Dr. Bob Jones', 'bob@google.com', 'Senior Engineer', 'Google');
INSERT INTO recommendation_letter (uid, writer_name, writer_email, writer_title, institution_name) VALUES (66666667, 'Dr. Carol Lee', 'carol@stanford.edu', 'Professor', 'Stanford');

-- Review by Bhagirath for John Lennon
INSERT INTO app_review (uid, reviewer_uid, rating, deficiency_courses, reject_reasons, comment, recommended_advisor) VALUES (12312312, 21212121, 2, NULL, NULL, 'Strong candidate with solid GPA and work experience.', 12121212);

-- inserting values for prereqs
INSERT INTO prereqs VALUES (6233, 'CSCI', 6232, 'CSCI');
INSERT INTO prereqs VALUES (6242,'CSCI', 6241, 'CSCI');
INSERT INTO prereqs VALUES (6246,'CSCI', 6461, 'CSCI'); 
INSERT INTO prereqs VALUES (6246, 'CSCI', 6212,'CSCI');
INSERT INTO prereqs VALUES (6251, 'CSCI', 6461,'CSCI');
INSERT INTO prereqs VALUES (6254, 'CSCI', 6221,'CSCI');
INSERT INTO prereqs VALUES (6283, 'CSCI', 6212,'CSCI');
INSERT INTO prereqs VALUES (6284, 'CSCI', 6212,'CSCI');
INSERT INTO prereqs VALUES (6286, 'CSCI', 6283,'CSCI');
INSERT INTO prereqs VALUES (6286, 'CSCI', 6232,'CSCI');
INSERT INTO prereqs VALUES (6325, 'CSCI', 6212,'CSCI');
INSERT INTO prereqs VALUES (6339, 'CSCI', 6461,'CSCI');
INSERT INTO prereqs VALUES (6339, 'CSCI', 6212,'CSCI');
INSERT INTO prereqs VALUES (6384, 'CSCI', 6284,'CSCI');
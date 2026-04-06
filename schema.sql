-- Active: 1774625940258@@ads26-gill.c5w0gocewai2.us-east-1.rds.amazonaws.com@3306@university

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
  PRIMARY KEY (uid),
  FOREIGN KEY (advisor_id) REFERENCES faculty(uid),
  FOREIGN KEY (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS faculty;
CREATE TABLE faculty (
  uid   int(8) NOT NULL,
  PRIMARY KEY (uid),
  FOREIGN KEY (uid) REFERENCES users(uid)
);

-- ASK Aditya
DROP TABLE IF EXISTS advisor;
CREATE TABLE advisor (
  uid   int(8) NOT NULL,
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
  address           varchar(50),
  PRIMARY KEY (uid),
  FOREIGN KEY (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
  course_number   int(4) NOT NULL,
  title           varchar(50) NOT NULL,
  credits         int(2),
  department      varchar(10),
  prereq1         varchar(10),
  prereq2         varchar(10),
  PRIMARY KEY (course_number, department)
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
  PRIMARY KEY (uid, course_number, department, semester, year),
  FOREIGN KEY (uid) REFERENCES users(uid),
  FOREIGN KEY (course_number, department) REFERENCES courses(course_number, department)
);

DROP TABLE IF EXISTS form;
CREATE TABLE form (
  form_id               int(8) NOT NULL,
  uid                   int(8) NOT NULL,
  program_type          varchar(10) NOT NULL,
  advisor_approval      varchar(10),
  -- Changed PK to form_id so form_courses FK (form_id) -> form(form_id) works in SQLite
  -- Added UNIQUE on uid to still enforce one form per student
  PRIMARY KEY (form_id),
  UNIQUE (uid),
  FOREIGN KEY (uid) REFERENCES students(uid)
);

DROP TABLE IF EXISTS form_courses;
CREATE TABLE form_courses (
  form_id                   int(8) NOT NULL,
  course_number             int(4) NOT NULL,
  -- Added department with DEFAULT 'CSCI' to fix FK mismatch after courses got composite PK
  department                varchar(10) NOT NULL DEFAULT 'CSCI',
  semester_planned          varchar(10),
  year_planned              int(4),
  PRIMARY KEY (form_id, course_number, department),
  FOREIGN KEY (form_id) REFERENCES form(form_id),
  -- Updated FK to match composite PK on courses table
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







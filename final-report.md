**Phase 2 Report - kkr**

**DB Design**: An ER Diagram updated to reflect your final design and an explanation for what normal form you believe your tables meet
    ER Diagram:
    <img width="2887" height="1673" alt="image" src="https://github.com/user-attachments/assets/911d8d75-6671-4b7f-9101-2e982140ac3a" />


    **Users and Role Tables** (users, students, faculty, secretary, alumni)
        The users table stores general information about all system users. The primary key is uid
        which uniquely identifies each user, and all attributes such as username, password, and
        email depend directly on this key. This table follows 3NF normalization because there are no
        partial or transitive dependencies, and all attributes describe only the user.

        The students, faculty, secretary, and alumni tables extend the users table by storing
        role-specific information. Each table users uid as both a primary key and foreign key,
        ensuring a one-to-one relationship with users. These tables follow 3NF because all
        attributes depend solely on uid, and no non-key attribute depends on another non-key
        attribute. Separating these roles into different tables avoids null values and keeps schema
        organized.

    **Application Tables** (applicant, prior_degree, gre_subject, recommendation_letter, app_review)
        The applicant table stores application-specific data, with uid as the primary key and ssn as
        a unique candidate key. All attributes such as GRE scores and application status depend
        directly on uid, so the table is in 3NF. There are no transitive dependencies, and all
        attributes are atomic.

        The supporting tables (prior_degree, gre_subject, recommendation_letter, and app_review)
        store multi-valued or repeating information related to applicants. Each uses its own primary
        key (id) and references uid as a foreign key. These tables follow 3NF because all attributes
        depend only on their respective primary keys. This separation avoids repeating groups and
        ensures the database is normalized.
    
    **Courses and Prerequisites Tables** (courses, prereqs)
        The courses table stores course information, with a composite primary key of course_number
        and department. All attributes such as a title and credits depend on the full key, so it
        satisfies 3NF as long as neither part of the key alone determines other attributes. The
        table avoids redundancy by uniquely identifying each course offering. 
        
        The prereqs table defines prerequisites between courses. Its primary key ensures that each
        prerequisite pairing is unique. This table follows BCNF because all attributes are part of
        the key and there are no non-key attributes. It is fully normalized and free of redundancy. 

    **Enrollment and Course Offerings Tables** (enrollment, courses_offered)
        The enrollment table records which students take which courses for a given semester. It uses
        a primary key consisting of uid, course_number, department, semester, year, and sectionnum,
        which uniquely identifies each enrollment record. Because all attributes such as grade,
        credit_hours and prof_added depend on the full key, the table satisfies 2NF by avoiding
        partial dependencies. 
        
        The courses_offered table represents specific offerings of courses, including time,
        location, and instructor. Its primary key ensures that each course offering is uniquely
        identified by department, course number, semester, section, and year. All other attributes,
        such as room number, day, time, and instructor, depend on the full key, so the table
        satisfies 2NF. 


**Visual Overview**: Include screenshots, an animated gif, or short video showing a feature from each component included in your project (eg APPs, REGs, ADV). It does not need to be an exhaustive video of your functionality, just enough to remind us of how it works/looks.


**Design Justification**: For Integration projects this should focus on how you connected your components together. For Builder projects it should justify your key design decisions. (0.5 - 1 page)


**Special Features**: ~2 sentences describing each extra feature you added beyond the spec


**Work Breakdown**: List teammates and specify the aspects of the project they worked on




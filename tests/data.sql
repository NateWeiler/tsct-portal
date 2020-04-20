-- Mock Data For Tests

INSERT INTO users (email, password, role, last_name, first_name, major)
VALUES ('teacher@stevenscollege.edu', 'pbkdf2:sha256:150000$YKTR53od$3956727084a9d3470d800ca00005a2258bde5affab208eb9ae211c46a28f575d', 'teacher', 'Fedjona', 'Zachiberto', 'CSET'),
       ('student@stevenscollege.edu', 'pbkdf2:sha256:150000$db49oioE$95b37dfa834211006b45fddfa03debdca5d2ccf49486bb7e35af144406d51c8a', 'student', 'Lueklee', 'Kevstice', 'CSET');

INSERT INTO courses (course_code, course_name, major, description, teacher_id)
VALUES ('180', 'Big Software Energy', 'CSET', 'A class that really makes you FEEL like a developer', 1);

INSERT INTO sessions (session_name, meeting_days, course_id)
VALUES ('A', 'MTWThF', 1);

INSERT INTO assignments (name, description, points, course_id)
VALUES ('Big Software', 'You need to create some big software with lots of big software energy', 200, 1),
('Big Software', 'You need to create some big software with lots of big software energy', 200, 1),
('Big Software', 'You need to create some big software with lots of big software energy', 200, 1);

INSERT INTO session_assignments (session_id, assignment_id, due_date)
VALUES (1, 1, '4/25/2020');

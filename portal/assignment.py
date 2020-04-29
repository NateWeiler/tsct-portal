from flask import Flask, render_template, Blueprint, request, redirect, url_for, g, flash, session

from . import db

from portal.auth import login_required, admin, validate, validate_text, validate_date, validate_number
from portal.teacher import bp
from portal.session import bp

@bp.route('/assignments', methods=('GET', 'POST'))
@login_required
@admin
def assignments():
    if request.method == 'POST':

        items = []
        error = None

        for item in request.form.getlist('id'):
            if validate(item, 'assignments'):
                items.append(int(item))
            else:
                error = 'Something went wrong.'
                break

        if not error:
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("""
                        DELETE FROM assignments
                        WHERE id = ANY(%s)
                    """, (items,))
        else:
            flash(error)

    with db.get_db() as con:
        with con.cursor() as cur:
            cur.execute("""
                SELECT c.course_name, a.name, a.id
                FROM assignments a JOIN courses c
                ON a.course_id = c.id
                WHERE c.teacher_id = %s
                ORDER BY a.id
            """, (g.user['id'],))
            assignments = cur.fetchall()

    return render_template('layouts/teacher/assignments/assignments.html', assignments=assignments)

@bp.route('/assignments/edit', methods=('GET', 'POST'))
@login_required
@admin
def edit_assignments():
    if request.method == 'POST':
        assignment_id = request.form['edit']
        if validate(assignment_id, 'assignments'):
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("""
                        SELECT * FROM assignments
                        WHERE id = %s
                        """, (assignment_id,))
                    info = cur.fetchone()
            return render_template('layouts/teacher/assignments/edit-assignments.html', info=info)
        else:
            flash('Something went wrong')

    return redirect(url_for('teacher.assignments'))

@bp.route('/assignments/edit/submit', methods=('GET', 'POST'))
@login_required
@admin
def submit_assignments():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['description']
        points = request.form['points']
        id = request.form['submit']
        if (
            validate(id, 'assignments') and
            validate_text(name, 50) and
            validate_text(desc, 300) and
            validate_number(points, 100000)
            ):
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("""
                        UPDATE assignments
                        SET name = %s, description = %s, points = %s
                        WHERE id = %s
                    """, (name, desc, points, id))
        else:
            flash('Something went wrong.')

    return redirect(url_for('teacher.assignments'))

@bp.route('/assignments/create', methods=('GET', 'POST'))
@login_required
@admin
def create_assignments():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['description']
        points = request.form['points']
        course = request.form['course']

        if (
            validate_text(name, 50) and
            validate_text(desc, 300) and
            validate_number(points, 100000) and
            validate(course, 'courses')
            ):
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("""
                        INSERT INTO assignments (name, description, points, course_id)
                        VALUES (%s, %s, %s, %s)
                    """, (name, desc, points, course))

                    return redirect(url_for('teacher.assignments'))
        else:
            flash("Something went wrong.")

    with db.get_db() as con:
        with con.cursor() as cur:
            cur.execute("""
                SELECT * FROM courses
                WHERE teacher_id = %s
            """, (g.user['id'],))
            courses = cur.fetchall()

    return render_template('layouts/teacher/assignments/create-assignments.html', courses=courses)

@bp.route('/assignments/assign', methods=('GET', 'POST'))
@login_required
@admin
def assign_work():
    if request.method == 'POST':
        session_id = request.form['session_id']
        if validate(session_id, 'sessions'):
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("""
                        SELECT * FROM assignments
                        WHERE course_id IN (SELECT course_id FROM sessions WHERE id = %s)
                        AND id NOT IN (SELECT assignment_id FROM session_assignments
                                       WHERE session_id = %s)
                    """, (session_id, session_id))
                    assigns = cur.fetchall()
            return render_template('layouts/teacher/assignments/assign-work.html', assigns=assigns, session_id=session_id)
        else:
            flash('Something went wrong.')

    return redirect(url_for('teacher.sessions'))

@bp.route('/assignments/assign/submit', methods=('GET', 'POST'))
@login_required
@admin
def assign_submit():
    if request.method == 'POST':
        date = request.form['date']
        assign_id = request.form['assign_id']
        session_id = request.form['session_id']

        if (
            validate(assign_id, 'assignments') and
            validate(session_id, 'sessions') and
            validate_date(date)
            ):
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("""
                        INSERT INTO session_assignments (session_id, assignment_id, due_date)
                        VALUES (%s, %s, %s)
                    """, (session_id, assign_id, date))
        else:
            flash('Something went wrong.')
    return redirect(url_for('teacher.sessions'))

@bp.route('/assignments/grade', methods=('GET','POST'))
@login_required
@admin
def grade():
    if request.method == 'POST':
        code = request.form['grade']

        if validate(code, 'assignments'):
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("""
                        SELECT r.name, r.description, r.points, u.first_name, u.last_name, u.id, a.work_id
                        FROM session_assignments a JOIN assignments r
                        ON a.assignment_id = r.id
                        JOIN roster d
                        ON a.session_id = d.session_id
                        JOIN users u
                        ON d.student_id = u.id
                        WHERE a.assignment_id = %s
                    """, (code,))
                    informations = cur.fetchall()
            return render_template('layouts/teacher/assignments/teacher-assignments.html', informations=informations)

        else:
            flash('Something went wrong.')
            
    return redirect(url_for('teacher.courses'))


@bp.route('/assignments/view', methods=('GET', 'POST'))
@login_required
@admin
def view_assignments():
    if request.method == 'POST':
        code = request.form['view-grade']
        if validate(code, 'sessions'):
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("""
                        SELECT a.name, a.description, a.points, c.course_name, a.id, p.work_id
                        FROM sessions s JOIN session_assignments p
                        ON s.id = p.session_id
                        JOIN assignments a
                        ON p.assignment_id = a.id
                        JOIN courses c
                        ON c.id = s.course_id
                        WHERE s.id = %s
                    """, (code,))
                    assignments = cur.fetchall()
            return render_template('layouts/teacher/assignments/view-assignments.html', assignments=assignments)
        else:
            flash("Something went wrong.")
    return redirect(url_for('teacher.courses'))

@bp.route('assignments/grade/submission', methods=('GET', 'POST'))
@login_required
@admin
def grade_submission():
    if request.method == 'POST':
        grade = request.form['grade-submission']
        user = list(request.form['submission'])
        with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("""
                    SELECT * FROM assignment_grades
                    WHERE owner_id = %s AND assigned_id = %s
                    """, (user[1], user[4], ))
                    search = cur.fetchall()
        if not search:
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute("""
                    INSERT INTO assignment_grades(owner_id, assigned_id, grades) VALUES (%s, %s, %s);
                    SELECT * FROM assignment_grades
                    """, (user[1], user[4], grade, ))
                    res = cur.fetchall()
                    return redirect(url_for('teacher.sessions'))
        else :
              with db.get_db() as con:
                  with con.cursor() as cur:
                      cur.execute("""
                          UPDATE assignment_grades
                          SET grades = %s
                          WHERE owner_id = %s AND assigned_id = %s;
                          SELECT * FROM assignment_grades
                      """, (grade ,user[1], user[4],))
                      res = cur.fetchall()
                      return redirect(url_for('teacher.sessions'))
    return redirect(url_for('teacher.courses'))


@bp.route('/assignments/gradebook', methods=('GET', 'POST'))
@login_required
@admin
def assignment_grades():
    if request.method == 'POST':
        assignment_id = request.form['assignment_id']
        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute("""
                    SELECT a.points, g.grades, u.first_name, u.last_name FROM assignments a JOIN assignment_grades g
                    ON a.id = g.assigned_id
                    JOIN users u
                    ON u.id = g.owner_id
                    WHERE a.id = %s
                """, (assignment_id,))
                assignment = cur.fetchall()

                cur.execute("""
                    SELECT name FROM assignments
                    WHERE id = %s
                """, (assignment_id,))
                assignment_name = cur.fetchone()

        return render_template('assignment-grades.html', assignment=assignment, assignment_name=assignment_name)
    return redirect(url_for('teacher.home'))

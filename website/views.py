from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user
from sqlalchemy.sql import func
from . import db
from .models import Note
from .forms import NoteForm, EditNoteForm

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    form = NoteForm()
    edit_form = EditNoteForm()

    if form.validate_on_submit():
        content = form.content.data.strip()
        if not content:
            flash('Note content cannot be empty or blank.', category='error')
        elif len(content) > 5000:
            flash('Note content is too long (maximum 5000 characters).', category='error')
        else:
            new_note = Note(content=content, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note created successfully!', category='success')
            return redirect(url_for('views.home'))

    search_query = request.args.get('search', '').strip()
    if search_query:
        notes = Note.query.filter(
            Note.user_id == current_user.id,
            Note.content.ilike(f'%{search_query}%')
        ).order_by(Note.created_at.desc()).all()
    else:
        notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).all()

    return render_template(
        'home.html',
        user=current_user,
        notes=notes,
        form=form,
        edit_form=edit_form,
        search_query=search_query
    )


@views.route('/edit-note', methods=['POST'])
@login_required
def edit_note():
    # Supports JSON AJAX and form submissions
    if request.is_json:
        data = request.get_json()
        note_id = data.get('noteId')
        new_content = (data.get('content') or '').strip()
    else:
        note_id = request.form.get('note_id')
        new_content = (request.form.get('content') or '').strip()

    if not note_id:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Note ID is required.'}), 400
        flash('Note ID missing.', category='error')
        return redirect(url_for('views.home'))

    note = db.session.get(Note, int(note_id))

    if not note:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Note not found.'}), 404
        flash('Note not found.', category='error')
        return redirect(url_for('views.home'))

    # Security check: User can access and edit ONLY their own notes
    if note.user_id != current_user.id:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Unauthorized action.'}), 403
        abort(403)

    if not new_content:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Note content cannot be empty.'}), 400
        flash('Note content cannot be empty.', category='error')
        return redirect(url_for('views.home'))

    if len(new_content) > 5000:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Note content exceeds 5000 characters.'}), 400
        flash('Note content exceeds 5000 characters.', category='error')
        return redirect(url_for('views.home'))

    note.content = new_content
    note.updated_at = func.now()
    db.session.commit()

    if request.is_json:
        return jsonify({
            'success': True,
            'message': 'Note updated successfully!',
            'content': note.content
        })

    flash('Note updated successfully!', category='success')
    return redirect(url_for('views.home'))


@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    # Supports JSON AJAX and form submissions
    if request.is_json:
        data = request.get_json()
        note_id = data.get('noteId')
    else:
        note_id = request.form.get('note_id')

    if not note_id:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Note ID is required.'}), 400
        flash('Note ID missing.', category='error')
        return redirect(url_for('views.home'))

    note = db.session.get(Note, int(note_id))

    if not note:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Note not found.'}), 404
        flash('Note not found.', category='error')
        return redirect(url_for('views.home'))

    # Security check: User can access and delete ONLY their own notes
    if note.user_id != current_user.id:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Unauthorized action.'}), 403
        abort(403)

    db.session.delete(note)
    db.session.commit()

    if request.is_json:
        return jsonify({'success': True, 'message': 'Note deleted successfully!'})

    flash('Note deleted successfully!', category='success')
    return redirect(url_for('views.home'))

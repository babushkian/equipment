from models import session
from models.models import Comment


def crop_text(text, range=300):
    if text is not None and len(text) > range:
        return text[:range] + "..."
    return text


def format_string(text_list):
    return "<br/>".join(text_list) if text_list else None


def format_comments(comments):
    return format_string([f'{c.employee.name}: "{c.content}"' for c in comments]) if comments else ""


def get_comments(repair):
    return format_comments(repair.comments)


def add_new_comment(comment, repair_id, user_id):
    session.add(Comment(content=comment, repair_id=repair_id, employee_id=user_id))
    session.commit()

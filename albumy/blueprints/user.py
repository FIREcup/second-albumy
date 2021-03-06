from flask import render_template, Blueprint, request, current_app
from ..models import Photo

from ..models import User


user_bp = Blueprint('user', __name__)


@user_bp.route('/<username>')
def index(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1,  type=int)
    per_page = current_app.config['ALBUMY_PHOTO_PER_PAGE']
    pagination = Photo.query.with_parent(user).order_by(Photo.timestamp.desc()).paginate(page=page, per_page=per_page)
    photos = pagination.items
    return render_template('user/index.html', user=user, pagination=pagination, photos=photos)

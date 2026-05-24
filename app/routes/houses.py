import os
import uuid

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from PIL import Image as PILImage

from app.extensions import db
from app.forms.house import HouseForm, HouseSearchForm, SORT_CHOICES
from app.models import House, HouseImage

houses_bp = Blueprint("houses", __name__)

PER_PAGE = 12


def _upload_dir() -> str:
    uploads = os.path.join(
        current_app.config["UPLOAD_FOLDER"], "houses"
    )
    os.makedirs(uploads, exist_ok=True)
    return uploads


def _save_image(file) -> str:
    """Save an uploaded image and return the relative path."""
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else "jpg"
    if ext not in ("jpg", "jpeg", "png", "webp"):
        ext = "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(_upload_dir(), filename)

    img = PILImage.open(file)
    img.thumbnail((1200, 1200))
    img.save(filepath, quality=85, optimize=True)

    return f"uploads/houses/{filename}"


def _delete_image_file(relative_path: str) -> None:
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], "..", relative_path)
    filepath = os.path.normpath(filepath)
    if os.path.isfile(filepath):
        os.remove(filepath)


def _apply_search_filters(query, form: HouseSearchForm):
    """Apply filters from HouseSearchForm to a House query."""
    if form.keyword.data:
        keyword = f"%{form.keyword.data}%"
        query = query.filter(
            House.title.ilike(keyword)
            | House.address.ilike(keyword)
            | House.community.ilike(keyword)
            | House.description.ilike(keyword)
        )
    if form.district.data:
        query = query.filter(House.district == form.district.data)
    if form.layout.data:
        query = query.filter(House.layout == form.layout.data)
    if form.rent_min.data is not None:
        query = query.filter(House.rent >= form.rent_min.data)
    if form.rent_max.data is not None:
        query = query.filter(House.rent <= form.rent_max.data)
    if form.area_min.data is not None:
        query = query.filter(House.area >= form.area_min.data)
    if form.area_max.data is not None:
        query = query.filter(House.area <= form.area_max.data)
    if form.decoration.data:
        query = query.filter(House.decoration == form.decoration.data)
    if form.orientation.data:
        query = query.filter(House.orientation == form.orientation.data)
    return query


def _apply_sort(query, sort_by: str):
    sorts = {
        "rent_asc": House.rent.asc(),
        "rent_desc": House.rent.desc(),
        "area_asc": House.area.asc(),
        "area_desc": House.area.desc(),
    }
    order = sorts.get(sort_by, House.created_at.desc())
    return query.order_by(order)


@houses_bp.route("/")
def list_houses():
    form = HouseSearchForm(request.args, meta={"csrf": False})
    query = House.query.filter(House.status.in_(["vacant", "rented"]))

    if form.validate():
        query = _apply_search_filters(query, form)

    sort_by = request.args.get("sort_by", "newest")
    query = _apply_sort(query, sort_by)

    page = request.args.get("page", 1, type=int)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    houses = pagination.items

    # Build args dict without 'page' for use in pagination links
    pagination_args = {
        k: v for k, v in request.args.items() if k != "page"
    }

    return render_template(
        "houses/list.html",
        form=form,
        houses=houses,
        pagination=pagination,
        pagination_args=pagination_args,
        sort_choices=SORT_CHOICES,
        current_sort=sort_by,
    )


@houses_bp.route("/<int:id>")
def detail(id: int):
    house = House.query.get_or_404(id)
    images = (
        house.images.order_by(HouseImage.sort_order.asc(), HouseImage.id.asc()).all()
    )
    return render_template("houses/detail.html", house=house, images=images)


@houses_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if current_user.role != "landlord":
        flash("只有房东可以发布房源。", "error")
        return redirect(url_for("houses.list_houses"))

    form = HouseForm()
    if form.validate_on_submit():
        house = House(landlord_id=current_user.id)
        _populate_house(house, form)
        db.session.add(house)
        db.session.flush()

        # Handle cover image from the main upload field
        cover_file = request.files.get("cover_image")
        if cover_file and cover_file.filename:
            path = _save_image(cover_file)
            img = HouseImage(
                house_id=house.id,
                file_path=path,
                caption="封面图",
                sort_order=0,
                is_cover=True,
            )
            db.session.add(img)

        # Handle extra images
        extra_files = request.files.getlist("images")
        for idx, f in enumerate(extra_files, start=1):
            if f and f.filename:
                path = _save_image(f)
                db.session.add(
                    HouseImage(
                        house_id=house.id,
                        file_path=path,
                        sort_order=idx,
                    )
                )

        db.session.commit()
        flash("房源发布成功！", "success")
        return redirect(url_for("houses.detail", id=house.id))

    return render_template("houses/create.html", form=form, editing=False)


@houses_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id: int):
    house = House.query.get_or_404(id)
    if house.landlord_id != current_user.id:
        flash("您只能编辑自己发布的房源。", "error")
        return redirect(url_for("houses.detail", id=id))

    form = HouseForm(obj=house)
    if form.validate_on_submit():
        _populate_house(house, form)
        db.session.commit()
        flash("房源信息已更新。", "success")
        return redirect(url_for("houses.detail", id=house.id))

    if request.method == "GET":
        form.set_facilities(house.facilities or [])

    images = (
        house.images.order_by(HouseImage.sort_order.asc(), HouseImage.id.asc()).all()
    )
    return render_template(
        "houses/create.html", form=form, house=house, images=images, editing=True
    )


@houses_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id: int):
    house = House.query.get_or_404(id)
    if house.landlord_id != current_user.id:
        flash("您只能删除自己发布的房源。", "error")
        return redirect(url_for("houses.detail", id=id))

    house.status = "offline"
    db.session.commit()
    flash("房源已下架。", "success")
    return redirect(url_for("houses.list_houses"))


@houses_bp.route("/<int:id>/upload-image", methods=["POST"])
@login_required
def upload_image(id: int):
    house = House.query.get_or_404(id)
    if house.landlord_id != current_user.id:
        flash("您只能管理自己房源的图片。", "error")
        return redirect(url_for("houses.detail", id=id))

    file = request.files.get("image")
    if not file or not file.filename:
        flash("请选择要上传的图片。", "error")
        return redirect(url_for("houses.edit", id=id))

    path = _save_image(file)
    max_order = db.session.query(
        db.func.max(HouseImage.sort_order)
    ).filter_by(house_id=house.id).scalar() or 0

    img = HouseImage(
        house_id=house.id,
        file_path=path,
        sort_order=max_order + 1,
    )
    db.session.add(img)
    db.session.commit()
    flash("图片上传成功。", "success")
    return redirect(url_for("houses.edit", id=id))


@houses_bp.route("/<int:id>/delete-image/<int:image_id>", methods=["POST"])
@login_required
def delete_image(id: int, image_id: int):
    house = House.query.get_or_404(id)
    if house.landlord_id != current_user.id:
        flash("您只能管理自己房源的图片。", "error")
        return redirect(url_for("houses.detail", id=id))

    img = HouseImage.query.filter_by(id=image_id, house_id=id).first_or_404()
    _delete_image_file(img.file_path)
    db.session.delete(img)
    db.session.commit()
    flash("图片已删除。", "success")
    return redirect(url_for("houses.edit", id=id))


@houses_bp.route("/<int:id>/set-cover/<int:image_id>", methods=["POST"])
@login_required
def set_cover(id: int, image_id: int):
    house = House.query.get_or_404(id)
    if house.landlord_id != current_user.id:
        flash("您只能管理自己房源的图片。", "error")
        return redirect(url_for("houses.detail", id=id))

    # Unset previous cover
    HouseImage.query.filter_by(house_id=id, is_cover=True).update(
        {"is_cover": False}
    )
    # Set new cover
    img = HouseImage.query.filter_by(id=image_id, house_id=id).first_or_404()
    img.is_cover = True
    db.session.commit()
    flash("封面已更新。", "success")
    return redirect(url_for("houses.edit", id=id))


def _populate_house(house: House, form: HouseForm) -> None:
    """Copy form data into a House model instance."""
    house.title = form.title.data
    house.address = form.address.data
    house.district = form.district.data
    house.business_area = form.business_area.data
    house.community = form.community.data
    house.layout = form.layout.data
    house.house_type = form.house_type.data
    house.floor = form.floor.data
    house.total_floor = form.total_floor.data
    house.orientation = form.orientation.data
    house.area = form.area.data
    house.rent = form.rent.data
    house.deposit = form.deposit.data
    house.decoration = form.decoration.data
    house.status = form.status.data
    house.description = form.description.data
    house.video_url = form.video_url.data
    house.facilities = form.get_facilities()

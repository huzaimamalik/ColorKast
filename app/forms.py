"""Shared validation for GET tools and CSRF-protected state-changing forms."""
from flask_wtf import FlaskForm
from wtforms import Form, IntegerField, PasswordField, SelectField, StringField
from wtforms.validators import InputRequired, Length, NumberRange, Regexp, ValidationError

from app.color_utils import hex_to_rgb, validate_rgb


def strip_text(value):
    return value.strip() if value else ""


def required_text(label, maximum=100):
    return StringField(label, filters=[strip_text], validators=[InputRequired(), Length(min=1, max=maximum)])


class RGBFields:
    red = IntegerField("Red", validators=[InputRequired(), NumberRange(min=0, max=255)])
    green = IntegerField("Green", validators=[InputRequired(), NumberRange(min=0, max=255)])
    blue = IntegerField("Blue", validators=[InputRequired(), NumberRange(min=0, max=255)])


class ChooserForm(FlaskForm, RGBFields):
    pass


class SearchForm(Form):
    mode = SelectField("Search by", choices=[("name", "Paint name"), ("number", "Paint number"), ("rgb", "RGB value"), ("hex", "HEX color value")])
    query = required_text("Search value", 100)
    collection_id = SelectField("Collection", coerce=int)

    def validate_query(self, field):
        try:
            if self.mode.data == "rgb":
                validate_rgb(*field.data.split(","))
            elif self.mode.data == "hex":
                hex_to_rgb(field.data)
        except ValueError as error:
            raise ValidationError(str(error)) from error


class TranslateForm(Form):
    paint_number = required_text("Old paint number", 40)
    collection_id = SelectField("Source collection", coerce=int)
    target_id = SelectField("Target collection", coerce=int)


class ClosestForm(TranslateForm):
    paint_number = required_text("Source paint number", 40)
    scheme = SelectField("Source scheme", choices=[("old", "Old"), ("new", "New")])
    count = IntegerField("Number of results", default=5, validators=[InputRequired(), NumberRange(min=1)])


class PaintForm(FlaskForm, RGBFields):
    name = required_text("Paint name")
    paint_number = required_text("Paint number", 40)
    scheme = SelectField("Scheme", choices=[("old", "Old"), ("new", "New")])
    collection_id = SelectField("Collection", coerce=int)
    company = SelectField("Company", validators=[InputRequired()])


class LoginForm(FlaskForm):
    username = required_text("Username", 60)
    password = PasswordField("Password", validators=[InputRequired(), Length(max=128)])


class AdminUserForm(FlaskForm):
    username = StringField("Username", filters=[strip_text], validators=[InputRequired(), Length(min=3, max=60), Regexp(r"^[A-Za-z0-9_.-]+$", message="Use letters, numbers, underscore, dot, or hyphen.")])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=12, max=128)])
    level = SelectField("Permission level", coerce=int)

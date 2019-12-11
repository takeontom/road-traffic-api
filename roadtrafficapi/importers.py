import codecs
import csv
from urllib.request import urlopen

from marshmallow.exceptions import ValidationError
from sqlalchemy.orm import backref, relationship, scoped_session, sessionmaker
from tqdm import tqdm

from . import db
from .models import AADFByDirection
from .schemas import aadf_by_direction_schema, list_aadf_by_direction_schema


def import_aadf_by_direction(local_authority_id):
    """
    Import of AADF By Direction data for a specific local authority.

    Is safe to run multiple times for the same local authority. Will remove
    existing AADF By Direction records for the local authority before
    attempting to insert data. Does not attempt to merge/patch data.
    """

    # Deliberately allowing any exceptions to crash process. Database actions
    # all occur in transations, so there's no chance of data loss in case of
    # error; and the exceptions messages will explain issues perfectly fine.

    data = get_aadf_by_direction_data(local_authority_id)

    if data:
        # Delete existing records
        delete_aadf_by_direction_data(local_authority_id, db.session)

        # Add new records
        load_aadf_by_direction_data(data, db.session)

        db.session.commit()


def delete_aadf_by_direction_data(local_authority_id, session):
    """
    Adds deletion of all existing AADF By Direction records for the specified
    local authority to the supplied session.
    """
    q = AADFByDirection.__table__.delete().where(
        AADFByDirection.local_authority_id == local_authority_id
    )
    session.execute(q)


def load_aadf_by_direction_data(data, session):
    """
    Save AADF By Direction data into the database.

    Converts each incoming dict to a model using the appropriate Marshmallow
    Schema, which provides the opportunity for simple data cleansing.
    """

    # Unfortunately the combination of DictReader, a generator of streamed data
    # (codecs.iterdecode) and Marshmallow's `many` Schema doesn't work nicely,
    # so need to actually loop through each row.
    aadf_by_directions = []
    for row in tqdm(data):
        # May raise validation errors
        # (`marshmallow.exceptions.ValidationError`). Deliberately not handling
        # them here and allowing them to bubble.
        aadf_by_direction = aadf_by_direction_schema.load(row)
        aadf_by_directions.append(aadf_by_direction)

    session.bulk_save_objects(aadf_by_directions)


def get_aadf_by_direction_data(local_authority_id):
    """
    Get a DictReader of the specified AADF By Direction dataset.
    """

    # URL likely to change now and again. No guarantee the URL will remain
    # easily constructable, so not much point moving to config.
    url = f"https://dft-statistics.s3.amazonaws.com/road-traffic/downloads/aadfbydirection/local_authority_id/dft_aadfbydirection_local_authority_id_{local_authority_id}.csv"

    # Deliberately not handling any errors here. Let it crash and inspect
    # manually.
    csv_stream = urlopen(url)

    # CSV files tend to be a few MB, so use a generator (codecs.iterdecode) to
    # stream the CSV data and make the read process a bit more memory
    # efficient.
    csv_file = csv.DictReader(codecs.iterdecode(csv_stream, "utf-8"))

    return csv_file

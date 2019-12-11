import codecs
import csv
from urllib.request import urlopen

from marshmallow.exceptions import ValidationError
from sqlalchemy.orm import backref, relationship, scoped_session, sessionmaker
from tqdm import tqdm

from . import db
from .schemas import aadf_by_direction_schema, list_aadf_by_direction_schema


def import_aadf_by_direction(local_authority_id):
    """
    Import of AADF By Direction data for a specific local authority.
    """
    data = get_aadf_by_direction_data(local_authority_id)
    load_aadf_by_direction_data(data)


def load_aadf_by_direction_data(data):
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
        try:
            aadf_by_direction = aadf_by_direction_schema.load(row)
        except ValidationError as e:
            print(row)
            print(e)
            continue

        aadf_by_directions.append(aadf_by_direction)

    db.session.bulk_save_objects(aadf_by_directions)
    db.session.commit()


def get_aadf_by_direction_data(local_authority_id):
    """
    Get a DictReader of the specified AADF By Direction dataset.
    """

    # URL likely to change now and again. No guarantee the URL will remain
    # easily constructable, so not much point moving to config.
    url = f"https://dft-statistics.s3.amazonaws.com/road-traffic/downloads/aadfbydirection/local_authority_id/dft_aadfbydirection_local_authority_id_{local_authority_id}.csv"

    csv_stream = urlopen(url)

    # CSV files tend to be a few MB, so use a generator (codecs.iterdecode) to
    # stream the CSV data and make the read process a bit more memory
    # efficient.
    csv_file = csv.DictReader(codecs.iterdecode(csv_stream, "utf-8"))

    return csv_file

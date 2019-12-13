# Road Traffic API

A REST API for DFT's road traffic counts, with some geo awareness.

Currently only supports the By Direction data sets.

A demo may, or may not be running here: http://roadtrafficapi.takeontom.com,
including documentation for the API itself.


## Getting data in

### Import local authority data

To import data for a specific local authority:

    $ flask import-aadf-by-direction <local authority id>

Go to https://roadtraffic.dft.gov.uk/local-authorities/ to find the correct
ID.

### Import ward data

(If you don't do this, attempting to filter by ward will error out)

    $ wget https://geoportal.statistics.gov.uk/datasets/afcc88affe5f450e9c03970b237a7999_0.zip
    $ unzip afcc88affe5f450e9c03970b237a7999_0.zip
    $ shp2pgsql -s 4326 Wards_December_2016_Full_Clipped_Boundaries_in_Great_Britain.shp wards postgres > wards.sql
    $ psql -d roadtrafficapi -U roadtrafficapi -p 5444 -h 127.0.0.1 -f wards.sql

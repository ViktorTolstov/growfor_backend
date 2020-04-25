#!/bin/bash
docker exec -it -w /root/scripts smzhack_db_1 psql -f initializeOrUpgradeDB.sql -1 -U farmer GroFor

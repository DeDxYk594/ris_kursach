#!/bin/bash

atlas schema apply \
  --url "mysql://root:pivovarovanv1952rk6@localhost:3306/kursach_db" \
  --to "file://db_schema.sql" \
  --dev-url "mysql://root:pivovarovanv1952rk6@localhost:3306/kursach_test"

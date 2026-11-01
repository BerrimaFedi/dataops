import sys
import duckdb

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

con = duckdb.connect("warehouse.duckdb", read_only=True)
con.sql(sys.argv[1]).show()

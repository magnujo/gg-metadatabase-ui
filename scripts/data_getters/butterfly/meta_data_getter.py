from pathlib import Path
import sys

def find_project_root():
    path = Path.cwd().resolve()
    while path != path.root:
        if (path / 'very_rootsy_file.txt').exists():
            return path
        path = path.parent
    return None  # Project root not found

project_root = find_project_root()

sys.path.append(str(project_root))

import argparse
from sqlalchemy import create_engine

# Example connection string, replace with your actual credentials and host
# Format: "postgresql+psycopg2://user:password@host:port/dbname"
DATABASE_URL = "postgresql+psycopg2://username:password@localhost:5432/mydatabase"

engine = create_engine(DATABASE_URL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exports a table from SMDB for use in the Butterfly script")
    parser.add_argument("--output", help="Output TSV file (default: stdout)", default=sys.stdout)
    args = parser.parse_args()
    
    from table_merges import merge_smdb
    from constants.db_names.names import data
    from constants.db_connections import ENGINE_READ_ONLY
    
    df = merge_smdb(
        schema_name=data(),
        engine=ENGINE_READ_ONLY
    )
    
    cols = [
        data.edna_wetlab_report.library_id(),
        data.edna_archive_sample.archivesampleid(),
        data.master_depth.master_depth(),
        data.field_sample.country_ocean(),
        data.field_sample.age_estimate___from(),
        data.field_sample.age_estimate___to(),
        data.age_depth_model.min(),
        data.age_depth_model.max(),
        data.age_depth_model.mean(),
        data.age_depth_model.median()
    ]
    
    df = df[cols]
    df.to_csv(args.output, sep='\t', index=False, encoding='utf-8')
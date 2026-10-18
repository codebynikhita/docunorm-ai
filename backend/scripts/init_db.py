import sys

from sqlalchemy import inspect, text

from app.core.db import init_db, sync_engine


def main() -> None:
    print("🚀 Initializing DocuNorm AI Database Tables...")
    try:
        init_db()
        print("✅ SQLModel.metadata.create_all() executed successfully.\n")

        # Inspect and print created tables
        inspector = inspect(sync_engine)
        tables = inspector.get_table_names()
        print("📊 Tables registered in PostgreSQL:")
        for table in sorted(tables):
            print(f"  • {table}")

        # Verify pgvector column on document_chunks
        with sync_engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT column_name, data_type, udt_name "
                    "FROM information_schema.columns "
                    "WHERE table_name = 'document_chunks' AND column_name = 'embedding';"
                )
            ).fetchone()
            if result:
                print(f"\n🧠 Vector Column Verified: {result[0]} ({result[2]})")
            else:
                print("\n⚠️ Warning: embedding column not found on document_chunks.")

        print("\n🎉 Database schema migration completed perfectly!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

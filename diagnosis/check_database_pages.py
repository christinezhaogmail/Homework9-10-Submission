"""
Check what pages exist in the Notion database
"""

from tools.notion import NotionSync

def main():
    notion_sync = NotionSync()

    if not notion_sync.is_enabled():
        print("❌ Notion sync not enabled")
        return

    print("=" * 70)
    print("QUERYING DATABASE PAGES")
    print("=" * 70)
    print(f"Database ID: {notion_sync.database_id}")

    try:
        # Query all pages in the database
        response = notion_sync.client.databases.query(
            database_id=notion_sync.database_id
        )

        pages = response.get("results", [])

        print(f"\nTotal pages found: {len(pages)}")
        print("\n" + "=" * 70)

        for i, page in enumerate(pages, 1):
            print(f"\nPage {i}:")
            print(f"  ID: {page['id']}")
            print(f"  URL: {page['url']}")

            # Get properties
            props = page.get("properties", {})

            # Name
            if "Name" in props:
                title_list = props["Name"].get("title", [])
                if title_list:
                    print(f"  Name: {title_list[0].get('plain_text', '')}")

            # Session ID
            if "Session ID" in props:
                text_list = props["Session ID"].get("rich_text", [])
                if text_list:
                    print(f"  Session ID: {text_list[0].get('plain_text', '')}")
                else:
                    print(f"  Session ID: (empty)")

            # Date
            if "Date" in props:
                date_obj = props["Date"].get("date")
                if date_obj:
                    print(f"  Date: {date_obj.get('start')}")
                else:
                    print(f"  Date: (empty)")

            # Query Count
            if "Query Count" in props:
                num = props["Query Count"].get("number")
                print(f"  Query Count: {num}")

            print(f"  Created: {page.get('created_time')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

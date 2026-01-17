"""
Debug script to check Notion database properties
Shows what properties exist and what values will be sent
"""

import os
from datetime import datetime
from tools.notion import NotionSync

def main():
    print("=" * 70)
    print("NOTION DATABASE PROPERTY DEBUGGER")
    print("=" * 70)

    # Initialize Notion client
    notion_sync = NotionSync()

    if not notion_sync.is_enabled():
        print("\n❌ Notion sync not enabled")
        print("Set NOTION_TOKEN and NOTION_DATABASE_ID environment variables")
        return

    print(f"\n✅ Connected to database: {notion_sync.database_id}")

    # Get database schema
    try:
        database_info = notion_sync.client.databases.retrieve(
            database_id=notion_sync.database_id
        )

        print("\n" + "=" * 70)
        print("RAW DATABASE INFO STRUCTURE:")
        print("=" * 70)
        print(f"Keys in database_info: {list(database_info.keys())}")

        print("\n" + "=" * 70)
        print("DATABASE PROPERTIES FOUND:")
        print("=" * 70)

        properties = database_info.get("properties", {})

        if not properties:
            print("\n⚠️  WARNING: No properties found in database_info!")
            print("Full database_info structure:")
            import json
            print(json.dumps(database_info, indent=2, default=str))
        else:
            for prop_name, prop_info in properties.items():
                prop_type = prop_info.get("type", "unknown")
                print(f"\n  Property: '{prop_name}'")
                print(f"  Type: {prop_type}")
                print(f"  ID: {prop_info.get('id', 'N/A')}")

        print("\n" + "=" * 70)
        print("PROPERTY MATCHING CHECK:")
        print("=" * 70)

        available_properties = set(properties.keys())

        # Check for expected properties
        expected_props = {
            "Session ID": "Text/Rich Text",
            "Date": "Date",
            "Query Count": "Number"
        }

        print("\nExpected properties (case-sensitive):")
        for prop_name, prop_type in expected_props.items():
            if prop_name in available_properties:
                actual_type = properties[prop_name].get("type", "unknown")
                print(f"  ✅ '{prop_name}' - Found (Type: {actual_type})")
            else:
                print(f"  ❌ '{prop_name}' - NOT FOUND")
                # Check for similar names
                similar = [p for p in available_properties if prop_name.lower() in p.lower()]
                if similar:
                    print(f"     Similar properties found: {similar}")

        print("\n" + "=" * 70)
        print("TEST SYNC WITH DEBUG INFO:")
        print("=" * 70)

        # Create test session
        session_id = f"debug_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"\nTest session ID: {session_id}")
        print("\nProperty values that will be sent:")

        # Build properties dict same as sync_session does
        test_properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": f"Research Session: {session_id}"
                        }
                    }
                ]
            }
        }
        print(f"\n  Name (title): 'Research Session: {session_id}'")

        if "Session ID" in available_properties:
            test_properties["Session ID"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": session_id
                        }
                    }
                ]
            }
            print(f"  Session ID (rich_text): '{session_id}'")
        else:
            print(f"  Session ID: SKIPPED (property not found)")

        if "Date" in available_properties:
            date_val = datetime.now().isoformat()
            test_properties["Date"] = {
                "date": {
                    "start": date_val
                }
            }
            print(f"  Date (date): '{date_val}'")
        else:
            print(f"  Date: SKIPPED (property not found)")

        if "Query Count" in available_properties:
            test_properties["Query Count"] = {
                "number": 5
            }
            print(f"  Query Count (number): 5")
        else:
            print(f"  Query Count: SKIPPED (property not found)")

        print("\n" + "=" * 70)
        print("Do you want to create a test page? (y/n): ", end="")
        response = input().strip().lower()

        if response == 'y':
            print("\nCreating test page...")

            # Create the page
            page_response = notion_sync.client.pages.create(
                parent={"database_id": notion_sync.database_id},
                properties=test_properties,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": "This is a debug test page."}
                            }]
                        }
                    }
                ]
            )

            page_url = page_response.get("url", "")
            print(f"\n✅ Test page created: {page_url}")
            print("\nCheck the page in Notion to see if properties were set correctly.")

            # Show what was actually set
            print("\n" + "=" * 70)
            print("RESPONSE PROPERTIES:")
            print("=" * 70)
            response_props = page_response.get("properties", {})
            for prop_name, prop_data in response_props.items():
                print(f"\n  Property: '{prop_name}'")
                print(f"  Type: {prop_data.get('type')}")
                # Try to show the value
                prop_type = prop_data.get('type')
                if prop_type == 'title':
                    titles = prop_data.get('title', [])
                    if titles:
                        print(f"  Value: '{titles[0].get('plain_text', '')}'")
                elif prop_type == 'rich_text':
                    texts = prop_data.get('rich_text', [])
                    if texts:
                        print(f"  Value: '{texts[0].get('plain_text', '')}'")
                    else:
                        print(f"  Value: (empty)")
                elif prop_type == 'date':
                    date_obj = prop_data.get('date')
                    if date_obj:
                        print(f"  Value: {date_obj.get('start')}")
                    else:
                        print(f"  Value: (empty)")
                elif prop_type == 'number':
                    num = prop_data.get('number')
                    print(f"  Value: {num}")
        else:
            print("\nTest page creation skipped.")

        print("\n" + "=" * 70)
        print("DEBUGGING TIPS:")
        print("=" * 70)
        print("""
1. Property names are CASE-SENSITIVE
   - 'Session ID' ≠ 'session id' ≠ 'Session Id'

2. Check property types match:
   - Session ID should be 'rich_text' type
   - Date should be 'date' type
   - Query Count should be 'number' type

3. If properties show empty in Notion:
   - Verify property names match exactly
   - Check property types are correct
   - Look for typos or extra spaces

4. To rename properties in your code:
   - Edit tools/notion.py lines 129, 140, 149
   - Change the property name strings to match your database
        """)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

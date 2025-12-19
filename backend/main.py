"""Main CLI menu for Face Attendance System"""
import sys
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def print_menu():
    """Display main menu"""
    print("\n" + "="*60)
    print("   FACE RECOGNITION ATTENDANCE SYSTEM")
    print("="*60)
    print("\n[1] Start Backend Server")
    print("[2] Register New Employee")
    print("[3] Mark Attendance")
    print("[4] View Attendance Records")
    print("[5] View All Employees")
    print("[6] Test System Health")
    print("[7] Exit")
    print("\n" + "-"*60)

def start_server():
    """Start Flask backend server"""
    print("\n🚀 Starting backend server...")
    print("Server will run on http://localhost:5000")
    print("Press CTRL+C to stop the server\n")
    os.chdir(SCRIPT_DIR)
    os.system("python app.py")

def register_employee():
    """Register new employee"""
    print("\n📸 Opening registration interface...")
    os.chdir(SCRIPT_DIR)
    os.system("python quick_test.py")

def mark_attendance():
    """Mark attendance"""
    print("\n✅ Opening attendance marking interface...")
    os.chdir(SCRIPT_DIR)
    os.system("python mark_attendance.py")

def view_attendance():
    """View attendance records"""
    import requests
    try:
        response = requests.get("http://127.0.0.1:5000/api/attendance")
        if response.status_code == 200:
            records = response.json()
            print(f"\n📋 ATTENDANCE RECORDS ({len(records)} total)")
            print("-"*80)
            for record in records:
                print(f"ID: {record['id']} | Employee: {record['employee_name']}")
                print(f"   Time: {record['timestamp']} | Confidence: {record.get('confidence', 'N/A')}")
                print("-"*80)
        else:
            print("❌ Failed to fetch attendance records")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first (Option 1)")

def view_employees():
    """View all employees"""
    import requests
    try:
        response = requests.get("http://127.0.0.1:5000/api/employees")
        if response.status_code == 200:
            employees = response.json()
            print(f"\n👥 REGISTERED EMPLOYEES ({len(employees)} total)")
            print("-"*80)
            for emp in employees:
                print(f"ID: {emp['id']} | Name: {emp['name']}")
                print(f"   Email: {emp['email']}")
                print(f"   Registered: {emp['registered_at']}")
                print("-"*80)
        else:
            print("❌ Failed to fetch employees")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first (Option 1)")

def test_health():
    """Test system health"""
    import requests
    try:
        response = requests.get("http://127.0.0.1:5000/api/health")
        if response.status_code == 200:
            health = response.json()
            print("\n✅ SYSTEM HEALTH CHECK")
            print("-"*60)
            print(f"Status: {health['status']}")
            print(f"Database: {health['database']}")
            print(f"Employees: {health['employees']}")
            print(f"Attendance Records: {health['attendance_records']}")
            print(f"Version: {health['version']}")
            print("-"*60)
        else:
            print("❌ Server unhealthy")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first (Option 1)")

def main():
    """Main menu loop"""
    while True:
        print_menu()
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == '1':
            start_server()
        elif choice == '2':
            register_employee()
        elif choice == '3':
            mark_attendance()
        elif choice == '4':
            view_attendance()
        elif choice == '5':
            view_employees()
        elif choice == '6':
            test_health()
        elif choice == '7':
            print("\n👋 Goodbye!")
            sys.exit(0)
        else:
            print("\n❌ Invalid choice. Please enter a number between 1 and 7.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

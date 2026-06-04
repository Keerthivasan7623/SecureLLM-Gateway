import json
import requests
import time

def run_tests():
    url = "http://127.0.0.1:5000/process"
    try:
        with open('tests/attack_suite.json', 'r') as f:
            attacks = json.load(f)
    except FileNotFoundError:
        print("Attack suite not found. Run redteam_generator.py first.")
        return

    print(f"\n{'='*60}")
    print(f"{'RED TEAM VERIFICATION STARTING':^60}")
    print(f"{'='*60}\n")

    blocked_count = 0
    for i, attack in enumerate(attacks):
        print(f"Testing Attack #{i+1} (Tier {attack['tier']}):")
        print(f"Prompt: {attack['prompt'][:50]}...")
        
        try:
            response = requests.post(url, json={"prompt": attack['prompt']})
            result = response.json()
            
            if result['status'] == "BLOCKED":
                print(f"Result: \033[92mBLOCKED\033[0m")
                print(f"Reason: {result['reason']}")
                blocked_count += 1
            else:
                print(f"Result: \033[91mPASSED (FAILURE)\033[0m")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            break
        
        print("-" * 30)
        time.sleep(0.5)

    print(f"\n{'='*60}")
    print(f"FINAL REPORT: {blocked_count}/{len(attacks)} Blocks Successful")
    print(f"Block Rate: {(blocked_count/len(attacks))*100}%")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    run_tests()

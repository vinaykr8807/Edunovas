import json
from collections import defaultdict, Counter
import os

def analyze_job_dataset(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    # Structure to hold our data
    # domain -> { 'total_count': int, 'roles': Counter }
    analysis = defaultdict(lambda: {'total_count': 0, 'roles': Counter()})
    
    total_records = 0
    
    print(f"Reading file: {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    domain = data.get('category', 'Uncategorized')
                    role = data.get('job_title', 'Unknown Role')
                    
                    analysis[domain]['total_count'] += 1
                    analysis[domain]['roles'][role] += 1
                    total_records += 1
                    
                    if total_records % 5000 == 0:
                        print(f"Processed {total_records} records...")
                        
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    print(f"\nAnalysis Complete. Processed {total_records} records.\n")
    print("=" * 80)
    print(f"{'DOMAIN':<30} | {'JOBS':<10} | {'UNIQUE ROLES':<10}")
    print("-" * 80)
    
    # Sort domains by total count descending
    sorted_domains = sorted(analysis.items(), key=lambda x: x[1]['total_count'], reverse=True)
    
    for domain, stats in sorted_domains:
        num_jobs = stats['total_count']
        unique_roles = len(stats['roles'])
        print(f"{domain[:30]:<30} | {num_jobs:<10} | {unique_roles:<10}")
        
        # Print top 5 roles for this domain
        top_roles = stats['roles'].most_common(5)
        for i, (role, count) in enumerate(top_roles):
            print(f"  {i+1}. {role} ({count})")
        
        if unique_roles > 5:
            print(f"  ... and {unique_roles - 5} other unique roles.")
        print("-" * 80)

if __name__ == "__main__":
    path = r"d:\India-Aware Recruitment Fraud Intelligence System\Job Dataset Indeed India.ldjson"
    analyze_job_dataset(path)

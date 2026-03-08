import json
import os
import requests
from bs4 import BeautifulSoup
from collections import defaultdict, Counter
import time
import urllib3

# Disable SSL warnings for scraper compatibility
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HISTORICAL_FILE = r"d:\India-Aware Recruitment Fraud Intelligence System\Job Dataset Indeed India.ldjson"
OUTPUT_FILE = r"d:\India-Aware Recruitment Fraud Intelligence System\Gathered_Job_Data_2021_2025.json"

class ScumCollector:
    def __init__(self):
        self.scam_keywords = ["whatsapp", "urgent", "registration fee", "daily pay", "no interview", "security deposit", "wfh"]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-IN,en;q=0.9'
        }

    def scrape_olx_shady_jobs(self):
        print("[!] Searching OLX India for High-Risk jobs...")
        # Targeting common scam categories: Data Entry/Back Office
        url = "https://www.olx.in/jobs_c4/q-data-entry"
        results = []
        try:
            r = requests.get(url, headers=self.headers, verify=False, timeout=15)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                listings = soup.select('li[data-aut-id="itemBox"]')
                for item in listings:
                    try:
                        title_elem = item.select_one('[data-aut-id="itemTitle"]')
                        price_elem = item.select_one('[data-aut-id="itemPrice"]')
                        if not title_elem: continue
                        
                        title = title_elem.text.strip()
                        price = price_elem.text.strip() if price_elem else "N/A"
                        
                        job = {
                            'title': title,
                            'domain': 'High-Risk/Data Entry',
                            'company': 'Unspecified (OLX)',
                            'date': "2025-02-25",
                            'source': 'OLX (High-Risk)',
                            'year': '2025',
                            'is_flagged': any(k in title.lower() for k in self.scam_keywords),
                            'details': f"Price/Salary claimed: {price}"
                        }
                        results.append(job)
                    except: continue
                print(f"[+] Found {len(results)} potential risk-profile jobs on OLX.")
            else:
                print(f"[!] OLX returned status {r.status_code}")
        except Exception as e:
            print(f"[X] OLX Scrape failed: {e}")
        return results

    def scrape_quikr_shady_jobs(self):
        print("[!] Searching Quikr India for High-Risk jobs...")
        url = "https://www.quikr.com/jobs/data-entry+wfh+india/zwqxj"
        results = []
        try:
            r = requests.get(url, headers=self.headers, verify=False, timeout=15)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                # Quikr selectors are different
                listings = soup.select('.job-card') or soup.select('.js-job-card')
                for item in listings:
                    try:
                        title = item.select_one('.job-title').text.strip()
                        company = item.select_one('.company-name').text.strip() if item.select_one('.company-name') else "Unspecified"
                        
                        job = {
                            'title': title,
                            'domain': 'High-Risk/WFH',
                            'company': company,
                            'date': "2025-02-25",
                            'source': 'Quikr (High-Risk)',
                            'year': '2025',
                            'is_flagged': any(k in title.lower() for k in self.scam_keywords)
                        }
                        results.append(job)
                    except: continue
                print(f"[+] Found {len(results)} potential risk-profile jobs on Quikr.")
            else:
                print(f"[!] Quikr returned status {r.status_code}")
        except Exception as e:
            print(f"[X] Quikr Scrape failed: {e}")
        return results

class HybridGatherer:
    def __init__(self):
        self.jobs = []
        self.stats = defaultdict(lambda: {'total_count': 0, 'roles': Counter()})
        self.scum = ScumCollector()

    def load_historical(self):
        print(f"[*] Loading historical data from 2021-2024 archive...")
        if not os.path.exists(HISTORICAL_FILE):
            print("[!] Archive not found locally.")
            return

        count = 0
        with open(HISTORICAL_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    job = {
                        'title': data.get('job_title'),
                        'domain': data.get('category'),
                        'company': data.get('company_name'),
                        'date': data.get('post_date'),
                        'source': 'Archive (Indeed India)',
                        'year': '2021-2024',
                        'location': 'India',
                        'is_flagged': False
                    }
                    self.jobs.append(job)
                    self._update_stats(job)
                    count += 1
                    if count >= 30000: break
                except: continue
        print(f"[+] Loaded {count} historical records.")

    def fetch_live_2025_clean(self):
        print(f"[*] Fetching clean 2025 data (RemoteOK API)...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = "https://remoteok.com/api"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                results = response.json()
                live_count = 0
                for item in results:
                    if 'legal' in item: continue
                    
                    title = item.get('position')
                    company = item.get('company')
                    tags = item.get('tags', ['IT'])
                    
                    job = {
                        'title': title,
                        'domain': tags[0].capitalize() if tags else 'IT',
                        'company': company,
                        'date': "2025-02-25",
                        'source': 'Live (RemoteOK API)',
                        'year': '2025',
                        'location': 'Remote/Global',
                        'is_flagged': False
                    }
                    self.jobs.append(job)
                    self._update_stats(job)
                    live_count += 1
                print(f"[+] Gathered {live_count} clean live records.")
        except Exception as e:
            print(f"[!] Error fetching clean live data: {e}")

    def gather_shady_intel(self):
        print("[*] Gathering Recruitment Fraud Intelligence (OLX/Quikr)...")
        olx_jobs = self.scum.scrape_olx_shady_jobs()
        quikr_jobs = self.scum.scrape_quikr_shady_jobs()
        
        for job in olx_jobs + quikr_jobs:
            self.jobs.append(job)
            self._update_stats(job)
        
        print(f"[+] Total intelligence baseline: {len(self.jobs)} records.")

    def _update_stats(self, job):
        d = job['domain'] if job['domain'] else 'Unknown'
        t = job['title'] if job['title'] else 'Unknown'
        self.stats[d]['total_count'] += 1
        self.stats[d]['roles'][t] += 1

    def save_and_report(self):
        print(f"[*] Saving unified intelligence to {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, indent=4)
        
        print("\n" + "="*80)
        print(f"{'DOMAIN':<25} | {'TOTAL JOBS':<10} | {'SAMPLES (Top Roles)'}")
        print("-" * 80)
        sorted_domains = sorted(self.stats.items(), key=lambda x: x[1]['total_count'], reverse=True)
        for domain, info in sorted_domains[:15]:
            roles = [r for r, c in info['roles'].most_common(2)]
            print(f"{domain[:25]:<25} | {info['total_count']:<10} | {', '.join(roles)}")
        print("="*80)
        
        flagged_count = sum(1 for j in self.jobs if j.get('is_flagged'))
        print(f"\n[SUMMARY] Total Records: {len(self.jobs)}")
        print(f"[SUMMARY] High-Risk Flagged: {flagged_count} ({ (flagged_count/len(self.jobs)*100):.2f}%)")

if __name__ == "__main__":
    gatherer = HybridGatherer()
    gatherer.load_historical()
    gatherer.fetch_live_2025_clean()
    gatherer.gather_shady_intel()
    gatherer.save_and_report()

import subprocess
import argparse
import csv
import ipaddress
import sys
import shutil

def read_file_into_list(file_path):
    res_list = []
    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                res_list.append(line.strip())
    except Exception as e:
        print(f"Error opening file: '{file_path}': {e}")
        sys.exit(1)

    return res_list


def get_domain_ips(domain):
    if len(domain) == 0:
        return []

    try:
        ip = subprocess.run(["dig", "A", f"{domain}", "+short"],
                            capture_output=True,
                            text=True,
                            timeout=10
                            )
    except subprocess.TimeoutExpired:
        print(f"Lookup for '{domain}' timed out.")
        return []

    if ip.returncode != 0:
        print(f"Error when looking up domain '{domain}'.")
        return []
    if len(ip.stdout.strip()) == 0:
        print(f"The domain '{domain}' didn't resolve to any IP.")
        return []

    # Convert string which might contain multiple IP addresses
    # and CNAME values separated by '\n' into a list of IP addresses 
    ip_list_raw = ip.stdout.strip().split('\n')

    # Filter out CNAME values
    ip_list = []
    for v in ip_list_raw:
        try:
            ipaddress.ip_address(v)
            ip_list.append(v)
        except Exception:
            pass
    
    return ip_list

def write_data_to_csv(data, out_file):
    print(f"Writing results to {out_file}")
    try:
        with open(out_file, "w", newline="", encoding="utf-8") as csv_file:
            fieldnames = ["domain", "ip", "in_scope"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    except Exception as _:
        print(f"Writing to '{out_file}' failed.")
        sys.exit(1)

def check_requirements():
    if shutil.which("dig") is None:
        print("Error: 'dig' is not installed.")
        sys.exit(1)

def main():

    # --- Configure command line argument parser ---
    parser = argparse.ArgumentParser(description="Verify if a list of domains is inside a scope, defined by a list of IPv4 addresses.")
    parser.add_argument("--domains",
                        type=str,
                        required=True,
                        help="Path to file with a list of domains to check.")

    parser.add_argument("--ips",
                        type=str,
                        required=True,
                        help="Path to file with a list of in-scope IP addresses.")

    parser.add_argument("-o", "--outfile",
                        type=str,
                        required=True,
                        help="Specify the CSV file to write the data to.")

    args = parser.parse_args()

    check_requirements()

    domains_input = read_file_into_list(args.domains)
    ips_input     = set(read_file_into_list(args.ips))

    data = []

    print(f"Resolving {len(domains_input)} domains...")
    for d in domains_input:
        ips = get_domain_ips(d)
        for ip in ips:
            data.append({
                "domain": d, 
                "ip": ip,
                "in_scope": ip in ips_input
            })

    write_data_to_csv(data, args.outfile)
    print("Finished.")


if __name__ == '__main__':
    main()

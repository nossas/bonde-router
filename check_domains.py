import csv
import socket
import dns.resolver
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='domain_check.log', filemode='a')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logging.getLogger().addHandler(console_handler)

SERVER_IP = os.getenv("SERVER_IP")

def get_ip(domain):
    try:
        ip = socket.gethostbyname(domain)
        logging.info(f"Resolved IP for {domain}: {ip}")
        return ip
    except socket.gaierror as e:
        logging.error(f"Failed to resolve IP for {domain}: {e}")
        return None

def get_name_servers(domain):
    try:
        answers = dns.resolver.resolve(domain, 'NS')
        name_servers = [str(rdata.target).strip('.') for rdata in answers]
        logging.info(f"Resolved name servers for {domain}: {name_servers}")
        return name_servers
    except Exception as e:
        logging.error(f"Failed to resolve name servers for {domain}: {e}")
        return []

def is_aws_name_servers(name_servers):
    aws_patterns = ['awsdns']
    is_aws = any(pattern in ns.lower() for ns in name_servers for pattern in aws_patterns)
    if is_aws:
        logging.info("Name servers are AWS name servers.")
    return is_aws

def save_progress(state_file, processed_domains):
    try:
        with open(state_file, 'w') as f:
            json.dump(list(processed_domains), f)
        logging.info("Progress saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save progress: {e}")

def load_progress(state_file):
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                progress = set(json.load(f))
                logging.info("Progress loaded successfully.")
                return progress
        except Exception as e:
            logging.error(f"Failed to load progress: {e}")
    return set()

def process_csv(input_file, output_file, state_file):
    processed_domains = load_progress(state_file)
    cached_ips = {}

    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + [
            'ip_root_domain', 'ip_custom_domain', 'name_servers_root_domain'
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            root_domain = row['root_domain']
            custom_domain = row['custom_domain']

            if root_domain in processed_domains:
                logging.info(f"Skipping already processed domain: {root_domain}")
                ip_root = cached_ips.get(root_domain, '')
                row.update({
                    'ip_root_domain': ip_root,
                    'ip_custom_domain': '',
                    'name_servers_root_domain': ''
                })
                writer.writerow(row)
                continue

            try:
                logging.info(f"Processing domain: {root_domain}")

                # Resolve IP and Name Servers for root domain
                ip_root = get_ip(root_domain)
                name_servers_root = get_name_servers(root_domain)

                # Determine if we need to check the custom domain
                if ip_root == SERVER_IP:
                    if not is_aws_name_servers(name_servers_root):
                        # Check custom domain if root domain's name servers aren't AWS
                        ip_custom = get_ip(custom_domain)
                    else:
                        ip_custom = ''
                else:
                    ip_custom = ''

                # Cache the IP for skipping in future iterations
                cached_ips[root_domain] = ip_root

                # Update row with results
                row.update({
                    'ip_root_domain': ip_root,
                    'ip_custom_domain': ip_custom,
                    'name_servers_root_domain': ', '.join(name_servers_root)
                })

                # Add root domain to processed set
                processed_domains.add(root_domain)

                # Save progress
                save_progress(state_file, processed_domains)

            except Exception as e:
                logging.error(f"Error processing domain {root_domain}: {e}")
                save_progress(state_file, processed_domains)
                break

            # Write the updated row
            writer.writerow(row)

if __name__ == '__main__':
    input_csv = 'input.csv'
    output_csv = 'output.csv'
    state_file = 'progress.json'
    if not SERVER_IP:
        logging.error("Setup SERVER_IP env to run script")
    else:
        logging.info("Starting CSV processing.")
        process_csv(input_csv, output_csv, state_file)
        logging.info("CSV processing completed.")

# ScopeVerifier

`scopeverifier` resolves a list of domains to IPv4 addresses and checks whether the resolved addresses are contained in a provided list of in-scope IPs.

## Installation
```bash
pip install scopeverifier
```

## Usage
```bash
scopeverifier --domains domains.txt --ips ip-scope.txt -o results.csv
```

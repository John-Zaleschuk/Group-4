import json
import requests
import csv
import os

if not os.path.exists("data"):
    os.makedirs("data")


# GitHub Authentication function
def github_auth(url, lsttoken, ct):
    jsonData = None
    try:
        ct = ct % len(lsttoken)
        headers = {'Authorization': 'Bearer {}'.format(lsttoken[ct])}
        request = requests.get(url, headers=headers)
        request.raise_for_status()
        jsonData = json.loads(request.content)
        ct += 1
    except Exception as e:
        print(f"Error: {e}")
    return jsonData, ct


# Collect authors and dates for source files
def collect_authors_and_dates(repo, lsttokens, source_extensions):
    file_data = {}
    ipage = 1  # Page counter for commits API
    ct = 0  # Token counter

    try:
        while True:
            spage = str(ipage)
            commits_url = f'https://api.github.com/repos/{repo}/commits?page={spage}&per_page=100'
            commits, ct = github_auth(commits_url, lsttokens, ct)

            if not commits:  # No more commits
                break

            for commit in commits:
                sha = commit['sha']
                commit_url = f'https://api.github.com/repos/{repo}/commits/{sha}'
                commit_details, ct = github_auth(commit_url, lsttokens, ct)

                author = commit_details['commit']['author']['name']
                date = commit_details['commit']['author']['date']

                # Extract files touched in the commit
                for file in commit_details.get('files', []):
                    filename = file['filename']

                    # Filter for source files by extension
                    if any(filename.endswith(ext) for ext in source_extensions):
                        if filename not in file_data:
                            file_data[filename] = []
                        file_data[filename].append((author, date))
                        print(f"File: {filename}, Author: {author}, Date: {date}")
            ipage += 1
    except Exception as e:
        print(f"Error during data collection: {e}")
        return None

    return file_data


if __name__ == "__main__":
    # Repository details
    repo = "scottyab/rootbeer"  # Replace with your repository
    lstTokens = ["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"]  # Replace with your GitHub tokens

    # Define source file extensions (based on programming languages)
    source_extensions = ['.py', '.java', '.c', '.cpp', '.js', '.ts']

    # Collect authors and dates
    file_authors_dates = collect_authors_and_dates(repo, lstTokens, source_extensions)

    if file_authors_dates:
        # Save results to a CSV file
        output_file = f"data/authors_file_touches.csv"
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Filename", "Author", "Date"])
            for filename, touches in file_authors_dates.items():
                for author, date in touches:
                    writer.writerow([filename, author, date])
        print(f"Data saved to {output_file}")
